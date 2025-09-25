"""Audio analysis processor templates."""

import json
import subprocess
from pathlib import Path

from cream.core.processor import register_processor, ModelBackedProcessor
from cream.audio.audio_processor import BaseAudioProcessor
from cream.core.exceptions import AudioProcessingError
from cream.core.logging import get_logger
from cream.core.config import config, set_env

from mutagen import File

logger = get_logger()


@register_processor("audio_metaviewer")
class AudioMetaViewer(BaseAudioProcessor):
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
            subprocess.run(
                ["uplot", "hist"],
                input="\n".join(map(str, lengths)),
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            error_message = f"Command failed: {e}\nstdout: {e.stdout or ''}\nstderr: {e.stderr or ''}"
            logger.error(error_message)
            raise AudioProcessingError(error_message) from e

        return process_results


@register_processor("speech_vad_fsmn")
class VAD_FSMN(ModelBackedProcessor):
    """Speech processing using FunASR.
    learn more: https://github.com/modelscope/FunASR
    """

    def load_model(self):
        try:
            from funasr import AutoModel
        except ImportError as e:
            logger.error("FunASR is not found, using `pip install funasr`")
            raise AudioProcessingError from e
        with set_env(MODELSCOPE_CACHE=config.model_dir / "ModelScope"):
            model = AutoModel(model="fsmn-vad", model_revision="v2.0.4")

        return model

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> Path:
        self.validate_input(input_path)
        output_path = output_path or input_path.with_suffix(".json")

        result = self.model.generate(input=input_path)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)

        return output_path
