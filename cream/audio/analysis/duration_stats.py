"""Audio duration statistics analysis."""

from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError
from cream.core.logging import get_logger

logger = get_logger(__name__)


class DurationAnalyzer:
    """Audio duration statistics analyzer."""
    
    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers or config.max_workers
    
    def get_duration(self, audio_path: Path) -> float:
        """Get duration of an audio file in seconds."""
        if not config.is_audio_file(audio_path):
            logger.error(f"Unsupported audio format for duration analysis: {audio_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {audio_path.suffix}")
        
        try:
            # Placeholder for actual duration extraction
            # In real implementation, this would use librosa, pydub, or ffprobe
            logger.info(f"Getting duration for {audio_path}")
            
            # Mock duration based on file size (very rough approximation)
            import random
            random.seed(hash(str(audio_path)) % 2147483647)
            mock_duration = random.uniform(5.0, 120.0)  # 5 seconds to 2 minutes
            
            return round(mock_duration, 2)
            
        except Exception as e:
            logger.exception(f"Failed to get duration for {audio_path}")
            raise AudioProcessingError(f"Failed to get duration for {audio_path}: {str(e)}")
    
    def analyze_directory(self, input_dir: Path) -> dict[str, float | int | dict]:
        """Analyze duration statistics for all audio files in directory."""
        if not input_dir.exists():
            logger.error(f"Input directory not found for duration analysis: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            logger.error(f"No audio files found for duration analysis in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        # Get durations
        durations = {}
        
        def process_file(audio_file):
            duration = self.get_duration(audio_file)
            return audio_file.name, duration
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, duration = future.result()
                durations[file_name] = duration
        
        # Calculate statistics
        duration_values = list(durations.values())
        total_duration = sum(duration_values)
        average_duration = total_duration / len(duration_values)
        min_duration = min(duration_values)
        max_duration = max(duration_values)
        
        # Calculate percentiles
        sorted_durations = sorted(duration_values)
        n = len(sorted_durations)
        
        def get_percentile(percentile):
            index = (percentile / 100) * (n - 1)
            if index.is_integer():
                return sorted_durations[int(index)]
            else:
                lower_index = int(index)
                upper_index = lower_index + 1
                weight = index - lower_index
                return sorted_durations[lower_index] * (1 - weight) + sorted_durations[upper_index] * weight
        
        # Duration distribution (bins)
        bins = [0, 10, 30, 60, 120, 300, float('inf')]
        bin_labels = ['0-10s', '10-30s', '30-60s', '1-2min', '2-5min', '5min+']
        distribution = {label: 0 for label in bin_labels}
        
        for duration in duration_values:
            for i, (bin_start, bin_end) in enumerate(zip(bins[:-1], bins[1:])):
                if bin_start <= duration < bin_end:
                    distribution[bin_labels[i]] += 1
                    break
        
        statistics = {
            "total_files": len(audio_files),
            "total_duration": round(total_duration, 2),
            "total_duration_hours": round(total_duration / 3600, 2),
            "average_duration": round(average_duration, 2),
            "min_duration": round(min_duration, 2),
            "max_duration": round(max_duration, 2),
            "median_duration": round(get_percentile(50), 2),
            "percentiles": {
                "25th": round(get_percentile(25), 2),
                "50th": round(get_percentile(50), 2),
                "75th": round(get_percentile(75), 2),
                "90th": round(get_percentile(90), 2),
                "95th": round(get_percentile(95), 2)
            },
            "duration_distribution": distribution,
            "file_durations": durations
        }
        
        return statistics
    
    def generate_report(self, statistics: dict[str, float | int | dict]) -> str:
        """Generate a formatted report from statistics."""
        report_lines = [
            "Audio Duration Analysis Report",
            "=" * 35,
            "",
            f"Total Files: {statistics['total_files']}",
            f"Total Duration: {statistics['total_duration']} seconds ({statistics['total_duration_hours']} hours)",
            f"Average Duration: {statistics['average_duration']} seconds",
            f"Min Duration: {statistics['min_duration']} seconds",
            f"Max Duration: {statistics['max_duration']} seconds",
            f"Median Duration: {statistics['median_duration']} seconds",
            "",
            "Percentiles:",
            f"  25th: {statistics['percentiles']['25th']} seconds",
            f"  50th: {statistics['percentiles']['50th']} seconds",
            f"  75th: {statistics['percentiles']['75th']} seconds",
            f"  90th: {statistics['percentiles']['90th']} seconds",
            f"  95th: {statistics['percentiles']['95th']} seconds",
            "",
            "Duration Distribution:",
        ]
        
        for duration_range, count in statistics['duration_distribution'].items():
            percentage = (count / statistics['total_files']) * 100
            report_lines.append(f"  {duration_range}: {count} files ({percentage:.1f}%)")
        
        return "\n".join(report_lines)