"""Acoustic frontend functionality for audio separation and enhancement."""

from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError


class AcousticFrontend:
    """Acoustic frontend processor for separation and enhancement."""
    
    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers or config.max_workers
    
    def separate_file(self, input_path: Path, output_dir: Path, 
                     method: str, overwrite: bool = False) -> list[Path]:
        """Separate a single audio file."""
        if not config.is_audio_file(input_path):
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Placeholder for actual separation implementation
            if method == "uvr":
                print(f"UVR separating {input_path}")
                # Mock UVR separation (vocals, accompaniment)
                outputs = []
                base_name = input_path.stem
                
                for component in ["vocals", "accompaniment"]:
                    output_name = f"{base_name}_{component}{input_path.suffix}"
                    output_path = output_dir / output_name
                    
                    if not output_path.exists() or overwrite:
                        # In real implementation, this would create actual separated audio
                        output_path.touch()
                        outputs.append(output_path)
                
                return outputs
                
            elif method == "deep-filter-net":
                print(f"Deep Filter Net enhancing {input_path}")
                # Mock noise reduction
                base_name = input_path.stem
                output_name = f"{base_name}_enhanced{input_path.suffix}"
                output_path = output_dir / output_name
                
                if not output_path.exists() or overwrite:
                    output_path.touch()
                    return [output_path]
                return []
            
            else:
                raise AudioProcessingError(f"Unknown separation method: {method}")
                
        except Exception as e:
            raise AudioProcessingError(f"Failed to separate {input_path}: {str(e)}")
    
    def separate_directory(self, input_dir: Path, output_dir: Path, 
                          method: str, overwrite: bool = False) -> dict[str, list[Path]]:
        """Separate all audio files in directory."""
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        results = {}
        
        def process_file(audio_file):
            relative_path = audio_file.relative_to(input_dir)
            file_output_dir = output_dir / relative_path.parent / relative_path.stem
            
            separated_files = self.separate_file(audio_file, file_output_dir, method, overwrite)
            return audio_file.name, separated_files
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, separated_files = future.result()
                results[file_name] = separated_files
        
        return results
    
    def enhance_audio(self, input_path: Path, output_path: Path, 
                     method: str = "deep-filter-net", overwrite: bool = False) -> bool:
        """Enhance a single audio file (noise reduction)."""
        if not config.is_audio_file(input_path):
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")
        
        if output_path.exists() and not overwrite:
            return False
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"Enhancing {input_path} using {method}")
            
            # In real implementation, this would apply noise reduction/enhancement
            import shutil
            shutil.copy2(input_path, output_path)
            
            return True
            
        except Exception as e:
            raise AudioProcessingError(f"Failed to enhance {input_path}: {str(e)}")
    
    def batch_enhance(self, audio_files: list[Path], output_dir: Path, 
                     method: str = "deep-filter-net", overwrite: bool = False) -> list[Path]:
        """Enhance multiple audio files."""
        enhanced_files = []
        
        def process_file(audio_file):
            output_name = f"{audio_file.stem}_enhanced{audio_file.suffix}"
            output_path = output_dir / output_name
            
            if self.enhance_audio(audio_file, output_path, method, overwrite):
                return output_path
            return None
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                result = future.result()
                if result:
                    enhanced_files.append(result)
        
        return enhanced_files