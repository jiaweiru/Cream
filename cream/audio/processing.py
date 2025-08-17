"""Audio processing templates - separation, enhancement, and basic processing."""

from pathlib import Path

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


# Basic Audio Processing Example
@register_processor("audio_resampler")
class AudioResampler(BaseAudioProcessor):
    """Audio resampler - Template Implementation."""

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> Path:
        """Resample audio to target sample rate - Template Implementation."""
        self.validate_input(input_path)

        # Template implementation - replace with actual resampling code
        error_msg = "Audio resampler not implemented - add your resampling logic here"
        self.logger.error(error_msg)
        raise AudioProcessingError(error_msg)
