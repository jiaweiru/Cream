"""Text normalization functionality.

This module provides comprehensive text normalization capabilities including
whitespace cleanup, punctuation normalization, encoding fixes, and web content
cleaning.

Classes:
    TextNormalizer: Main class for text normalization operations.
    
Example:
    Basic usage:
        
        from cream.text.normalization import TextNormalizer
        
        normalizer = TextNormalizer()
        clean_text = normalizer.apply_normalization(dirty_text, "basic")
        
        # Normalize files
        success = normalizer.normalize_file(
            input_file=Path("input.txt"),
            output_file=Path("output.txt"),
            method="aggressive"
        )
"""

from pathlib import Path
import re
import json

from cream.core.config import config
from cream.core.exceptions import InvalidFormatError, AudioProcessingError
from cream.core.logging import get_logger

logger = get_logger(__name__)


class TextNormalizer:
    """Text normalization processor.
    
    This class provides various text normalization methods to clean and standardize
    text data. It supports multiple normalization strategies and file formats.
    
    Attributes:
        patterns (dict): Dictionary containing normalization pattern categories
            and their corresponding regex patterns and replacements.
            
    Example:
        Basic usage:
            
            normalizer = TextNormalizer()
            clean_text = normalizer.apply_normalization("messy   text!!!", "basic")
            
            # File processing
            normalizer.normalize_file(
                input_file=Path("input.txt"),
                output_file=Path("clean.txt"),
                method="aggressive"
            )
    """
    
    def __init__(self):
        """Initialize TextNormalizer with predefined normalization patterns."""
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
        """Apply normalization to text based on method.
        
        Args:
            text (str): Input text to normalize.
            method (str): Normalization method ("basic", "aggressive", "whitespace_only", 
                "unicode", "web").
                
        Returns:
            str: Normalized text.
            
        Raises:
            AudioProcessingError: If normalization method is unknown.
        """
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
            logger.error(f"Unknown text normalization method: {method}")
            raise AudioProcessingError(f"Unknown normalization method: {method}")
        
        return normalized_text.strip()
    
    def normalize_file(self, input_file: Path, output_file: Path, 
                      method: str = "basic", overwrite: bool = False) -> bool:
        """Normalize text in a file.
        
        Supports plain text, JSON, and CSV file formats.
        
        Args:
            input_file (Path): Path to input text file.
            output_file (Path): Path to output normalized file.
            method (str): Normalization method to apply.
            overwrite (bool): Whether to overwrite existing output file.
            
        Returns:
            bool: True if normalization was performed, False if skipped.
            
        Raises:
            InvalidFormatError: If input file format is not supported.
            FileNotFoundError: If input file doesn't exist.
            AudioProcessingError: If normalization process fails.
        """
        if not config.is_text_file(input_file):
            logger.error(f"Unsupported text format: {input_file.suffix}")
            raise InvalidFormatError(f"Unsupported text format: {input_file.suffix}")
        
        if not input_file.exists():
            logger.error(f"Input file not found: {input_file}")
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
            logger.exception(f"Failed to normalize text file {input_file}")
            raise AudioProcessingError(f"Failed to normalize text file: {str(e)}")
    
    def normalize_directory(self, input_dir: Path, output_dir: Path, 
                           method: str = "basic", pattern: str = "*.txt",
                           overwrite: bool = False) -> list[Path]:
        """Normalize all text files in directory.
        
        Args:
            input_dir (Path): Directory containing input text files.
            output_dir (Path): Directory where normalized files will be saved.
            method (str): Normalization method to apply.
            pattern (str): File pattern to match (e.g., "*.txt", "*.json").
            overwrite (bool): Whether to overwrite existing output files.
            
        Returns:
            list[Path]: List of successfully normalized file paths.
            
        Raises:
            FileNotFoundError: If input directory doesn't exist.
            AudioProcessingError: If no matching files found.
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found for text normalization: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        text_files = list(input_dir.glob(pattern))
        if not text_files:
            logger.error(f"No text files found in {input_dir} matching pattern {pattern}")
            raise AudioProcessingError(f"No text files found in {input_dir} matching pattern {pattern}")
        
        normalized_files = []
        
        for text_file in text_files:
            try:
                relative_path = text_file.relative_to(input_dir)
                output_file = output_dir / relative_path
                
                if self.normalize_file(text_file, output_file, method, overwrite):
                    normalized_files.append(output_file)
                    
            except Exception as e:
                logger.exception(f"Failed to normalize {text_file}")
                continue
        
        return normalized_files
    
    def normalize_text_list(self, texts: list[str], method: str = "basic") -> list[str]:
        """Normalize a list of text strings.
        
        Args:
            texts (list[str]): List of text strings to normalize.
            method (str): Normalization method to apply.
            
        Returns:
            list[str]: List of normalized text strings.
        """
        return [self.apply_normalization(text, method) for text in texts]
    
    def get_normalization_stats(self, original_text: str, normalized_text: str) -> dict[str, dict[str, int]]:
        """Get statistics about the normalization process.
        
        Args:
            original_text (str): Original text before normalization.
            normalized_text (str): Text after normalization.
            
        Returns:
            dict[str, dict[str, int]]: Dictionary containing statistics about
                original text, normalized text, and changes made.
        """
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
        """Preview normalization changes on a text sample.
        
        Args:
            text (str): Text to preview normalization on.
            method (str): Normalization method to apply.
            max_length (int): Maximum length of text to preview.
            
        Returns:
            dict[str, str]: Dictionary containing original text, normalized text,
                method used, and whether changes were detected.
        """
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