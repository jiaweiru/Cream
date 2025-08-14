"""Audio analysis processor templates."""

from pathlib import Path

from cream.core.processor import BaseAudioProcessor, processor_registry
from cream.core.exceptions import AudioProcessingError


# Audio Analysis Processor Example
class MOSEvaluator(BaseAudioProcessor):
    """MOS (Mean Opinion Score) evaluator - Template Implementation."""
    
    def process_single(self, input_path: Path, output_path: Path = None, **kwargs) -> dict[str, float]:
        """Evaluate MOS score - Template Implementation."""
        self.validate_input(input_path)
        
        # Template implementation - replace with actual model code
        raise AudioProcessingError("MOS evaluator not implemented - add your model integration here")


# Register processor
processor_registry.register("mos_evaluator", MOSEvaluator)