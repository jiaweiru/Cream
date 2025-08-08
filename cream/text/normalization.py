"""Text normalization functionality."""

from pathlib import Path
import re
import json

from cream.core.config import config
from cream.core.exceptions import InvalidFormatError, AudioProcessingError


class TextNormalizer:
    """Text normalization processor."""
    
    def __init__(self):
        # Common normalization patterns
        self.patterns = {
            "whitespace": {
                "multiple_spaces": (r'\s+', ' '),
                "leading_trailing": (r'^\s+|\s+$', ''),
                "empty_lines": (r'\n\s*\n', '\n')
            },
            "punctuation": {
                "normalize_quotes": (r'[""''„"‚'']', '"'),
                "normalize_dashes": (r'[–—]', '-'),
                "normalize_ellipsis": (r'\.{3,}', '...'),
                "remove_extra_punctuation": (r'([.!?]){2,}', r'\1')
            },
            "encoding": {
                "normalize_unicode": (r'[^\x00-\x7F]+', ''),  # Remove non-ASCII
                "smart_quotes": (r'[''`]', "'"),
                "smart_double_quotes": (r'["""]', '"')
            },
            "formatting": {
                "remove_html_tags": (r'<[^>]+>', ''),
                "normalize_newlines": (r'\r\n|\r', '\n'),
                "remove_urls": (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ''),
                "remove_email": (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '')
            }
        }
    
    def apply_normalization(self, text: str, method: str = "basic") -> str:
        """Apply normalization to text based on method."""
        normalized_text = text
        
        if method == "basic":
            # Basic normalization: whitespace and common issues
            for pattern, replacement in self.patterns["whitespace"].values():
                normalized_text = re.sub(pattern, replacement, normalized_text)
            
            for pattern, replacement in self.patterns["punctuation"].values():
                normalized_text = re.sub(pattern, replacement, normalized_text)
        
        elif method == "aggressive":
            # Aggressive normalization: everything
            for category in self.patterns.values():
                for pattern, replacement in category.values():
                    normalized_text = re.sub(pattern, replacement, normalized_text)
        
        elif method == "whitespace_only":
            # Only whitespace normalization
            for pattern, replacement in self.patterns["whitespace"].values():
                normalized_text = re.sub(pattern, replacement, normalized_text)
        
        elif method == "unicode":
            # Unicode and encoding normalization
            for pattern, replacement in self.patterns["encoding"].values():
                normalized_text = re.sub(pattern, replacement, normalized_text)
        
        elif method == "web":
            # Web content normalization (HTML, URLs, etc.)
            for pattern, replacement in self.patterns["formatting"].values():
                normalized_text = re.sub(pattern, replacement, normalized_text)
                
            # Also apply basic normalization
            for pattern, replacement in self.patterns["whitespace"].values():
                normalized_text = re.sub(pattern, replacement, normalized_text)
        
        else:
            raise AudioProcessingError(f"Unknown normalization method: {method}")
        
        return normalized_text.strip()
    
    def normalize_file(self, input_file: Path, output_file: Path, 
                      method: str = "basic", overwrite: bool = False) -> bool:
        """Normalize text in a file."""
        if not config.is_text_file(input_file):
            raise InvalidFormatError(f"Unsupported text format: {input_file.suffix}")
        
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        if output_file.exists() and not overwrite:
            return False
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if input_file.suffix.lower() == ".json":
                # Handle JSON files
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                def normalize_json_value(value):
                    if isinstance(value, str):
                        return self.apply_normalization(value, method)
                    elif isinstance(value, list):
                        return [normalize_json_value(item) for item in value]
                    elif isinstance(value, dict):
                        return {k: normalize_json_value(v) for k, v in value.items()}
                    else:
                        return value
                
                normalized_data = normalize_json_value(data)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(normalized_data, f, indent=2, ensure_ascii=False)
            
            elif input_file.suffix.lower() == ".csv":
                # Handle CSV files
                import csv
                with open(input_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                
                normalized_rows = []
                for row in rows:
                    normalized_row = [self.apply_normalization(cell, method) for cell in row]
                    normalized_rows.append(normalized_row)
                
                with open(output_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(normalized_rows)
            
            else:
                # Handle plain text files
                with open(input_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                normalized_content = self.apply_normalization(content, method)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(normalized_content)
            
            return True
            
        except Exception as e:
            raise AudioProcessingError(f"Failed to normalize text file: {str(e)}")
    
    def normalize_directory(self, input_dir: Path, output_dir: Path, 
                           method: str = "basic", pattern: str = "*.txt",
                           overwrite: bool = False) -> list[Path]:
        """Normalize all text files in directory."""
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        text_files = list(input_dir.glob(pattern))
        if not text_files:
            raise AudioProcessingError(f"No text files found in {input_dir} matching pattern {pattern}")
        
        normalized_files = []
        
        for text_file in text_files:
            try:
                relative_path = text_file.relative_to(input_dir)
                output_file = output_dir / relative_path
                
                if self.normalize_file(text_file, output_file, method, overwrite):
                    normalized_files.append(output_file)
                    
            except Exception as e:
                print(f"Failed to normalize {text_file}: {str(e)}")
                continue
        
        return normalized_files
    
    def normalize_text_list(self, texts: list[str], method: str = "basic") -> list[str]:
        """Normalize a list of text strings."""
        return [self.apply_normalization(text, method) for text in texts]
    
    def get_normalization_stats(self, original_text: str, normalized_text: str) -> dict[str, dict[str, int]]:
        """Get statistics about the normalization process."""
        original_lines = original_text.split('\n')
        normalized_lines = normalized_text.split('\n')
        
        stats = {
            "original": {
                "characters": len(original_text),
                "lines": len(original_lines),
                "words": len(original_text.split()),
                "whitespace_chars": len(re.findall(r'\s', original_text))
            },
            "normalized": {
                "characters": len(normalized_text),
                "lines": len(normalized_lines),
                "words": len(normalized_text.split()),
                "whitespace_chars": len(re.findall(r'\s', normalized_text))
            }
        }
        
        stats["changes"] = {
            "characters_removed": stats["original"]["characters"] - stats["normalized"]["characters"],
            "lines_removed": stats["original"]["lines"] - stats["normalized"]["lines"],
            "words_changed": stats["original"]["words"] - stats["normalized"]["words"],
            "whitespace_reduced": stats["original"]["whitespace_chars"] - stats["normalized"]["whitespace_chars"]
        }
        
        return stats
    
    def preview_normalization(self, text: str, method: str = "basic", 
                            max_length: int = 500) -> dict[str, str]:
        """Preview normalization changes on a text sample."""
        if len(text) > max_length:
            preview_text = text[:max_length] + "..."
        else:
            preview_text = text
        
        normalized_preview = self.apply_normalization(preview_text, method)
        
        return {
            "original": preview_text,
            "normalized": normalized_preview,
            "method": method,
            "changes_detected": preview_text != normalized_preview
        }