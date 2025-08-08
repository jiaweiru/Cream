"""Text statistics analysis functionality."""

from pathlib import Path
import json

from cream.core.config import config
from cream.core.exceptions import InvalidFormatError, AudioProcessingError


class TextStatistics:
    """Text length distribution statistics analyzer."""
    
    def analyze_file(self, input_file: Path) -> dict[str, int | float | dict[str, int]]:
        """Analyze text statistics for a single file."""
        if not config.is_text_file(input_file):
            raise InvalidFormatError(f"Unsupported text format: {input_file.suffix}")
        
        if not input_file.exists():
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
            raise AudioProcessingError(f"Failed to analyze text statistics: {str(e)}")
    
    def analyze_directory(self, input_dir: Path, pattern: str = "*.txt") -> dict[str, dict[str, int | float | dict[str, int]]]:
        """Analyze text statistics for all text files in directory."""
        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        text_files = list(input_dir.glob(pattern))
        if not text_files:
            raise AudioProcessingError(f"No text files found in {input_dir} matching pattern {pattern}")
        
        results = {}
        
        for text_file in text_files:
            try:
                stats = self.analyze_file(text_file)
                results[text_file.name] = stats
            except Exception as e:
                print(f"Failed to analyze {text_file}: {str(e)}")
                continue
        
        return results
    
    def generate_summary(self, statistics: dict[str, int | float | dict[str, int]]) -> dict[str, str | dict[str, int | float | dict[str, int]]]:
        """Generate a summary from text statistics."""
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
        """Compare statistics between two files."""
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