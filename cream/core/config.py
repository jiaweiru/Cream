"""Configuration management for cream package."""

from pathlib import Path
import os


class Config:
    """Global configuration manager."""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".cream"
        self.config_dir.mkdir(exist_ok=True)
        
        # Default configurations
        self.audio_formats = [".wav", ".mp3", ".flac", ".m4a", ".ogg"]
        self.text_formats = [".txt", ".json", ".csv"]
        
        # Model configurations (placeholders for future use)
        self.models = {
            "mos": {
                "nisqa": {"path": "", "enabled": False},
                "utmosv2": {"path": "", "enabled": False}
            },
            "asr": {
                "paraformer": {"path": "", "enabled": False},
                "whisper": {"path": "", "enabled": False}
            },
            "vad": {
                "silero": {"path": "", "enabled": False}
            },
            "speaker": {
                "3d-speaker": {"path": "", "enabled": False}
            }
        }
        
        # Processing defaults
        self.default_sample_rate = 16000
        self.default_segment_length = 10.0
        self.max_workers = os.cpu_count() or 4
    
    def get_model_config(self, category: str, model_name: str) -> dict[str, str | bool]:
        """Get model configuration."""
        return self.models.get(category, {}).get(model_name, {})
    
    def is_audio_file(self, path: Path) -> bool:
        """Check if file is supported audio format."""
        return path.suffix.lower() in self.audio_formats
    
    def is_text_file(self, path: Path) -> bool:
        """Check if file is supported text format."""
        return path.suffix.lower() in self.text_formats


config = Config()