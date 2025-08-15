"""Audio processing templates - separation, enhancement, and basic processing."""

from pathlib import Path

from cream.core.processor import processor_registry
from cream.audio.audio_processor import BaseAudioProcessor
from cream.core.exceptions import AudioProcessingError


# Audio Separation Processor Example
class AudioSeparatorVR(BaseAudioProcessor):
    """Audio separator using VR architecture - Template Implementation."""

    def process_single(
        self, input_path: Path, output_path: Path = None, **kwargs
    ) -> list[Path]:
        """Separate audio using VR model - Template Implementation."""
        self.validate_input(input_path)

        # Template implementation - replace with actual model code
        raise AudioProcessingError(
            "VR separator not implemented - add your model integration here"
        )


# Audio Enhancement Processor Example
class FRCRNEnhancer(BaseAudioProcessor):
    """Audio enhancer using FRCRN - Template Implementation."""

    def process_single(
        self, input_path: Path, output_path: Path = None, **kwargs
    ) -> Path:
        """Enhance audio using FRCRN - Template Implementation."""
        self.validate_input(input_path)

        # Template implementation - replace with actual model code
        raise AudioProcessingError(
            "FRCRN enhancer not implemented - add your model integration here"
        )


# Basic Audio Processing Example
class AudioResampler(BaseAudioProcessor):
    """Audio resampler - Template Implementation."""

    def process_single(
        self, input_path: Path, output_path: Path = None, **kwargs
    ) -> Path:
        """Resample audio to target sample rate - Template Implementation."""
        self.validate_input(input_path)

        # Template implementation - replace with actual resampling code
        raise AudioProcessingError(
            "Audio resampler not implemented - add your resampling logic here"
        )


# Register processors
processor_registry.register("audio_separator_vr", AudioSeparatorVR)
processor_registry.register("frcrn_enhancer", FRCRNEnhancer)
processor_registry.register("audio_resampler", AudioResampler)
