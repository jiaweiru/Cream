"""Acoustic frontend functionality for audio separation and enhancement.

This module provides classes for audio source separation and audio enhancement
using various machine learning models and signal processing techniques.

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
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

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

    This class provides functionality to separate audio sources from mixed audio
    using various separation models by `python-audio-separator`.

    Attributes:
        max_workers (int): Maximum number of worker threads for parallel processing.

    Example:
        Basic usage:

            separator = AudioSeparator(max_workers=4)
            output_files = separator.separate_file(
                Path("input.wav"),
                Path("output/"),
                method="uvr"
            )
    """

    def __init__(self, max_workers: int | None = None):
        """Initialize AudioSeparator.

        Args:
            max_workers (int | None): Maximum number of worker threads.
                If None, uses config.max_workers.
        """
        self.max_workers = max_workers or config.max_workers

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
            logger.error(f"Unsupported audio format for separation: {input_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")

        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            if method == "uvr":
                return self._separate_with_UVR(input_path, output_dir, overwrite)
            else:
                logger.error(f"Unknown separation method: {method}")
                raise ModelNotAvailableError(f"Unknown separation method: {method}")

        except Exception as e:
            logger.exception(f"Failed to separate {input_path}")
            raise AudioProcessingError(f"Failed to separate {input_path}: {str(e)}")

    def _separate_with_UVR(
        self, input_path: Path, output_dir: Path, overwrite: bool
    ) -> list[Path]:
        """Separate using UVR (Ultimate Vocal Remover) model.

        Args:
            input_path (Path): Path to input audio file.
            output_dir (Path): Directory for output files.
            overwrite (bool): Whether to overwrite existing files.

        Returns:
            list[Path]: List of separated component file paths.
        """
        logger.info(f"UVR separating {input_path}")
        outputs = []
        base_name = input_path.stem

        for component in ["vocals", "accompaniment"]:
            output_name = f"{base_name}_{component}{input_path.suffix}"
            output_path = output_dir / output_name

            if not output_path.exists() or overwrite:
                # TODO: Implement actual UVR model inference
                output_path.touch()
                outputs.append(output_path)

        return outputs

    def separate_directory(
        self, input_dir: Path, output_dir: Path, method: str, overwrite: bool = False
    ) -> dict[str, list[Path]]:
        """Separate all audio files in directory.

        Args:
            input_dir (Path): Directory containing input audio files.
            output_dir (Path): Directory where separated files will be saved.
            method (str): Separation method to use.
            overwrite (bool): Whether to overwrite existing output files.

        Returns:
            dict[str, list[Path]]: Mapping of input filename to separated file paths.

        Raises:
            FileNotFoundError: If input directory doesn't exist.
            AudioProcessingError: If no audio files found or processing fails.
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)

        if not audio_files:
            logger.error(f"No audio files found in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")

        results = {}

        def process_file(audio_file):
            relative_path = audio_file.relative_to(input_dir)
            file_output_dir = output_dir / relative_path.parent / relative_path.stem

            separated_files = self.separate_file(
                audio_file, file_output_dir, method, overwrite
            )
            return audio_file.name, separated_files

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(process_file, af): af for af in audio_files
            }

            for future in concurrent.futures.as_completed(future_to_file):
                file_name, separated_files = future.result()
                results[file_name] = separated_files

        return results


class AudioEnhancer:
    """Audio enhancement and noise reduction processor.

    This class provides functionality to enhance audio quality by reducing noise
    and improving signal clarity using various enhancement methods.

    Attributes:
        max_workers (int): Maximum number of worker threads for parallel processing.

    Example:
        Basic usage:

            enhancer = AudioEnhancer(max_workers=4)
            success = enhancer.enhance_file(
                Path("noisy.wav"),
                Path("clean.wav"),
                method="deep-filter-net"
            )
    """

    def __init__(self, max_workers: int | None = None):
        """Initialize AudioEnhancer.

        Args:
            max_workers (int | None): Maximum number of worker threads.
                If None, uses config.max_workers.
        """
        self.max_workers = max_workers or config.max_workers

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
            logger.error(f"Unsupported audio format for enhancement: {input_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")

        if output_path.exists() and not overwrite:
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if method == "deep-filter-net":
                return self._enhance_with_deep_filter_net(input_path, output_path)
            elif method == "speechenhancement":
                return self._enhance_with_speech_enhancement(input_path, output_path)
            elif method == "rnnoise":
                return self._enhance_with_rnnoise(input_path, output_path)
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
        # TODO: Implement actual Deep Filter Net model inference
        import shutil

        shutil.copy2(input_path, output_path)
        return True

    def _enhance_with_speech_enhancement(
        self, input_path: Path, output_path: Path
    ) -> bool:
        """Enhance using Speech Enhancement model.

        Args:
            input_path (Path): Input audio file path.
            output_path (Path): Output audio file path.

        Returns:
            bool: True if enhancement was successful.
        """
        logger.info(f"Speech Enhancement processing {input_path}")
        # TODO: Implement actual Speech Enhancement model inference
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
        logger.info(f"RNNoise processing {input_path}")
        # TODO: Implement actual RNNoise model inference
        import shutil

        shutil.copy2(input_path, output_path)
        return True

    def enhance_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        method: str = "deep-filter-net",
        overwrite: bool = False,
    ) -> list[Path]:
        """Enhance all audio files in directory.

        Args:
            input_dir (Path): Directory containing input audio files.
            output_dir (Path): Directory where enhanced files will be saved.
            method (str): Enhancement method to use.
            overwrite (bool): Whether to overwrite existing output files.

        Returns:
            list[Path]: List of paths to successfully enhanced audio files.

        Raises:
            FileNotFoundError: If input directory doesn't exist.
            AudioProcessingError: If no audio files found.
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)

        if not audio_files:
            logger.error(f"No audio files found in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")

        enhanced_files = []

        def process_file(audio_file):
            relative_path = audio_file.relative_to(input_dir)
            output_name = f"{relative_path.stem}_enhanced{relative_path.suffix}"
            output_path = output_dir / relative_path.parent / output_name

            if self.enhance_file(audio_file, output_path, method, overwrite):
                return output_path
            return None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(process_file, af): af for af in audio_files
            }

            for future in concurrent.futures.as_completed(future_to_file):
                result = future.result()
                if result:
                    enhanced_files.append(result)

        return enhanced_files
