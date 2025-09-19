"""Audio analysis processor templates."""

from pathlib import Path
import subprocess

from cream.core.processor import register_processor
from cream.audio.audio_processor import BaseAudioProcessor
from cream.core.exceptions import AudioProcessingError
from cream.core.logging import get_logger

from mutagen import File

logger = get_logger()


@register_processor("audio_metaviewer")
class MetaViewer(BaseAudioProcessor):
    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> dict[str, int | float]:
        self.validate_input(input_path)

        audio = File(input_path)
        if audio is None:
            logger.error(f"Failed to load file: {input_path}")
            raise AudioProcessingError

        return {
            "channels": getattr(audio.info, "channels", None),
            "length": getattr(audio.info, "length", None),
            "sample_rate": getattr(audio.info, "sample_rate", None),
            "bits_per_sample": getattr(audio.info, "bits_per_sample", None),
            "bitrate": getattr(audio.info, "bitrate", None),
        }


def process_batch(
    self,
    input_files: list[Path],
    output_dir: Path | None = None,
    num_workers: int | None = None,
    **kwargs,
):
    process_results = super().process_batch(
        input_files, output_dir, num_workers, **kwargs
    )

    # Print length distribution with youplot
    lengths = [r["length"] for r in process_results]
    try:
        result = subprocess.run(
            ["uplot", "hist"],
            input="\n".join(map(str, lengths)),
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(
            f"Command failed: {e}\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        raise AudioProcessingError from e

    return process_results
