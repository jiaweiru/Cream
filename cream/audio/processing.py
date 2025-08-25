"""Audio processing templates - separation, enhancement, and basic processing."""

from pathlib import Path

import librosa
import soundfile as sf

from cream.core.processor import register_processor
from cream.audio.audio_processor import BaseAudioProcessor
from cream.core.exceptions import AudioProcessingError


# Audio Separation Processor Example
@register_processor("audio_separator_vr")
class AudioSeparatorVR(BaseAudioProcessor):
    """Audio separator using VR architecture - Template Implementation."""

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> list[Path]:
        """Separate audio using VR model - Template Implementation."""
        self.validate_input(input_path)

        # Template implementation - replace with actual model code
        error_msg = "VR separator not implemented - add your model integration here"
        self.logger.error(error_msg)
        raise AudioProcessingError(error_msg)


# Audio Enhancement Processor Example
@register_processor("frcrn_enhancer")
class FRCRNEnhancer(BaseAudioProcessor):
    """Audio enhancer using FRCRN - Template Implementation."""

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> Path:
        """Enhance audio using FRCRN - Template Implementation."""
        self.validate_input(input_path)

        # Template implementation - replace with actual model code
        error_msg = "FRCRN enhancer not implemented - add your model integration here"
        self.logger.error(error_msg)
        raise AudioProcessingError(error_msg)


@register_processor("audio_resampler")
class AudioResampler(BaseAudioProcessor):
    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> Path:
        """Resample audio to target sample rate."""
        self.validate_input(input_path)

        output_path = output_path or input_path
        target_sr = kwargs["target_sr"]

        y, sr = librosa.load(input_path, sr=target_sr)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, y, sr)
