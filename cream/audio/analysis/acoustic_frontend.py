"""Acoustic frontend functionality for audio separation and enhancement.

This module provides classes for audio source separation and audio enhancement
using various methods.

Classes:
    AudioSeparator: Handles audio source separation tasks.
    AudioEnhancer: Handles audio enhancement and noise reduction tasks.

Example:
    Basic usage:

        from cream.audio.analysis.acoustic_frontend import AudioSeparator, AudioEnhancer

        # Audio separation
        separator = AudioSeparator(max_workers=4)
        separated_files = separator.separate_file(input_path, output_dir, "uvr")

        # Audio enhancement
        enhancer = AudioEnhancer(max_workers=4)
        enhancer.enhance_file(input_path, output_path, "deep-filter-net")
"""

from pathlib import Path

from cream.core.config import config
from cream.core.exceptions import (
    AudioProcessingError,
    InvalidFormatError,
    ModelNotAvailableError,
)
from cream.core.logging import get_logger

logger = get_logger(__name__)


class AudioSeparator:
    """Audio source separation processor.

    This class provides functionality to separate vocals from mixed audio
    using various separation models. Models are loaded lazily when first used.

    Attributes:
        _models (dict): Dictionary containing loaded separation models.

    Example:
        Basic usage:

            separator = AudioSeparator()
            output_files = separator.separate_file(
                Path("input.wav"),
                Path("output/"),
                method="uvr"
            )
    """

    def __init__(self):
        """Initialize AudioSeparator with available separation methods."""
        self._models = {}
        self.available_methods = config.get_available_models("separation")
        if not self.available_methods:
            logger.warning(
                "No separation methods are available. Check model configuration."
            )
        else:
            logger.info(f"Available separation methods: {self.available_methods}")
        self.default_method = (
            self.available_methods[0] if self.available_methods else None
        )

    def _get_model(self, method: str):
        """Load and cache model for the specified method."""
        if method in self._models:
            return self._models[method]

        model_config = config.get_model_config("separation", method)
        if not model_config.get("enabled", False):
            raise ModelNotAvailableError(
                f"Separation method {method} is not available or not enabled"
            )

        # Load model based on method
        try:
            if method in ["uvr-roformer", "uvr-mdx"]:
                # TODO: Replace with actual UVR model loading
                model = f"mock_uvr_model_{method}_{model_config.get('path', '')}"
            elif method == "spleeter":
                # TODO: Replace with actual Spleeter model loading
                model = f"mock_spleeter_model_{model_config.get('path', '')}"
            else:
                raise ValueError(f"Unknown separation method: {method}")

            self._models[method] = model
            logger.info(f"Loaded separation model: {method}")
            return model

        except Exception as e:
            logger.exception(f"Failed to load separation model {method}")
            raise ModelNotAvailableError(
                f"Failed to load separation model {method}: {str(e)}"
            )

    def separate_file(
        self, input_path: Path, output_dir: Path, method: str, overwrite: bool = False
    ) -> list[Path]:
        """Separate a single audio file using specified method.

        Args:
            input_path (Path): Path to input audio file.
            output_dir (Path): Directory where separated files will be saved.
            method (str): Separation method to use (e.g., "uvr").
            overwrite (bool): Whether to overwrite existing output files.

        Returns:
            list[Path]: List of paths to generated separated audio files.

        Raises:
            InvalidFormatError: If input file format is not supported.
            ModelNotAvailableError: If separation method is not available.
            AudioProcessingError: If separation process fails.
        """
        if not config.is_audio_file(input_path):
            logger.error(
                f"Unsupported audio format for separation: {input_path.suffix}"
            )
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Use default method if none specified and available
        if not method and self.default_method:
            method = self.default_method
            logger.info(f"Using default separation method: {method}")

        # Check if method is available
        if method not in self.available_methods:
            logger.error(f"Separation method {method} is not available or not enabled")
            raise ModelNotAvailableError(
                f"Separation method {method} is not available or not enabled"
            )

        try:
            if method in ["uvr-roformer", "uvr-mdx"]:
                return self._separate_with_UVR(input_path, output_dir, overwrite, method)
            elif method == "spleeter":
                return self._separate_with_spleeter(input_path, output_dir, overwrite)
            else:
                logger.error(f"Unknown separation method: {method}")
                raise ModelNotAvailableError(f"Unknown separation method: {method}")

        except Exception as e:
            logger.exception(f"Failed to separate {input_path}")
            raise AudioProcessingError(f"Failed to separate {input_path}: {str(e)}")

    def _separate_with_UVR(
        self, input_path: Path, output_dir: Path, overwrite: bool, method: str = "uvr-roformer"
    ) -> list[Path]:
        """Separate using UVR (Ultimate Vocal Remover) model.

        Args:
            input_path (Path): Path to input audio file.
            output_dir (Path): Directory for output files.
            overwrite (bool): Whether to overwrite existing files.
            method (str): UVR method to use ("uvr-roformer" or "uvr-mdx").

        Returns:
            list[Path]: List of separated component file paths.
        """
        logger.info(f"UVR {method} separating {input_path}")
        loaded_model = self._get_model(method)
        outputs = []
        base_name = input_path.stem

        for component in ["vocals", "accompaniment"]:
            output_name = f"{base_name}_{component}{input_path.suffix}"
            output_path = output_dir / output_name

            if not output_path.exists() or overwrite:
                # TODO: Implement actual UVR model inference using loaded_model
                output_path.touch()
                outputs.append(output_path)

        return outputs

    def _separate_with_spleeter(
        self, input_path: Path, output_dir: Path, overwrite: bool
    ) -> list[Path]:
        """Separate using Spleeter model.

        Args:
            input_path (Path): Path to input audio file.
            output_dir (Path): Directory for output files.
            overwrite (bool): Whether to overwrite existing files.

        Returns:
            list[Path]: List of separated component file paths.
        """
        logger.info(f"Spleeter separating {input_path}")
        loaded_model = self._get_model("spleeter")
        outputs = []
        base_name = input_path.stem

        # Spleeter typically separates into vocals and accompaniment (2stems)
        for component in ["vocals", "accompaniment"]:
            output_name = f"{base_name}_{component}{input_path.suffix}"
            output_path = output_dir / output_name

            if not output_path.exists() or overwrite:
                # TODO: Implement actual Spleeter model inference using loaded_model
                output_path.touch()
                outputs.append(output_path)

        return outputs


class AudioEnhancer:
    """Audio enhancement and noise reduction processor.

    This class provides functionality to enhance audio quality by reducing noise
    and improving signal clarity using various enhancement methods. Models are
    loaded lazily when first used.

    Attributes:
        _models (dict): Dictionary containing loaded enhancement models.

    Example:
        Basic usage:

            enhancer = AudioEnhancer()
            success = enhancer.enhance_file(
                Path("noisy.wav"),
                Path("clean.wav"),
                method="deep-filter-net"
            )
    """

    def __init__(self):
        """Initialize AudioEnhancer with available enhancement methods."""
        self._models = {}
        self.available_methods = config.get_available_models("enhancement")
        if not self.available_methods:
            logger.warning(
                "No enhancement methods are available. Check model configuration."
            )
        else:
            logger.info(f"Available enhancement methods: {self.available_methods}")
        self.default_method = (
            self.available_methods[0] if self.available_methods else None
        )

    def _get_model(self, method: str):
        """Load and cache model for the specified method."""
        if method in self._models:
            return self._models[method]

        model_config = config.get_model_config("enhancement", method)
        if not model_config.get("enabled", False):
            raise ModelNotAvailableError(
                f"Enhancement method {method} is not available or not enabled"
            )

        # Load model based on method
        try:
            if method == "deep-filter-net":
                # TODO: Replace with actual Deep Filter Net model loading
                model = f"mock_deep_filter_net_model_{model_config.get('path', '')}"
            elif method == "rnnoise":
                # TODO: Replace with actual RNNoise model loading
                model = f"mock_rnnoise_model_{model_config.get('path', '')}"
            elif method == "speechenhancement":
                # TODO: Replace with actual SpeechEnhancement model loading
                model = f"mock_speechenhancement_model_{model_config.get('path', '')}"
            else:
                raise ValueError(f"Unknown enhancement method: {method}")

            self._models[method] = model
            logger.info(f"Loaded enhancement model: {method}")
            return model

        except Exception as e:
            logger.exception(f"Failed to load enhancement model {method}")
            raise ModelNotAvailableError(
                f"Failed to load enhancement model {method}: {str(e)}"
            )

    def enhance_file(
        self,
        input_path: Path,
        output_path: Path,
        method: str = "deep-filter-net",
        overwrite: bool = False,
    ) -> bool:
        """Enhance a single audio file using specified method.

        Args:
            input_path (Path): Path to input audio file.
            output_path (Path): Path where enhanced file will be saved.
            method (str): Enhancement method ("deep-filter-net", "speechenhancement", "rnnoise").
            overwrite (bool): Whether to overwrite existing output file.

        Returns:
            bool: True if enhancement was performed, False if skipped.

        Raises:
            InvalidFormatError: If input file format is not supported.
            AudioProcessingError: If enhancement method is unknown or processing fails.
        """
        if not config.is_audio_file(input_path):
            logger.error(
                f"Unsupported audio format for enhancement: {input_path.suffix}"
            )
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")

        if output_path.exists() and not overwrite:
            return False

        # Use default method if none specified and available
        if not method and self.default_method:
            method = self.default_method
            logger.info(f"Using default enhancement method: {method}")

        # Check if method is available
        if method not in self.available_methods:
            logger.error(f"Enhancement method {method} is not available or not enabled")
            raise AudioProcessingError(
                f"Enhancement method {method} is not available or not enabled"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if method == "deep-filter-net":
                return self._enhance_with_deep_filter_net(input_path, output_path)
            elif method == "rnnoise":
                return self._enhance_with_rnnoise(input_path, output_path)
            elif method == "speechenhancement":
                return self._enhance_with_speechenhancement(input_path, output_path)
            else:
                logger.error(f"Unknown enhancement method: {method}")
                raise AudioProcessingError(f"Unknown enhancement method: {method}")

        except Exception as e:
            logger.exception(f"Failed to enhance {input_path}")
            raise AudioProcessingError(f"Failed to enhance {input_path}: {str(e)}")

    def _enhance_with_deep_filter_net(
        self, input_path: Path, output_path: Path
    ) -> bool:
        """Enhance using Deep Filter Net model.

        Args:
            input_path (Path): Input audio file path.
            output_path (Path): Output audio file path.

        Returns:
            bool: True if enhancement was successful.
        """
        logger.info(f"Deep Filter Net enhancing {input_path}")
        loaded_model = self._get_model("deep-filter-net")
        # TODO: Implement actual Deep Filter Net model inference using loaded_model
        import shutil

        shutil.copy2(input_path, output_path)
        return True

    def _enhance_with_rnnoise(self, input_path: Path, output_path: Path) -> bool:
        """Enhance using RNNoise model.

        Args:
            input_path (Path): Input audio file path.
            output_path (Path): Output audio file path.

        Returns:
            bool: True if enhancement was successful.
        """
        logger.info(f"RNNoise enhancing {input_path}")
        loaded_model = self._get_model("rnnoise")
        # TODO: Implement actual RNNoise model inference using loaded_model
        import shutil

        shutil.copy2(input_path, output_path)
        return True

    def _enhance_with_speechenhancement(
        self, input_path: Path, output_path: Path
    ) -> bool:
        """Enhance using SpeechEnhancement model.

        Args:
            input_path (Path): Input audio file path.
            output_path (Path): Output audio file path.

        Returns:
            bool: True if enhancement was successful.
        """
        logger.info(f"SpeechEnhancement enhancing {input_path}")
        loaded_model = self._get_model("speechenhancement")
        # TODO: Implement actual SpeechEnhancement model inference using loaded_model
        import shutil

        shutil.copy2(input_path, output_path)
        return True
