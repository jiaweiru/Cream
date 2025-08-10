"""Acoustic frontend functionality for audio separation and enhancement."""

from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from cream.core.config import config
from cream.core.exceptions import (
    AudioProcessingError,
    InvalidFormatError,
    ModelNotAvailableError,
)


class AudioSeparator:
    """Audio source separation processor."""

    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers or config.max_workers

    def separate_file(
        self, input_path: Path, output_dir: Path, method: str, overwrite: bool = False
    ) -> list[Path]:
        """Separate a single audio file using specified method."""
        if not config.is_audio_file(input_path):
            raise InvalidFormatError(f"Unsupported audio format: {input_path.suffix}")

        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            if method == "uvr":
                return self._separate_with_UVR(input_path, output_dir, overwrite)
            else:
                raise ModelNotAvailableError(f"Unknown separation method: {method}")

        except Exception as e:
            raise AudioProcessingError(f"Failed to separate {input_path}: {str(e)}")

    def _separate_with_UVR(
        self, input_path: Path, output_dir: Path, overwrite: bool
    ) -> list[Path]:
        """Separate using UVR model."""
        print(f"UVR separating {input_path}")
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
    """Audio enhancement and noise reduction processor."""

    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers or config.max_workers

    def enhance_file(
        self,
        input_path: Path,
        output_path: Path,
        method: str = "deep-filter-net",
        overwrite: bool = False,
    ) -> bool:
        """Enhance a single audio file using specified method."""
        if not config.is_audio_file(input_path):
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
                raise AudioProcessingError(f"Unknown enhancement method: {method}")

        except Exception as e:
            raise AudioProcessingError(f"Failed to enhance {input_path}: {str(e)}")

    def _enhance_with_deep_filter_net(
        self, input_path: Path, output_path: Path
    ) -> bool:
        """Enhance using Deep Filter Net model."""
        print(f"Deep Filter Net enhancing {input_path}")
        # TODO: Implement actual Deep Filter Net model inference
        import shutil

        shutil.copy2(input_path, output_path)
        return True

    def _enhance_with_speech_enhancement(
        self, input_path: Path, output_path: Path
    ) -> bool:
        """Enhance using Speech Enhancement model."""
        print(f"Speech Enhancement processing {input_path}")
        # TODO: Implement actual Speech Enhancement model inference
        import shutil

        shutil.copy2(input_path, output_path)
        return True

    def _enhance_with_rnnoise(self, input_path: Path, output_path: Path) -> bool:
        """Enhance using RNNoise model."""
        print(f"RNNoise processing {input_path}")
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
        """Enhance all audio files in directory."""
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)

        if not audio_files:
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
