"""Text processing templates - normalization and other processing operations."""

from pathlib import Path

from cream.core.processor import register_processor, ModelBackedProcessor
from cream.text.text_processor import BaseTextProcessor
from cream.core.exceptions import TextProcessingError
from cream.core.logging import get_logger

logger = get_logger()


@register_processor("text_normalizer")
class TextNormalizer(ModelBackedProcessor, BaseTextProcessor):
    """Chinese text normalize using `WeTextProcessing`
    learn more: https://github.com/wenet-e2e/WeTextProcessing
    """

    def load_model(self):
        try:
            from tn.chinese.normalizer import Normalizer as ZhNormalizer
        except ImportError as e:
            logger.error(
                "WeTextProcessing is not found, using `pip install WeTextProcessing`"
            )
            raise TextProcessingError from e

        model = ZhNormalizer(remove_erhua=True, overwrite_cache=True)

        return model

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> Path:
        self.validate_input(input_path)

        output_path = output_path or input_path

        # Each line is considered a separate text
        with (
            input_path.open("r", encoding="utf-8") as fin,
            output_path.open("w", encoding="utf-8") as fout,
        ):
            for line in fin:
                fout.write(self.model.normalize(line.strip()) + "\n")

        return output_path
