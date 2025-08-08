"""Audio segmentation functionality."""

from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError


class AudioSegmenter:
    """Audio segmentation processor."""
    
    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers or config.max_workers
    
    def segment_file_fixed(self, input_path: Path, output_dir: Path, 
                          segment_length: float, overwrite: bool = False) -> list[Path]:
        """Segment a single audio file using fixed length."""
        if not config.is_audio_file(input_path):
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Placeholder for actual segmentation implementation
            # In real implementation, this would use librosa, pydub, or similar
            print(f"Segmenting {input_path} into {segment_length}s chunks")
            
            # For demonstration, create mock segment files
            segments = []
            base_name = input_path.stem
            
            # Mock: assume 30-second file, create 3 segments of 10s each
            for i in range(3):
                segment_name = f"{base_name}_segment_{i:03d}{input_path.suffix}"
                segment_path = output_dir / segment_name
                
                if not segment_path.exists() or overwrite:
                    # In real implementation, this would create actual audio segments
                    segment_path.touch()
                    segments.append(segment_path)
            
            return segments
            
        except Exception as e:
            raise AudioProcessingError(f"Failed to segment {input_path}: {str(e)}")
    
    def segment_file_vad(self, input_path: Path, output_dir: Path, 
                        vad_model: str, overwrite: bool = False) -> list[Path]:
        """Segment a single audio file using VAD."""
        if not config.is_audio_file(input_path):
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")
        
        model_config = config.get_model_config("vad", vad_model)
        if not model_config.get("enabled", False):
            raise ModelNotAvailableError(f"VAD model {vad_model} is not available")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Placeholder for actual VAD segmentation
            print(f"VAD segmenting {input_path} using {vad_model}")
            
            # Mock VAD segments
            segments = []
            base_name = input_path.stem
            
            # Mock: create variable length segments based on "voice activity"
            segment_info = [(0.5, 3.2), (4.1, 7.8), (9.0, 12.5)]  # start, end times
            
            for i, (start, end) in enumerate(segment_info):
                segment_name = f"{base_name}_vad_{i:03d}_{start:.1f}_{end:.1f}{input_path.suffix}"
                segment_path = output_dir / segment_name
                
                if not segment_path.exists() or overwrite:
                    segment_path.touch()
                    segments.append(segment_path)
            
            return segments
            
        except Exception as e:
            raise AudioProcessingError(f"Failed to VAD segment {input_path}: {str(e)}")
    
    def segment_fixed_length(self, input_dir: Path, output_dir: Path, 
                           segment_length: float, overwrite: bool = False) -> dict[str, list[Path]]:
        """Segment all audio files in directory using fixed length."""
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
            
            segments = self.segment_file_fixed(audio_file, file_output_dir, segment_length, overwrite)
            return audio_file.name, segments
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, segments = future.result()
                results[file_name] = segments
        
        return results
    
    def segment_vad(self, input_dir: Path, output_dir: Path, 
                   vad_model: str, overwrite: bool = False) -> dict[str, list[Path]]:
        """Segment all audio files in directory using VAD."""
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
            
            segments = self.segment_file_vad(audio_file, file_output_dir, vad_model, overwrite)
            return audio_file.name, segments
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, segments = future.result()
                results[file_name] = segments
        
        return results