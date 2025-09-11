"""Audio processing templates - separation, enhancement, and basic processing."""

import subprocess
from pathlib import Path

import librosa
import soundfile as sf

from cream.core.processor import register_processor
from cream.audio.audio_processor import BaseAudioProcessor
from cream.core.exceptions import AudioProcessingError
from cream.core.logging import get_logger

logger = get_logger(__name__)


@register_processor("audio_resampler")
class AudioResampler(BaseAudioProcessor):
    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> Path:
        """Resample audio to target sample rate."""
        self.validate_input(input_path)

        output_path = output_path or input_path
        if "target_sr" not in kwargs:
            logger.warning(
                "Can't get target samplerate, using default target_sr=22050."
            )
        target_sr = int(kwargs.get("target_sr", 22050))

        y, sr = librosa.load(input_path, sr=target_sr)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, y, sr)
        return output_path


@register_processor("audio_normalizer")
class AudioNormalizer(BaseAudioProcessor):
    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> Path:
        """Normalize audio using ffmpeg-normlize.
        learn more: https://github.com/slhck/ffmpeg-normalize
        """
        self.validate_input(input_path)

        output_path = output_path or input_path
        normalization_type = kwargs.get("normalization_type")
        target_level = kwargs.get("target_level")

        # ffmpeg-normalize uses EBU loudness normalization by default
        # with a target level of -23 LUFS.
        cmd = ["ffmpeg-normalize", str(input_path), "-o", str(output_path), "-f"]
        if normalization_type is not None:
            cmd += ["-nt", normalization_type]
        if target_level is not None:
            cmd += ["-t", target_level]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}\nstdout: {e.stdout}\nstderr: {e.stderr}")
            raise AudioProcessingError from e
        return output_path or input_path
