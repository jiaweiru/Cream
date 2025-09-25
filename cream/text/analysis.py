"""Text analysis processor templates."""

import re
import subprocess
from pathlib import Path

from cream.core.processor import register_processor
from cream.text.text_processor import BaseTextProcessor
from cream.core.exceptions import TextProcessingError
from cream.core.logging import get_logger

logger = get_logger()


@register_processor("text_metaviewer")
class TextMetaViewer(BaseTextProcessor):
    @staticmethod
    def word_count(text: str) -> int:
        tokens = re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9]+", text)
        return len(tokens)

    def process_single(
        self, input_path: Path, output_path: Path | None = None, **kwargs
    ) -> dict[str, int | float]:
        self.validate_input(input_path)

        meta_info = []
        with input_path.open("r", encoding="utf-8") as fin:
            for line in fin:
                text = line.strip()
                meta_info.append(
                    # Add more info you want
                    {
                        "text": text,
                        "str_length": len(text),
                        "word_count": self.word_count(text),
                        "has_digit": any(ch.isdigit() for ch in text),
                        "has_zh": bool(re.search(r"[\u4e00-\u9fff]", text)),
                        "has_en": bool(re.search(r"[A-Za-z]", text)),
                    }
                )

        # Print length distribution with youplot
        lengths = [r["word_count"] for r in meta_info]
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
            raise TextProcessingError(error_message) from e

        return len(meta_info)
