"""Speaker similarity and clustering functionality using 3D-Speaker models.

This module provides comprehensive speaker similarity analysis and clustering
using various models from the 3D-Speaker toolkit, including CAM++ and ERes2NetV2
architectures for high-quality speaker embedding extraction.

The module now uses a factory pattern for extensible speaker model management,
allowing easy addition of new speaker recognition models.

Example:
    Basic usage for speaker analysis:
    
    >>> from pathlib import Path
    >>> from cream.audio.analysis.similarity import SpeakerAnalyzer
    >>> 
    >>> analyzer = SpeakerAnalyzer(max_workers=4)
    >>> 
    >>> # Extract embedding using CAM++ model
    >>> embedding = analyzer.extract_embedding(
    ...     Path("speaker.wav"),
    ...     model="3d-speaker-cam++"
    ... )
    >>> 
    >>> # Compare two speakers using ERes2NetV2
    >>> result = analyzer.compare_speakers(
    ...     Path("speaker1.wav"),
    ...     Path("speaker2.wav"),
    ...     model="3d-speaker-eres2netv2"
    ... )
    >>> print(f"Similarity: {result['similarity']}")

Classes:
    SpeakerAnalyzer: Main class for speaker similarity analysis and clustering.
"""

from pathlib import Path
import numpy as np

from cream.core.config import config
from cream.core.exceptions import AudioProcessingError, InvalidFormatError, ModelNotAvailableError
from cream.core.logging import get_logger
from cream.core.model_factory import speaker_factory

logger = get_logger(__name__)


class SpeakerAnalyzer:
    """Speaker similarity analyzer and clustering processor using multiple models.
    
    This class provides functionality for speaker embedding extraction, similarity
    calculation, and clustering using various models from the 3D-Speaker toolkit
    including CAM++ and ERes2NetV2 architectures.
    
    The processor supports both single file processing and batch directory processing
    with configurable multi-threading for efficient parallel processing.
    
    Attributes:
        available_models: List of available speaker model names.
        default_model: Default speaker model if none specified.
    
    Example:
        Creating and using a speaker analyzer:
        
        >>> analyzer = SpeakerAnalyzer()
        >>> 
        >>> # Extract embeddings using CAM++ model
        >>> embedding = analyzer.extract_embedding(
        ...     Path("audio.wav"),
        ...     model="3d-speaker-cam++"
        ... )
        >>> 
        >>> # Perform speaker clustering
        >>> embeddings = {
        ...     "file1.wav": embedding1,
        ...     "file2.wav": embedding2,
        ...     "file3.wav": embedding3
        ... }
        >>> clusters = analyzer.cluster_speakers(embeddings, threshold=0.7)
    """
    
    def __init__(self) -> None:
        """Initialize the speaker analyzer."""
        self._model_instances = {}
        self.available_models = speaker_factory.list_models()
        
        if not self.available_models:
            logger.warning(
                "No speaker models are available. Check model configuration."
            )
        else:
            logger.info(f"Available speaker models: {self.available_models}")
        
        self.default_model = (
            self.available_models[0] if self.available_models else None
        )
    
    def _get_model(self, model_name: str):
        """Get or create speaker model instance for the specified model.
        
        Args:
            model_name: Name of the speaker model.
            
        Returns:
            Model instance ready for embedding extraction.
            
        Raises:
            ModelNotAvailableError: If the model is not available or fails to load.
        """
        if model_name in self._model_instances:
            return self._model_instances[model_name]

        # Get model configuration from config
        model_config = config.get_model_config("speaker", model_name)
        if not model_config and model_name not in self.available_models:
            # If not in config, create default config for factory models
            model_config = {"enabled": True}
        
        if not model_config.get("enabled", True):
            raise ModelNotAvailableError(
                f"Speaker model {model_name} is not enabled"
            )

        try:
            # Create model using factory
            model = speaker_factory.create_model(model_name, model_config)
            self._model_instances[model_name] = model
            logger.info(f"Created speaker model: {model_name}")
            return model

        except Exception as e:
            logger.exception(f"Failed to create speaker model {model_name}")
            raise ModelNotAvailableError(
                f"Failed to create speaker model {model_name}: {str(e)}"
            )
    
    def extract_embedding(self, audio_path: Path, model: str | None = None) -> list[float]:
        """Extract speaker embedding from audio file.
        
        Args:
            audio_path: Path to the input audio file.
            model: Speaker model name to use for extraction (optional).
            
        Returns:
            List of floats representing the speaker embedding vector.
            
        Raises:
            InvalidFormatError: If audio file format is not supported.
            ModelNotAvailableError: If the specified model is not available.
            AudioProcessingError: If embedding extraction fails.
        """
        if not config.is_audio_file(audio_path):
            logger.error(f"Unsupported audio format for speaker analysis: {audio_path.suffix}")
            raise InvalidFormatError(f"Unsupported audio format: {audio_path.suffix}")
        
        # Use default model if none specified and available
        if not model and self.default_model:
            model = self.default_model
            logger.info(f"Using default speaker model: {model}")
        
        # Check if model is available
        if model not in self.available_models:
            logger.error(f"Speaker model {model} is not available")
            raise ModelNotAvailableError(f"Speaker model {model} is not available")
        
        try:
            # Get model instance and extract embedding
            speaker_model = self._get_model(model)
            
            logger.info(f"Extracting speaker embedding for {audio_path} using {model}")
            
            # Extract embedding using the model
            if not speaker_model.is_loaded:
                speaker_model.load()
            embedding = speaker_model.extract_embedding(audio_path)
            
            logger.info(f"Successfully extracted {len(embedding)}-dimensional embedding")
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
                        method: str = "agglomerative", threshold: float = 0.7, 
                        n_clusters: int | None = None) -> dict[str, int]:
        """Cluster speakers based on embedding similarities.
        
        Args:
            embeddings: Dictionary mapping filenames to embedding vectors.
            method: Clustering method ("agglomerative", "threshold").
            threshold: Similarity threshold for clustering (used with threshold method).
            n_clusters: Number of clusters (used with agglomerative method).
            
        Returns:
            Dictionary mapping filenames to cluster IDs.
            
        Raises:
            AudioProcessingError: If clustering fails.
        """
        if not embeddings:
            logger.warning("No embeddings provided for clustering")
            return {}
        
        try:
            filenames = list(embeddings.keys())
            embedding_matrix = np.array(list(embeddings.values()))
            
            if method == "agglomerative":
                return self._cluster_agglomerative(filenames, embedding_matrix, 
                                                 n_clusters, threshold)
            elif method == "threshold":
                return self._cluster_threshold(embeddings, threshold)
            else:
                raise ValueError(f"Unknown clustering method: {method}")
            
        except Exception as e:
            logger.exception("Failed to cluster speakers")
            raise AudioProcessingError(f"Failed to cluster speakers: {str(e)}")
    
    def _cluster_agglomerative(self, filenames: list[str], embeddings: np.ndarray, 
                              n_clusters: int | None, threshold: float) -> dict[str, int]:
        """Perform agglomerative clustering."""
        try:
            from sklearn.cluster import AgglomerativeClustering
            
            # Use distance_threshold if n_clusters is not specified
            if n_clusters is None:
                distance_threshold = 1.0 - threshold  # Convert similarity to distance
                clustering = AgglomerativeClustering(
                    distance_threshold=distance_threshold,
                    n_clusters=None,
                    linkage='average',
                    metric='cosine'
                )
            else:
                clustering = AgglomerativeClustering(
                    n_clusters=n_clusters,
                    linkage='average',
                    metric='cosine'
                )
            
            cluster_labels = clustering.fit_predict(embeddings)
            
            # Create filename to cluster mapping
            clusters = {}
            for filename, cluster_id in zip(filenames, cluster_labels):
                clusters[filename] = int(cluster_id)
            
            n_clusters_found = len(set(cluster_labels))
            logger.info(f"Agglomerative clustering found {n_clusters_found} clusters")
            
            return clusters
            
        except ImportError:
            logger.error("scikit-learn not installed. Install with: pip install scikit-learn")
            raise AudioProcessingError("scikit-learn required for agglomerative clustering")
        except Exception as e:
            logger.exception("Agglomerative clustering failed")
            raise AudioProcessingError(f"Agglomerative clustering failed: {str(e)}")
    
    def _cluster_threshold(self, embeddings: dict[str, list[float]], threshold: float) -> dict[str, int]:
        """Simple threshold-based clustering."""
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
        
        n_clusters_found = len(cluster_centers)
        logger.info(f"Threshold clustering found {n_clusters_found} clusters")
        
        return clusters
    
    def compare_speakers(self, file1: Path, file2: Path, model: str | None = None) -> dict[str, str | float]:
        """Compare similarity between two audio files.
        
        Args:
            file1: Path to the first audio file.
            file2: Path to the second audio file.
            model: Speaker model name to use for comparison (optional).
            
        Returns:
            Dictionary containing comparison results with keys:
            - file1: First file name
            - file2: Second file name
            - similarity: Cosine similarity score
            - same_speaker_likelihood: Likelihood assessment
            - model: Model used for comparison
            
        Raises:
            AudioProcessingError: If comparison fails.
        """
        try:
            embedding1 = self.extract_embedding(file1, model)
            embedding2 = self.extract_embedding(file2, model)
            
            similarity = self.calculate_similarity(embedding1, embedding2)
            
            # Use the model name from the first extraction
            model_used = model or self.default_model
            
            return {
                "file1": file1.name,
                "file2": file2.name,
                "similarity": round(similarity, 3),
                "same_speaker_likelihood": "High" if similarity > 0.8 else "Medium" if similarity > 0.6 else "Low",
                "model": model_used
            }
            
        except Exception as e:
            logger.exception(f"Failed to compare speakers: {file1} vs {file2}")
            raise AudioProcessingError(f"Speaker comparison failed: {str(e)}")
    
    def analyze_directory(self, input_dir: Path, model: str | None = None, 
                         cluster: bool = True, clustering_method: str = "agglomerative",
                         threshold: float = 0.7) -> dict[str, dict]:
        """Analyze speaker similarity for all audio files in a directory.
        
        Args:
            input_dir: Path to the input directory containing audio files.
            model: Speaker model name to use for analysis (optional).
            cluster: Whether to perform speaker clustering.
            clustering_method: Clustering method ("agglomerative", "threshold").
            threshold: Similarity threshold for clustering.
            
        Returns:
            Dictionary containing analysis results including embeddings and clusters.
            
        Raises:
            FileNotFoundError: If the input directory does not exist.
            AudioProcessingError: If no audio files are found or processing fails.
        """
        if not input_dir.exists():
            logger.error(f"Input directory not found: {input_dir}")
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Find all audio files
        audio_files = []
        for path in input_dir.rglob("*"):
            if path.is_file() and config.is_audio_file(path):
                audio_files.append(path)
        
        if not audio_files:
            logger.error(f"No audio files found in {input_dir}")
            raise AudioProcessingError(f"No audio files found in {input_dir}")
        
        embeddings = {}
        
        def process_file(audio_file: Path) -> tuple[str, list[float] | None]:
            """Process a single audio file."""
            try:
                embedding = self.extract_embedding(audio_file, model)
                return audio_file.name, embedding
            except Exception as e:
                logger.error(f"Failed to extract embedding for {audio_file}: {str(e)}")
                return audio_file.name, None
        
        # Process files sequentially
        for audio_file in audio_files:
            try:
                embedding = self.extract_embedding(audio_file, model)
                if embedding is not None:
                    embeddings[audio_file.name] = embedding
            except Exception as e:
                logger.error(f"Failed to extract embedding for {audio_file}: {str(e)}")
        
        results = {
            "embeddings": embeddings,
            "model": model or self.default_model,
            "total_files": len(audio_files),
            "successful_extractions": len(embeddings)
        }
        
        # Perform clustering if requested and we have embeddings
        if cluster and len(embeddings) > 1:
            try:
                clusters = self.cluster_speakers(embeddings, clustering_method, threshold)
                results["clusters"] = clusters
                results["num_clusters"] = len(set(clusters.values()))
                logger.info(f"Found {results['num_clusters']} speaker clusters")
            except Exception as e:
                logger.error(f"Clustering failed: {str(e)}")
                results["clustering_error"] = str(e)
        
        successful = len(embeddings)
        logger.info(f"Processed {len(audio_files)} files, {successful} successful embeddings")
        return results