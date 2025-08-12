"""Configuration management for the cream audio and text processing package.

This module provides centralized configuration management for the cream package,
including supported file formats, model configurations, and processing defaults.
The global `config` instance can be imported and used throughout the package.

Example:
    Basic usage of the configuration manager:

    >>> from cream.core.config import config
    >>> config.is_audio_file(Path("audio.wav"))
    True

Classes:
    Config: Global configuration manager with file format checking and model configs.
"""

from pathlib import Path
import os


class Config:
    """Global configuration manager for the cream package.

    This class manages all configuration settings including supported file formats,
    model configurations, processing defaults, and user-specific directories.
    It automatically creates a configuration directory in the user's home folder
    and provides methods to check file formats and retrieve model configurations.

    Attributes:
        home_dir (Path): User's home directory path.
        config_dir (Path): Cream configuration directory (~/.cream).
        audio_formats (list[str]): List of supported audio file extensions.
        text_formats (list[str]): List of supported text file extensions.
        models (dict): Configuration for various AI models (MOS, ASR, VAD, SS, SE, Speaker).
        max_workers (int): Maximum number of worker threads for parallel processing.

    Example:
        Creating and using a configuration instance:

        >>> config = Config()
        >>> config.is_audio_file(Path("test.wav"))
        True
        >>> config.get_model_config("mos", "nisqa")
        {'path': '', 'enabled': False}
    """

    def __init__(self) -> None:
        """Initialize the configuration manager.

        Sets up default configurations, creates the config directory if it doesn't
        exist, and initializes all default values for audio formats, text formats,
        model configurations, and processing parameters.

        The configuration directory is created at ~/.cream and will be used for
        storing user-specific settings and cached model files in the future.
        """
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".cream"
        self.model_dir = self.config_dir / "models"
        self.model_dir.mkdir(exist_ok=True)

        # Default configurations
        self.audio_formats = [
            ".wav",
            ".flac",
            ".mp3",
            ".ogg",
            ".opus",
            ".m4a",
            ".aiff",
            ".ac3",
        ]
        self.text_formats = [".txt", ".json", ".csv"]

        self.models = {
            "mos": {
                "nisqa": {
                    "path": "",
                    "enabled": False,
                    "model_type": "official",
                    "description": "NISQA: Speech Quality and Naturalness Assessment",
                    "project_url": "https://github.com/gabrielmittag/NISQA",
                    "paper": "https://arxiv.org/abs/2104.09494",
                },
                "utmosv2": {
                    "path": "",
                    "enabled": False,
                    "model_type": "official",
                    "description": "UTMOSv2: UTokyo-SaruLab MOS Prediction System",
                    "project_url": "https://github.com/sarulab-speech/UTMOSv2",
                    "paper": "https://arxiv.org/abs/2409.09305",
                },
            },
            "asr": {
                "paraformer": {
                    "path": "",
                    "enabled": False,
                    "model_type": "toolkit",
                    "toolkit": "funasr",
                    "description": "Paraformer ASR model from FunASR toolkit",
                    "project_url": "https://github.com/modelscope/FunASR",
                    "paper": "https://arxiv.org/abs/2206.08317",
                },
                "whisper": {
                    "path": "",
                    "enabled": False,
                    "model_type": "official",
                    "description": "OpenAI Whisper automatic speech recognition model",
                    "project_url": "https://github.com/openai/whisper",
                    "paper": "https://arxiv.org/abs/2212.04356",
                },
            },
            "vad": {
                "silero": {
                    "path": "",
                    "enabled": False,
                    "model_type": "toolkit",
                    "toolkit": "torch.hub",
                    "description": "Silero VAD model for voice activity detection",
                    "project_url": "https://github.com/snakers4/silero-vad",
                    "paper": "https://arxiv.org/abs/2103.04467",
                }
            },
            "speaker": {
                "3d-speaker": {
                    "path": "",
                    "enabled": False,
                    "model_type": "toolkit",
                    "toolkit": "3d-speaker",
                    "description": "3D-Speaker toolkit for speaker recognition and diarization",
                    "project_url": "https://github.com/alibaba-damo-academy/3D-Speaker",
                    "paper": "https://arxiv.org/abs/2306.15354",
                }
            },
            "separation": {
                "uvr-roformer": {
                    "path": "",
                    "enabled": False,
                    "model_type": "toolkit",
                    "toolkit": "ultimate-vocal-remover",
                    "description": "Roformer model via Ultimate Vocal Remover toolkit",
                    "project_url": "https://github.com/Anjok07/ultimatevocalremovergui",
                    "paper": "https://arxiv.org/abs/2210.01448",
                },
                "uvr-mdx": {
                    "path": "",
                    "enabled": False,
                    "model_type": "toolkit",
                    "toolkit": "ultimate-vocal-remover",
                    "description": "MDX-Net model via Ultimate Vocal Remover toolkit",
                    "project_url": "https://github.com/Anjok07/ultimatevocalremovergui",
                    "paper": "https://arxiv.org/abs/2108.13187",
                },
                "spleeter": {
                    "path": "",
                    "enabled": False,
                    "model_type": "official",
                    "description": "Deezer Spleeter for source separation",
                    "project_url": "https://github.com/deezer/spleeter",
                    "paper": "https://arxiv.org/abs/2002.08933",
                },
            },
            "enhancement": {
                "deep-filter-net": {
                    "path": "",
                    "enabled": False,
                    "model_type": "official",
                    "description": "DeepFilterNet for real-time speech enhancement",
                    "project_url": "https://github.com/Rikorose/DeepFilterNet",
                    "paper": "https://arxiv.org/abs/2110.05588",
                },
            },
        }

        # Processing defaults
        self.max_workers = os.cpu_count() or 4

    def get_model_config(
        self, category: str, model_name: str
    ) -> dict[str, str | bool | int | list]:
        """Get configuration for a specific AI model.

        Retrieves the configuration dictionary for the specified model within
        the given category. Returns an empty dictionary if the category or
        model is not found.

        Args:
            category: Model category (e.g., "mos", "asr", "vad", "speaker", "separation", "enhancement").
            model_name: Specific model name within the category.

        Returns:
            Dictionary containing model configuration with keys:
            - 'path': Model file path or identifier
            - 'enabled': Whether the model is enabled
            - 'model_type': Type of model ("official" or "toolkit")
            - 'toolkit': Toolkit name (for toolkit models only)
            - 'description': Human-readable description
            - 'project_url': Official project repository URL
            - 'paper': Research paper URL or DOI
            Returns empty dict if category or model not found.

        Example:
            >>> config = Config()
            >>> config.get_model_config("mos", "nisqa")
            {'path': '', 'enabled': False, 'model_type': 'official', ...}
            >>> config.get_model_config("invalid", "model")
            {}
        """
        return self.models.get(category, {}).get(model_name, {})

    def get_available_models(self, category: str) -> list[str]:
        """Get list of available (enabled) models for a category.

        Args:
            category: Model category to check.

        Returns:
            List of enabled model names.

        Example:
            >>> config = Config()
            >>> config.get_available_models("separation")
            []  # Empty if no models are enabled
        """
        category_models = self.models.get(category, {})
        return [
            model_name
            for model_name, config_dict in category_models.items()
            if config_dict.get("enabled", False)
        ]

    def get_models_by_type(self, category: str, model_type: str) -> list[str]:
        """Get list of models by type for a category.

        Args:
            category: Model category to check.
            model_type: Model type ("official" or "toolkit").

        Returns:
            List of model names matching the specified type.

        Example:
            >>> config = Config()
            >>> config.get_models_by_type("separation", "toolkit")
            ['uvr-roformer', 'uvr-mdx', 'speechenhancement']
        """
        category_models = self.models.get(category, {})
        return [
            model_name
            for model_name, config_dict in category_models.items()
            if config_dict.get("model_type") == model_type
        ]

    def get_toolkit_models(self, toolkit_name: str) -> dict[str, list[str]]:
        """Get all models that use a specific toolkit.

        Args:
            toolkit_name: Name of the toolkit to search for.

        Returns:
            Dictionary mapping category names to lists of model names using the toolkit.

        Example:
            >>> config = Config()
            >>> config.get_toolkit_models("ultimate-vocal-remover")
            {'separation': ['uvr-roformer', 'uvr-mdx']}
        """
        result = {}
        for category, models in self.models.items():
            toolkit_models = [
                model_name
                for model_name, config_dict in models.items()
                if config_dict.get("toolkit") == toolkit_name
            ]
            if toolkit_models:
                result[category] = toolkit_models
        return result

    def is_audio_file(self, path: Path) -> bool:
        """Check if a file has a supported audio format extension.

        Compares the file extension (case-insensitive) against the list of
        supported audio formats defined in self.audio_formats.

        Args:
            path: Path object representing the file to check.

        Returns:
            True if the file extension is in the supported audio formats list,
            False otherwise.

        Example:
            >>> config = Config()
            >>> config.is_audio_file(Path("audio.wav"))
            True
            >>> config.is_audio_file(Path("document.pdf"))
            False
        """
        return path.suffix.lower() in self.audio_formats

    def is_text_file(self, path: Path) -> bool:
        """Check if a file has a supported text format extension.

        Compares the file extension (case-insensitive) against the list of
        supported text formats defined in self.text_formats.

        Args:
            path: Path object representing the file to check.

        Returns:
            True if the file extension is in the supported text formats list,
            False otherwise.

        Example:
            >>> config = Config()
            >>> config.is_text_file(Path("data.txt"))
            True
            >>> config.is_text_file(Path("audio.wav"))
            False
        """
        return path.suffix.lower() in self.text_formats


config = Config()
