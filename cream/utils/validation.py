"""Input validation utilities."""

from pathlib import Path
import re

from cream.core.config import config
from cream.core.exceptions import ValidationError


class InputValidator:
    """Input validation utility for various data types and formats."""
    
    def validate_file_path(self, path: str | Path, must_exist: bool = True,
                          allowed_extensions: list[str] | None = None) -> Path:
        """Validate file path."""
        if isinstance(path, str):
            path = Path(path)
        
        if must_exist and not path.exists():
            raise ValidationError(f"File does not exist: {path}")
        
        if not must_exist and not path.parent.exists():
            raise ValidationError(f"Parent directory does not exist: {path.parent}")
        
        if allowed_extensions:
            if path.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
                raise ValidationError(f"File extension {path.suffix} not in allowed extensions: {allowed_extensions}")
        
        return path
    
    def validate_directory_path(self, path: str | Path, must_exist: bool = True,
                               create_if_not_exists: bool = False) -> Path:
        """Validate directory path."""
        if isinstance(path, str):
            path = Path(path)
        
        if must_exist and not path.exists():
            if create_if_not_exists:
                path.mkdir(parents=True, exist_ok=True)
            else:
                raise ValidationError(f"Directory does not exist: {path}")
        
        if path.exists() and not path.is_dir():
            raise ValidationError(f"Path exists but is not a directory: {path}")
        
        return path
    
    def validate_audio_file(self, path: str | Path, must_exist: bool = True) -> Path:
        """Validate audio file path."""
        path = self.validate_file_path(path, must_exist, config.audio_formats)
        
        if must_exist and not config.is_audio_file(path):
            raise ValidationError(f"File is not a supported audio format: {path}")
        
        return path
    
    def validate_text_file(self, path: str | Path, must_exist: bool = True) -> Path:
        """Validate text file path."""
        path = self.validate_file_path(path, must_exist, config.text_formats)
        
        if must_exist and not config.is_text_file(path):
            raise ValidationError(f"File is not a supported text format: {path}")
        
        return path
    
    def validate_sample_rate(self, sample_rate: int) -> int:
        """Validate audio sample rate."""
        valid_rates = [8000, 16000, 22050, 44100, 48000, 96000, 192000]
        
        if sample_rate not in valid_rates:
            raise ValidationError(f"Sample rate {sample_rate} not in supported rates: {valid_rates}")
        
        return sample_rate
    
    def validate_positive_number(self, value: int | float, name: str = "value") -> int | float:
        """Validate positive number."""
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{name} must be a number, got {type(value)}")
        
        if value <= 0:
            raise ValidationError(f"{name} must be positive, got {value}")
        
        return value
    
    def validate_range(self, value: int | float, min_val: int | float, 
                      max_val: int | float, name: str = "value") -> int | float:
        """Validate number within range."""
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{name} must be a number, got {type(value)}")
        
        if value < min_val or value > max_val:
            raise ValidationError(f"{name} must be between {min_val} and {max_val}, got {value}")
        
        return value
    
    def validate_regex_pattern(self, pattern: str) -> str:
        """Validate regex pattern."""
        try:
            re.compile(pattern)
            return pattern
        except re.error as e:
            raise ValidationError(f"Invalid regex pattern '{pattern}': {str(e)}")
    
    def validate_choice(self, value: str, choices: list[str], name: str = "value") -> str:
        """Validate choice from list of options."""
        if value not in choices:
            raise ValidationError(f"{name} must be one of {choices}, got '{value}'")
        
        return value
    
    def validate_model_name(self, model: str, category: str) -> str:
        """Validate model name for given category."""
        available_models = list(config.models.get(category, {}).keys())
        
        if not available_models:
            raise ValidationError(f"No models available for category '{category}'")
        
        if model not in available_models:
            raise ValidationError(f"Model '{model}' not available for {category}. Available: {available_models}")
        
        model_config = config.get_model_config(category, model)
        if not model_config.get("enabled", False):
            raise ValidationError(f"Model '{model}' is not enabled for {category}")
        
        return model
    
    def validate_count(self, count: int, max_count: int | None = None, 
                      name: str = "count") -> int:
        """Validate count parameter."""
        if not isinstance(count, int):
            raise ValidationError(f"{name} must be an integer, got {type(count)}")
        
        if count <= 0:
            raise ValidationError(f"{name} must be positive, got {count}")
        
        if max_count is not None and count > max_count:
            raise ValidationError(f"{name} cannot exceed {max_count}, got {count}")
        
        return count
    
    def validate_percentage(self, value: int | float, name: str = "percentage") -> float:
        """Validate percentage value (0-100)."""
        return float(self.validate_range(value, 0, 100, name))
    
    def validate_probability(self, value: int | float, name: str = "probability") -> float:
        """Validate probability value (0-1)."""
        return float(self.validate_range(value, 0, 1, name))
    
    def validate_file_size(self, path: Path, min_size: int | None = None,
                          max_size: int | None = None) -> int:
        """Validate file size in bytes."""
        if not path.exists():
            raise ValidationError(f"File does not exist: {path}")
        
        size = path.stat().st_size
        
        if min_size is not None and size < min_size:
            raise ValidationError(f"File {path} is too small ({size} bytes, minimum {min_size} bytes)")
        
        if max_size is not None and size > max_size:
            raise ValidationError(f"File {path} is too large ({size} bytes, maximum {max_size} bytes)")
        
        return size
    
    def validate_batch_size(self, batch_size: int, total_items: int) -> int:
        """Validate batch size for processing."""
        batch_size = self.validate_positive_number(batch_size, "batch_size")
        
        if batch_size > total_items:
            # Adjust batch size to total items
            batch_size = total_items
        
        return int(batch_size)
    
    def validate_output_format(self, format_name: str, supported_formats: list[str]) -> str:
        """Validate output format."""
        format_name = format_name.lower()
        supported_formats = [f.lower() for f in supported_formats]
        
        return self.validate_choice(format_name, supported_formats, "output format")


# Global validator instance
validator = InputValidator()