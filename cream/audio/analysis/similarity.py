"""Speaker similarity and clustering functionality using 3D-Speaker."""

from pathlib import Path
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError
from cream.core.logging import get_logger

logger = get_logger(__name__)


class SpeakerAnalyzer:
    """Speaker similarity analyzer and clustering processor."""
    
    def __init__(self, max_workers: int | None = None):
        self.max_workers = max_workers or config.max_workers
    
    def extract_embedding(self, audio_path: Path) -> list[float]:
        """Extract speaker embedding from audio file."""
        if not config.is_audio_file(audio_path):
            logger.error(f"Unsupported audio format for speaker analysis: {audio_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {audio_path.suffix}")
        
        model_config = config.get_model_config("speaker", "3d-speaker")
        if not model_config.get("enabled", False):
            logger.error("3D-Speaker model is not available")
            raise ModelNotAvailableError("3D-Speaker model is not available")
        
        try:
            # Placeholder for actual speaker embedding extraction
            # In real implementation, this would use 3D-Speaker library
            logger.info(f"Extracting speaker embedding for {audio_path}")
            
            # Mock embedding vector (256-dimensional)
            import random
            random.seed(hash(str(audio_path)) % 2147483647)
            embedding = [random.uniform(-1, 1) for _ in range(256)]
            
            return embedding
            
        except Exception as e:
            logger.exception(f"Failed to extract embedding for {audio_path}")
            raise AudioProcessingError(f"Failed to extract embedding for {audio_path}: {str(e)}")
    
    def calculate_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            # Simple cosine similarity calculation
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            magnitude1 = sum(a ** 2 for a in embedding1) ** 0.5
            magnitude2 = sum(a ** 2 for a in embedding2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return max(-1.0, min(1.0, similarity))  # Clamp to [-1, 1]
            
        except Exception as e:
            logger.exception("Failed to calculate similarity")
            raise AudioProcessingError(f"Failed to calculate similarity: {str(e)}")
    
    def cluster_speakers(self, embeddings: dict[str, list[float]], 
                        threshold: float = 0.7) -> dict[str, int]:
        """Simple clustering based on similarity threshold."""
        try:
            clusters = {}
            cluster_centers = {}
            next_cluster_id = 0
            
            for filename, embedding in embeddings.items():
                best_cluster = None
                best_similarity = -1
                
                # Find the best matching cluster
                for cluster_id, center in cluster_centers.items():
                    similarity = self.calculate_similarity(embedding, center)
                    if similarity > threshold and similarity > best_similarity:
                        best_similarity = similarity
                        best_cluster = cluster_id
                
                if best_cluster is not None:
                    clusters[filename] = best_cluster
                    # Update cluster center (simple average)
                    old_center = cluster_centers[best_cluster]
                    cluster_size = sum(1 for c in clusters.values() if c == best_cluster)
                    new_center = [(old * (cluster_size - 1) + new) / cluster_size 
                                 for old, new in zip(old_center, embedding)]
                    cluster_centers[best_cluster] = new_center
                else:
                    # Create new cluster
                    clusters[filename] = next_cluster_id
                    cluster_centers[next_cluster_id] = embedding[:]
                    next_cluster_id += 1
            
            return clusters
            
        except Exception as e:
            logger.exception("Failed to cluster speakers")
            raise AudioProcessingError(f"Failed to cluster speakers: {str(e)}")
    
    def analyze_directory(self, input_dir: Path, cluster: bool = False) -> dict[str, int | dict[str, list[float]] | dict[str, int] | dict[str, dict[str, list[str] | int]]]:
        """Analyze speaker similarity for all audio files in directory."""
        if not input_dir.exists():
            logger.error(f"Input directory not found for speaker analysis: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            logger.error(f"No audio files found for speaker analysis in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        # Extract embeddings
        embeddings = {}
        
        def process_file(audio_file):
            embedding = self.extract_embedding(audio_file)
            return audio_file.name, embedding
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(process_file, af): af for af in audio_files}
            
            for future in concurrent.futures.as_completed(future_to_file):
                file_name, embedding = future.result()
                embeddings[file_name] = embedding
        
        results = {
            "total_files": len(audio_files),
            "embeddings": embeddings
        }
        
        if cluster:
            clusters = self.cluster_speakers(embeddings)
            results["clusters"] = clusters
            results["num_speakers"] = len(set(clusters.values()))
            
            # Calculate cluster statistics
            cluster_stats = {}
            for cluster_id in set(clusters.values()):
                cluster_files = [f for f, c in clusters.items() if c == cluster_id]
                cluster_stats[f"speaker_{cluster_id}"] = {
                    "files": cluster_files,
                    "count": len(cluster_files)
                }
            results["cluster_stats"] = cluster_stats
        
        return results
    
    def compare_speakers(self, file1: Path, file2: Path) -> dict[str, str | float]:
        """Compare similarity between two audio files."""
        embedding1 = self.extract_embedding(file1)
        embedding2 = self.extract_embedding(file2)
        
        similarity = self.calculate_similarity(embedding1, embedding2)
        
        return {
            "file1": file1.name,
            "file2": file2.name,
            "similarity": round(similarity, 3),
            "same_speaker_likelihood": "High" if similarity > 0.8 else "Medium" if similarity > 0.6 else "Low"
        }