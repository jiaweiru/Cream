"""Text statistics analysis functionality for the cream package.

This module provides comprehensive text analysis capabilities including length
distribution analysis, word count statistics, and file comparison utilities.
It supports various text formats including plain text, JSON, and CSV files.

The analyzer calculates detailed statistics such as character counts, word counts,
percentiles, and distribution patterns for text datasets.

Example:
    Basic usage for text statistics analysis:
    
    >>> from pathlib import Path
    >>> from cream.text.stats import TextStatistics
    >>> 
    >>> analyzer = TextStatistics()
    >>> 
    >>> # Analyze a single file
    >>> stats = analyzer.analyze_file(Path("data.txt"))
    >>> print(f"Average line length: {stats['average_length']}")
    >>> 
    >>> # Analyze all files in a directory
    >>> results = analyzer.analyze_directory(Path("text_files/"))
    >>> 
    >>> # Generate summary
    >>> summary = analyzer.generate_summary(stats)

Classes:
    TextStatistics: Main class for text analysis operations.
"""

from pathlib import Path
import json

from cream.core.config import config
from cream.core.exceptions import InvalidFormatError, AudioProcessingError
from cream.core.logging import get_logger

logger = get_logger(__name__)


class TextStatistics:
    """Comprehensive text statistics analyzer with support for multiple formats.
    
    This class provides methods for analyzing text statistics including line lengths,
    word counts, character distributions, and percentile calculations. It supports
    various text file formats and provides detailed statistical analysis.
    
    The analyzer handles plain text files, JSON data structures, and CSV files,
    extracting meaningful text content and computing comprehensive statistics.
    
    Example:
        Creating and using a text statistics analyzer:
        
        >>> analyzer = TextStatistics()
        >>> stats = analyzer.analyze_file(Path("document.txt"))
        >>> print(f"Total lines: {stats['total_lines']}")
        >>> print(f"Average words per line: {stats['average_words']}")
    """
    
    def analyze_file(self, input_file: Path) -> dict[str, int | float | dict[str, int]]:
        """Analyze comprehensive text statistics for a single file.
        
        Processes the input file and calculates detailed statistics including
        line counts, character counts, word counts, length distributions, and
        percentile information. Handles multiple file formats automatically.
        
        Args:
            input_file: Path to the text file to analyze.
            
        Returns:
            Dictionary containing comprehensive statistics:
            - total_lines: Number of non-empty lines
            - total_characters: Total character count
            - total_words: Total word count
            - average_length: Average line length in characters
            - average_words: Average words per line
            - min_length/max_length: Shortest and longest line lengths
            - median_length: Median line length
            - percentiles: Length percentiles (25th, 50th, 75th, 90th, 95th)
            - length_distribution: Distribution by character length bins
            - word_distribution: Distribution by word count bins
            
        Raises:
            InvalidFormatError: If the file format is not supported.
            FileNotFoundError: If the input file does not exist.
            AudioProcessingError: If the analysis operation fails.
            
        Example:
            Analyze a text file and examine results:
            
            >>> analyzer = TextStatistics()
            >>> stats = analyzer.analyze_file(Path("corpus.txt"))
            >>> print(f"Dataset contains {stats['total_lines']} lines")
            >>> print(f"Average line length: {stats['average_length']:.1f} chars")
            >>> print(f"Longest line: {stats['max_length']} characters")
        """
        if not config.is_text_file(input_file):
            logger.error(f"Unsupported text format for analysis: {input_file.suffix}")
            raise InvalidFormatError(f"Unsupported text format: {input_file.suffix}")
        
        if not input_file.exists():
            logger.error(f"Input file not found for text analysis: {input_file}")
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        try:
            lines = []
            
            if input_file.suffix.lower() == ".json":
                # Handle JSON files
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    lines = [str(item) for item in data]
                elif isinstance(data, dict):
                    lines = [str(value) for value in data.values()]
                else:
                    lines = [str(data)]
                    
            elif input_file.suffix.lower() == ".csv":
                # Handle CSV files
                import csv
                with open(input_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        lines.append(" ".join(row))
                        
            else:
                # Handle plain text files
                with open(input_file, 'r', encoding='utf-8') as f:
                    lines = [line.strip() for line in f.readlines()]
            
            # Remove empty lines
            lines = [line for line in lines if line.strip()]
            
            if not lines:
                return {
                    "total_lines": 0,
                    "total_characters": 0,
                    "total_words": 0,
                    "average_length": 0.0,
                    "average_words": 0.0,
                    "min_length": 0,
                    "max_length": 0,
                    "length_distribution": {},
                    "word_distribution": {},
                    "percentiles": {}
                }
            
            # Calculate basic statistics
            lengths = [len(line) for line in lines]
            word_counts = [len(line.split()) for line in lines]
            
            total_lines = len(lines)
            total_characters = sum(lengths)
            total_words = sum(word_counts)
            average_length = total_characters / total_lines
            average_words = total_words / total_lines
            min_length = min(lengths)
            max_length = max(lengths)
            
            # Calculate percentiles
            sorted_lengths = sorted(lengths)
            n = len(sorted_lengths)
            
            def get_percentile(percentile):
                index = (percentile / 100) * (n - 1)
                if index.is_integer():
                    return sorted_lengths[int(index)]
                else:
                    lower_index = int(index)
                    upper_index = min(lower_index + 1, n - 1)
                    weight = index - lower_index
                    return sorted_lengths[lower_index] * (1 - weight) + sorted_lengths[upper_index] * weight
            
            percentiles = {
                "25th": int(get_percentile(25)),
                "50th": int(get_percentile(50)),
                "75th": int(get_percentile(75)),
                "90th": int(get_percentile(90)),
                "95th": int(get_percentile(95))
            }
            
            # Length distribution (character bins)
            length_bins = [0, 50, 100, 200, 500, 1000, float('inf')]
            length_labels = ['0-50', '50-100', '100-200', '200-500', '500-1000', '1000+']
            length_distribution = {label: 0 for label in length_labels}
            
            for length in lengths:
                for i, (bin_start, bin_end) in enumerate(zip(length_bins[:-1], length_bins[1:])):
                    if bin_start <= length < bin_end:
                        length_distribution[length_labels[i]] += 1
                        break
            
            # Word count distribution
            word_bins = [0, 5, 10, 20, 50, 100, float('inf')]
            word_labels = ['0-5', '5-10', '10-20', '20-50', '50-100', '100+']
            word_distribution = {label: 0 for label in word_labels}
            
            for word_count in word_counts:
                for i, (bin_start, bin_end) in enumerate(zip(word_bins[:-1], word_bins[1:])):
                    if bin_start <= word_count < bin_end:
                        word_distribution[word_labels[i]] += 1
                        break
            
            statistics = {
                "total_lines": total_lines,
                "total_characters": total_characters,
                "total_words": total_words,
                "average_length": round(average_length, 2),
                "average_words": round(average_words, 2),
                "min_length": min_length,
                "max_length": max_length,
                "median_length": int(get_percentile(50)),
                "length_distribution": length_distribution,
                "word_distribution": word_distribution,
                "percentiles": percentiles
            }
            
            return statistics
            
        except Exception as e:
            logger.exception(f"Failed to analyze text statistics for {input_file}")
            raise AudioProcessingError(f"Failed to analyze text statistics: {str(e)}")
    
    def analyze_directory(self, input_dir: Path, pattern: str = "*.txt") -> dict[str, dict[str, int | float | dict[str, int]]]:
        """Analyze text statistics for all matching files in a directory.
        
        Processes all files matching the specified pattern in the input directory
        and calculates statistics for each file. Continues processing even if
        individual files fail to analyze.
        
        Args:
            input_dir: Path to the directory containing text files.
            pattern: Glob pattern for file matching. Defaults to "*.txt".
            
        Returns:
            Dictionary mapping filenames to their respective statistics dictionaries.
            Files that fail to analyze are skipped and logged.
            
        Raises:
            FileNotFoundError: If the input directory does not exist.
            AudioProcessingError: If no matching files are found.
            
        Example:
            Batch analyze all text files in a directory:
            
            >>> analyzer = TextStatistics()
            >>> results = analyzer.analyze_directory(
            ...     Path("documents/"),
            ...     pattern="*.txt"
            ... )
            >>> for filename, stats in results.items():
            ...     print(f"{filename}: {stats['total_lines']} lines")
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found for text analysis: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        text_files = list(input_dir.glob(pattern))
        if not text_files:
            logger.error(f"No text files found in {input_dir} matching pattern {pattern}")
            raise AudioProcessingError(f"No text files found in {input_dir} matching pattern {pattern}")
        
        results = {}
        
        for text_file in text_files:
            try:
                stats = self.analyze_file(text_file)
                results[text_file.name] = stats
            except Exception as e:
                logger.exception(f"Failed to analyze {text_file}")
                continue
        
        return results
    
    def generate_summary(self, statistics: dict[str, int | float | dict[str, int]]) -> dict[str, str | dict[str, int | float | dict[str, int]]]:
        """Generate a structured summary from text statistics.
        
        Converts detailed statistics into a well-organized summary format
        suitable for reporting and visualization. Groups related metrics
        into logical sections.
        
        Args:
            statistics: Statistics dictionary returned by analyze_file().
            
        Returns:
            Structured summary dictionary with sections:
            - file_summary: Basic file metrics
            - length_analysis: Line length analysis
            - distributions: Character and word count distributions
            
        Example:
            Generate a summary from analysis results:
            
            >>> analyzer = TextStatistics()
            >>> stats = analyzer.analyze_file(Path("data.txt"))
            >>> summary = analyzer.generate_summary(stats)
            >>> print(f"Median length: {summary['length_analysis']['median_length']}")
        """
        if not statistics or statistics["total_lines"] == 0:
            return {"error": "No data to summarize"}
        
        summary = {
            "file_summary": {
                "total_lines": statistics["total_lines"],
                "total_characters": statistics["total_characters"],
                "total_words": statistics["total_words"],
                "average_line_length": statistics["average_length"],
                "average_words_per_line": statistics["average_words"]
            },
            "length_analysis": {
                "shortest_line": statistics["min_length"],
                "longest_line": statistics["max_length"],
                "median_length": statistics["median_length"],
                "quartiles": {
                    "Q1": statistics["percentiles"]["25th"],
                    "Q2": statistics["percentiles"]["50th"],
                    "Q3": statistics["percentiles"]["75th"]
                }
            },
            "distributions": {
                "character_length": statistics["length_distribution"],
                "word_count": statistics["word_distribution"]
            }
        }
        
        return summary
    
    def compare_files(self, file1_stats: dict[str, int | float | dict[str, int]], file2_stats: dict[str, int | float | dict[str, int]]) -> dict[str, int | float]:
        """Compare text statistics between two files.
        
        Computes differences and ratios between key statistics of two files,
        useful for comparing datasets or analyzing changes over time.
        
        Args:
            file1_stats: Statistics dictionary for the first file.
            file2_stats: Statistics dictionary for the second file.
            
        Returns:
            Dictionary containing comparison metrics:
            - Line count comparison and differences
            - Average length comparison and differences
            - Average words comparison and differences
            
        Example:
            Compare two text files:
            
            >>> analyzer = TextStatistics()
            >>> stats1 = analyzer.analyze_file(Path("file1.txt"))
            >>> stats2 = analyzer.analyze_file(Path("file2.txt"))
            >>> comparison = analyzer.compare_files(stats1, stats2)
            >>> print(f"Line difference: {comparison['lines_difference']}")
        """
        comparison = {
            "file1_lines": file1_stats["total_lines"],
            "file2_lines": file2_stats["total_lines"],
            "lines_difference": file2_stats["total_lines"] - file1_stats["total_lines"],
            "file1_avg_length": file1_stats["average_length"],
            "file2_avg_length": file2_stats["average_length"],
            "avg_length_difference": round(file2_stats["average_length"] - file1_stats["average_length"], 2),
            "file1_avg_words": file1_stats["average_words"],
            "file2_avg_words": file2_stats["average_words"],
            "avg_words_difference": round(file2_stats["average_words"] - file1_stats["average_words"], 2)
        }
        
        return comparison