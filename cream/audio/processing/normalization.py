"""Audio normalization functionality."""

from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError


class AudioNormalizer:
    """Audio normalization processor."""
    
    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers or config.max_workers
    
    def normalize_file(self, input_path: Path, output_path: Path, 
                      method: str, target_level: float | None = None,
                      overwrite: bool = False) -> bool:
        """Normalize a single audio file."""
        if not config.is_audio_file(input_path):
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")
        
        if output_path.exists() and not overwrite:
            return False
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set default target levels
        if target_level is None:
            target_level = -23.0 if method == "loudness" else -20.0
        
        try:
            # Placeholder for actual normalization implementation
            # In real implementation, this would use ffmpeg, pyloudnorm, or similar
            if method == "energy":
                print(f"Energy normalizing {input_path} -> {output_path} to {target_level} dB")
            elif method == "loudness":
                print(f"Loudness normalizing {input_path} -> {output_path} to {target_level} LUFS")
            else:
                raise AudioProcessingError(f"Unknown normalization method: {method}")
            
            # For now, just copy the file
            import shutil
            shutil.copy2(input_path, output_path)
            
            return True
            
        except Exception as e:
            raise AudioProcessingError(f"Failed to normalize {input_path}: {str(e)}")
    
    def normalize_directory(self, input_dir: Path, output_dir: Path, 
                           method: str, target_level: float | None = None,
                           overwrite: bool = False) -> list[Path]:
        """Normalize all audio files in a directory."""
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        processed_files = []
        
        def process_file(audio_file):
            relative_path = audio_file.relative_to(input_dir)
            output_path = output_dir / relative_path
            
            if self.normalize_file(audio_file, output_path, method, target_level, overwrite):
                return output_path
            return None
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                result = future.result()
                if result:
                    processed_files.append(result)
        
        return processed_files