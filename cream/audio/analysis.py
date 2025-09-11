"""Audio analysis processor templates."""

from pathlib import Path

from cream.core.processor import register_processor
from cream.audio.audio_processor import BaseAudioProcessor
from cream.core.exceptions import AudioProcessingError
from cream.core.logging import get_logger

logger = get_logger(__name__)


# Audio Analysis Processor Example
@register_processor("mos_evaluator")
class MOSEvaluator(BaseAudioProcessor):
    """MOS (Mean Opinion Score) evaluator - Template Implementation."""

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> dict[str, float]:
        """Evaluate MOS score - Template Implementation."""
        self.validate_input(input_path)

        # Template implementation - replace with actual model code
        error_msg = "MOS evaluator not implemented - add your model integration here"
        logger.error(error_msg)
        raise AudioProcessingError(error_msg)
