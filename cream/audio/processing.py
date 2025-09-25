"""Audio processing templates - separation, enhancement, and basic processing."""

import subprocess
from pathlib import Path

import librosa
import soundfile as sf

from cream.core.processor import register_processor, ModelBackedProcessor
from cream.audio.audio_processor import BaseAudioProcessor
from cream.core.exceptions import AudioProcessingError
from cream.core.logging import get_logger
from cream.core.config import config

from mutagen import File

logger = get_logger()


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
    """Normalize audio using ffmpeg-normlize.
    learn more: https://github.com/slhck/ffmpeg-normalize
    """

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> Path:
        self.validate_input(input_path)
        output_path = output_path or input_path
        normalization_type = kwargs.get("normalization_type")
        target_level = kwargs.get("target_level")
        sample_rate = getattr(File(input_path).info, "sample_rate", None)

        # ffmpeg-normalize uses EBU loudness normalization by default
        # with a target level of -23 LUFS.
        cmd = ["ffmpeg-normalize", str(input_path), "-o", str(output_path), "-f"]
        if normalization_type is not None:
            cmd += ["-nt", normalization_type]
        if target_level is not None:
            cmd += ["-t", target_level]
        if sample_rate is not None:
            cmd += ["-ar", str(sample_rate)]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            error_message = f"Command failed: {e}\nstdout: {e.stdout or ''}\nstderr: {e.stderr or ''}"
            logger.error(error_message)
            raise AudioProcessingError(error_message) from e
        return output_path


class ClearVoiceProcessor(ModelBackedProcessor, BaseAudioProcessor):
    """Speech processing using ClearVoice.
    learn more: https://github.com/modelscope/ClearerVoice-Studio
    """

    def patch_checkpoint_dir(self, cache_root: Path):
        try:
            from clearvoice import network_wrapper
        except ImportError as e:
            logger.error("ClearVoice is not found, using `pip install clearvoice`")
            raise AudioProcessingError from e

        def wrap_loader(loader):
            def inner(self):
                loader(self)
                model_name = getattr(self, "model_name", None)
                target_dir = cache_root / model_name
                target_dir.mkdir(parents=True, exist_ok=True)
                # checkpoint_dir expects a string path
                self.args.checkpoint_dir = str(target_dir.expanduser().resolve())

            return inner

        for name in ["load_args_se", "load_args_ss", "load_args_sr", "load_args_tse"]:
            if hasattr(network_wrapper, name):
                orig = getattr(network_wrapper, name)
                setattr(network_wrapper, name, wrap_loader(orig))

    def load_model(self):
        try:
            from clearvoice import ClearVoice
        except ImportError as e:
            logger.error("ClearVoice is not found, using `pip install clearvoice`")
            raise AudioProcessingError from e

        self.patch_checkpoint_dir(cache_root=config.model_dir / "ClearVoice")
        model = ClearVoice(task=self.task, model_names=[self.model])

        return model

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> Path:
        self.validate_input(input_path)
        output_path = output_path or input_path

        self.model(input_path=input_path, online_write=True, output_path=output_path)

        return output_path


# Add more ClearVoice models here~
# Required supported `task` and `model`


@register_processor("audio_denoiser_mossformergan_16k")
class AudioDenoiserMossFormerGANSR16k(ClearVoiceProcessor):
    task = "speech_enhancement"
    model = "MossFormerGAN_SE_16K"


@register_processor("audio_denoiser_mossformer2_48k")
class AudioDenoiserMossFormer2SR48k(ClearVoiceProcessor):
    task = "speech_enhancement"
    model = "MossFormer2_SE_48K"


@register_processor("audio_separator_mossformer2_16k")
class AudioSeparatorMossFormer2SR16k(ClearVoiceProcessor):
    task = "speech_separation"
    model = "MossFormer2_SS_16K"
