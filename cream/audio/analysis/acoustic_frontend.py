"""Acoustic frontend functionality for audio separation and enhancement.

This module provides classes for audio source separation and audio enhancement
using various methods including python-audio-separator models and ClearerVoice-Studio
enhancement models.

The classes now use a factory pattern for extensible model management, allowing
easy addition of new models without modifying existing code.

Classes:
    AudioSeparator: Handles audio source separation tasks using multiple model types.
    AudioEnhancer: Handles audio enhancement and noise reduction tasks.

Example:
    Basic usage:

        from cream.audio.analysis.acoustic_frontend import AudioSeparator, AudioEnhancer

        # Audio separation with python-audio-separator
        separator = AudioSeparator()
        separated_files = separator.separate_file(input_path, output_dir, "audio-separator-vr")

        # Audio enhancement with ClearerVoice-Studio
        enhancer = AudioEnhancer()
        enhancer.enhance_file(input_path, output_path, "clearervoice-migu")
"""

from pathlib import Path

from cream.core.config import config
from cream.core.exceptions import (
    AudioProcessingError,
    InvalidFormatError,
    ModelNotAvailableError,
)
from cream.core.logging import get_logger
from cream.core.model_factory import separation_factory, enhancement_factory

logger = get_logger(__name__)


class AudioSeparator:
    """Audio source separation processor using multiple model architectures.

    This class provides functionality to separate audio sources using various
    separation models including python-audio-separator models (VR, MDX, HT-Demucs)
    and Spleeter. Models are managed through a factory pattern for extensibility.

    The processor supports both single file and batch directory processing with
    configurable multi-threading for efficient parallel processing.

    Attributes:
        available_methods: List of available separation model names.
        default_method: Default separation method if none specified.

    Example:
        Basic usage with python-audio-separator models:

            separator = AudioSeparator()
            
            # Use VR architecture model
            output_files = separator.separate_file(
                Path("input.wav"),
                Path("output/"),
                method="audio-separator-vr"
            )
            
            # Use MDX-Net architecture model
            output_files = separator.separate_file(
                Path("input.wav"),
                Path("output/"),
                method="audio-separator-mdx"
            )
    """

    def __init__(self) -> None:
        """Initialize AudioSeparator with available separation methods."""
        self._model_instances = {}
        self.available_methods = separation_factory.list_models()
        
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
        """Get or create model instance for the specified method.
        
        Args:
            method: Name of the separation method/model.
            
        Returns:
            Model instance ready for separation.
            
        Raises:
            ModelNotAvailableError: If the method is not available or fails to load.
        """
        if method in self._model_instances:
            return self._model_instances[method]

        # Get model configuration from config
        model_config = config.get_model_config("separation", method)
        if not model_config and method not in self.available_methods:
            # If not in config, create default config for factory models
            model_config = {"enabled": True}
        
        if not model_config.get("enabled", True):
            raise ModelNotAvailableError(
                f"Separation method {method} is not enabled"
            )

        try:
            # Create model using factory
            model = separation_factory.create_model(method, model_config)
            self._model_instances[method] = model
            logger.info(f"Created separation model: {method}")
            return model

        except Exception as e:
            logger.exception(f"Failed to create separation model {method}")
            raise ModelNotAvailableError(
                f"Failed to create separation model {method}: {str(e)}"
            )

    def separate_file(
        self, input_path: Path, output_dir: Path, method: str, overwrite: bool = False
    ) -> list[Path]:
        """Separate a single audio file using specified method.

        Args:
            input_path: Path to input audio file.
            output_dir: Directory where separated files will be saved.
            method: Separation method to use (e.g., "audio-separator-vr", "audio-separator-mdx", "spleeter").
            overwrite: Whether to overwrite existing output files.

        Returns:
            List of paths to generated separated audio files.

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
            logger.error(f"Separation method {method} is not available")
            raise ModelNotAvailableError(
                f"Separation method {method} is not available"
            )

        try:
            # Get model instance and perform separation
            model = self._get_model(method)
            
            # Check if output files already exist
            base_name = input_path.stem
            potential_outputs = list(output_dir.glob(f"{base_name}*"))
            if potential_outputs and not overwrite:
                logger.info(f"Output files already exist for {input_path.name}, skipping")
                return potential_outputs
            
            # Perform separation using the model
            if not model.is_loaded:
                model.load()
            separated_files = model.separate(input_path, output_dir)
            
            logger.info(f"Successfully separated {input_path} into {len(separated_files)} files")
            return separated_files

        except Exception as e:
            logger.exception(f"Failed to separate {input_path}")
            raise AudioProcessingError(f"Failed to separate {input_path}: {str(e)}")

    def separate_directory(
        self, input_dir: Path, output_dir: Path, method: str, overwrite: bool = False
    ) -> dict[str, list[Path]]:
        """Separate all audio files in a directory using the specified method.
        
        Args:
            input_dir: Path to the input directory containing audio files.
            output_dir: Path to the output directory where separated files will be saved.
            method: Separation method to use.
            overwrite: Whether to overwrite existing output files.
            
        Returns:
            Dictionary mapping original filenames to lists of separated file paths.
            
        Raises:
            FileNotFoundError: If the input directory does not exist.
            AudioProcessingError: If no audio files are found or processing fails.
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Find all audio files
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            logger.error(f"No audio files found in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        results = {}
        
        # Process files sequentially
        for audio_file in audio_files:
            try:
                relative_path = audio_file.relative_to(input_dir)
                file_output_dir = output_dir / relative_path.parent / relative_path.stem
                
                separated_files = self.separate_file(audio_file, file_output_dir, method, overwrite)
                results[audio_file.name] = separated_files
            except Exception as e:
                logger.error(f"Failed to process {audio_file}: {str(e)}")
                results[audio_file.name] = []
        
        successful = sum(1 for files in results.values() if files)
        logger.info(f"Processed {len(audio_files)} files, {successful} successful")
        return results


class AudioEnhancer:
    """Audio enhancement and noise reduction processor using multiple models.

    This class provides functionality to enhance audio quality using various
    enhancement models including ClearerVoice-Studio models (MiGu, DataBaker)
    and DeepFilterNet. Models are managed through a factory pattern for extensibility.

    The processor supports both single file and batch directory processing with
    configurable multi-threading for efficient parallel processing.

    Attributes:
        available_methods: List of available enhancement model names.
        default_method: Default enhancement method if none specified.

    Example:
        Basic usage with ClearerVoice-Studio models:

            enhancer = AudioEnhancer()
            
            # Use MiGu model
            success = enhancer.enhance_file(
                Path("noisy.wav"),
                Path("clean.wav"),
                method="clearervoice-migu"
            )
            
            # Use DataBaker model
            success = enhancer.enhance_file(
                Path("noisy.wav"),
                Path("clean.wav"),
                method="clearervoice-databaker"
            )
    """

    def __init__(self) -> None:
        """Initialize AudioEnhancer with available enhancement methods."""
        self._model_instances = {}
        self.available_methods = enhancement_factory.list_models()
        
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
        """Get or create model instance for the specified method.
        
        Args:
            method: Name of the enhancement method/model.
            
        Returns:
            Model instance ready for enhancement.
            
        Raises:
            ModelNotAvailableError: If the method is not available or fails to load.
        """
        if method in self._model_instances:
            return self._model_instances[method]

        # Get model configuration from config
        model_config = config.get_model_config("enhancement", method)
        if not model_config and method not in self.available_methods:
            # If not in config, create default config for factory models
            model_config = {"enabled": True}
        
        if not model_config.get("enabled", True):
            raise ModelNotAvailableError(
                f"Enhancement method {method} is not enabled"
            )

        try:
            # Create model using factory
            model = enhancement_factory.create_model(method, model_config)
            self._model_instances[method] = model
            logger.info(f"Created enhancement model: {method}")
            return model

        except Exception as e:
            logger.exception(f"Failed to create enhancement model {method}")
            raise ModelNotAvailableError(
                f"Failed to create enhancement model {method}: {str(e)}"
            )

    def enhance_file(
        self,
        input_path: Path,
        output_path: Path,
        method: str,
        overwrite: bool = False,
    ) -> bool:
        """Enhance a single audio file using specified method.

        Args:
            input_path: Path to input audio file.
            output_path: Path where enhanced file will be saved.
            method: Enhancement method ("clearervoice-migu", "clearervoice-databaker", "deep-filter-net").
            overwrite: Whether to overwrite existing output file.

        Returns:
            True if enhancement was performed, False if skipped.

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
            logger.info(f"Output file already exists: {output_path}, skipping")
            return False

        # Use default method if none specified and available
        if not method and self.default_method:
            method = self.default_method
            logger.info(f"Using default enhancement method: {method}")

        # Check if method is available
        if method not in self.available_methods:
            logger.error(f"Enhancement method {method} is not available")
            raise AudioProcessingError(
                f"Enhancement method {method} is not available"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Get model instance and perform enhancement
            model = self._get_model(method)
            
            # Perform enhancement using the model
            if not model.is_loaded:
                model.load()
            success = model.enhance(input_path, output_path)
            
            if success:
                logger.info(f"Successfully enhanced {input_path} -> {output_path}")
            else:
                logger.warning(f"Enhancement may have failed for {input_path}")
            
            return success

        except Exception as e:
            logger.exception(f"Failed to enhance {input_path}")
            raise AudioProcessingError(f"Failed to enhance {input_path}: {str(e)}")

    def enhance_directory(
        self, input_dir: Path, output_dir: Path, method: str, overwrite: bool = False
    ) -> dict[str, bool]:
        """Enhance all audio files in a directory using the specified method.
        
        Args:
            input_dir: Path to the input directory containing audio files.
            output_dir: Path to the output directory where enhanced files will be saved.
            method: Enhancement method to use.
            overwrite: Whether to overwrite existing output files.
            
        Returns:
            Dictionary mapping original filenames to enhancement success status.
            
        Raises:
            FileNotFoundError: If the input directory does not exist.
            AudioProcessingError: If no audio files are found or processing fails.
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Find all audio files
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            logger.error(f"No audio files found in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        results = {}
        
        # Process files sequentially
        for audio_file in audio_files:
            try:
                relative_path = audio_file.relative_to(input_dir)
                output_path = output_dir / relative_path
                
                success = self.enhance_file(audio_file, output_path, method, overwrite)
                results[audio_file.name] = success
            except Exception as e:
                logger.error(f"Failed to enhance {audio_file}: {str(e)}")
                results[audio_file.name] = False
        
        successful = sum(1 for success in results.values() if success)
        logger.info(f"Processed {len(audio_files)} files, {successful} successful")
        return results
