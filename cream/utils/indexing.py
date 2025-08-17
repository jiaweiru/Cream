"""Index matching utilities with regex support."""

from pathlib import Path
import re
import json

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, ValidationError
from cream.core.logging import get_logger

logger = get_logger(__name__)


class IndexMatcher:
    """Index matching utility with regex pattern support."""

    def __init__(self):
        self.compiled_patterns = {}

    def compile_pattern(self, pattern: str) -> re.Pattern:
        """Compile and cache regex pattern."""
        if pattern not in self.compiled_patterns:
            try:
                self.compiled_patterns[pattern] = re.compile(pattern)
            except re.error as e:
                logger.exception(f"Invalid regex pattern '{pattern}': {str(e)}")
                raise ValidationError(f"Invalid regex pattern '{pattern}': {str(e)}")

        return self.compiled_patterns[pattern]

    def extract_indices_from_filename(self, filename: str, pattern: str) -> list[str]:
        """Extract indices from filename using regex pattern."""
        compiled_pattern = self.compile_pattern(pattern)
        matches = compiled_pattern.findall(filename)

        # If pattern has groups, return the groups; otherwise return full matches
        if isinstance(matches, list) and matches:
            if isinstance(matches[0], tuple):
                # Multiple groups - flatten or return as is based on context
                return [item for match in matches for item in match if item]
            else:
                # Single group or no groups
                return matches

        return []

    def extract_indices_from_content(self, content: str, pattern: str) -> list[str]:
        """Extract indices from file content using regex pattern."""
        compiled_pattern = self.compile_pattern(pattern)
        matches = compiled_pattern.findall(content)

        if isinstance(matches, list) and matches:
            if isinstance(matches[0], tuple):
                return [item for match in matches for item in match if item]
            else:
                return matches

        return []

    def load_source_indices(self, source: Path, pattern: str) -> dict[str, list[str]]:
        """Load indices from source file or directory."""
        indices = {}

        if source.is_file():
            # Extract from single file
            try:
                if source.suffix.lower() == ".json":
                    with open(source, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    if isinstance(data, dict):
                        for key, value in data.items():
                            content_indices = self.extract_indices_from_content(
                                str(value), pattern
                            )
                            if content_indices:
                                indices[key] = content_indices
                    elif isinstance(data, list):
                        for i, item in enumerate(data):
                            content_indices = self.extract_indices_from_content(
                                str(item), pattern
                            )
                            if content_indices:
                                indices[f"item_{i}"] = content_indices
                else:
                    # Plain text file
                    with open(source, "r", encoding="utf-8") as f:
                        content = f.read()

                    content_indices = self.extract_indices_from_content(
                        content, pattern
                    )
                    if content_indices:
                        indices[source.name] = content_indices

                # Also try extracting from filename
                filename_indices = self.extract_indices_from_filename(
                    source.name, pattern
                )
                if filename_indices:
                    indices[f"{source.name}_filename"] = filename_indices

            except Exception as e:
                logger.exception(f"Failed to load indices from {source}")

        elif source.is_dir():
            # Extract from all files in directory
            for file_path in source.rglob("*"):
                if file_path.is_file():
                    try:
                        # Extract from filename
                        filename_indices = self.extract_indices_from_filename(
                            file_path.name, pattern
                        )
                        if filename_indices:
                            indices[file_path.name] = filename_indices

                        # Extract from content if it's a text file
                        if config.is_text_file(file_path):
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    content = f.read()

                                content_indices = self.extract_indices_from_content(
                                    content, pattern
                                )
                                if content_indices:
                                    content_key = f"{file_path.name}_content"
                                    indices[content_key] = content_indices

                            except Exception:
                                # Skip files that can't be read as text
                                continue

                    except Exception as e:
                        logger.exception(f"Failed to process {file_path}")
                        continue

        return indices

    def load_target_indices(self, target: Path, pattern: str) -> dict[str, list[str]]:
        """Load indices from target file or directory."""
        # Same logic as source for now
        return self.load_source_indices(target, pattern)

    def find_matches(
        self,
        source_indices: dict[str, list[str]],
        target_indices: dict[str, list[str]],
        match_type: str = "exact",
    ) -> list[dict[str, str | float]]:
        """Find matches between source and target indices."""
        matches = []

        for source_key, source_values in source_indices.items():
            for source_value in source_values:
                for target_key, target_values in target_indices.items():
                    for target_value in target_values:
                        is_match = False
                        confidence = 0.0

                        if match_type == "exact":
                            is_match = source_value == target_value
                            confidence = 1.0 if is_match else 0.0

                        elif match_type == "partial":
                            if (
                                source_value in target_value
                                or target_value in source_value
                            ):
                                is_match = True
                                # Simple confidence based on length ratio
                                shorter = min(len(source_value), len(target_value))
                                longer = max(len(source_value), len(target_value))
                                confidence = shorter / longer if longer > 0 else 0.0

                        elif match_type == "fuzzy":
                            # Simple fuzzy matching using edit distance
                            similarity = self.calculate_similarity(
                                source_value, target_value
                            )
                            is_match = similarity > 0.7  # Threshold for fuzzy matching
                            confidence = similarity

                        if is_match:
                            matches.append(
                                {
                                    "source": source_key,
                                    "source_value": source_value,
                                    "target": target_key,
                                    "target_value": target_value,
                                    "match_type": match_type,
                                    "confidence": round(confidence, 3),
                                }
                            )

        # Sort by confidence descending
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches

    def calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings using simple edit distance."""
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        # Simple Levenshtein distance implementation
        len1, len2 = len(s1), len(s2)
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j

        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        max_len = max(len1, len2)
        similarity = 1 - (dp[len1][len2] / max_len) if max_len > 0 else 1.0
        return max(0.0, similarity)

    def match_indices(
        self, source: Path, target: Path, pattern: str, match_type: str = "exact"
    ) -> list[dict[str, str | float]]:
        """Main method to match indices between source and target."""
        if not source.exists():
            logger.error(f"Source not found: {source}")
            raise FileNotFoundError(f"Source not found: {source}")
        if not target.exists():
            logger.error(f"Target not found: {target}")
            raise FileNotFoundError(f"Target not found: {target}")

        try:
            # Load indices from source and target
            source_indices = self.load_source_indices(source, pattern)
            target_indices = self.load_target_indices(target, pattern)

            if not source_indices:
                logger.error(f"No indices found in source using pattern: {pattern}")
                raise AudioProcessingError(
                    f"No indices found in source using pattern: {pattern}"
                )
            if not target_indices:
                logger.error(f"No indices found in target using pattern: {pattern}")
                raise AudioProcessingError(
                    f"No indices found in target using pattern: {pattern}"
                )

            # Find matches
            matches = self.find_matches(source_indices, target_indices, match_type)

            return matches

        except Exception as e:
            logger.exception("Failed to match indices")
            raise AudioProcessingError(f"Failed to match indices: {str(e)}")

    def generate_mapping_file(
        self, matches: list[dict[str, str | float]], output_file: Path
    ) -> None:
        """Generate a mapping file from matches."""
        mapping_data = {
            "total_matches": len(matches),
            "matches": matches,
            "generated_by": "cream index matcher",
        }

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(mapping_data, f, indent=2, ensure_ascii=False)

    def get_match_statistics(
        self, matches: list[dict[str, str | float]]
    ) -> dict[str, int | float | dict[str, int]]:
        """Get statistics about matches."""
        if not matches:
            return {"total_matches": 0}

        # Group by match type and confidence
        by_type = {}
        confidence_ranges = {"high": 0, "medium": 0, "low": 0}

        for match in matches:
            match_type = match["match_type"]
            confidence = match["confidence"]

            by_type[match_type] = by_type.get(match_type, 0) + 1

            if confidence >= 0.8:
                confidence_ranges["high"] += 1
            elif confidence >= 0.5:
                confidence_ranges["medium"] += 1
            else:
                confidence_ranges["low"] += 1

        avg_confidence = sum(m["confidence"] for m in matches) / len(matches)

        stats = {
            "total_matches": len(matches),
            "average_confidence": round(avg_confidence, 3),
            "by_match_type": by_type,
            "by_confidence_range": confidence_ranges,
            "unique_sources": len(set(m["source"] for m in matches)),
            "unique_targets": len(set(m["target"] for m in matches)),
        }

        return stats
