"""Model factory for creating and managing various AI models.

This module provides factory classes for creating and managing different types of AI models
used throughout the cream package. It supports extensible model registration and provides
a unified interface for model lifecycle management.

The factory pattern allows for easy addition of new models without modifying existing code,
supporting both lazy loading and eager loading strategies based on configuration.

Example:
    Basic usage of model factories:
    
    >>> from cream.core.model_factory import SeparationModelFactory
    >>> factory = SeparationModelFactory()
    >>> model = factory.create_model("audio-separator-vr", model_config)
    >>> result = model.separate(audio_path)

Classes:
    BaseModelFactory: Abstract base class for all model factories.
    SeparationModelFactory: Factory for audio separation models.
    EnhancementModelFactory: Factory for audio enhancement models.
    ASRModelFactory: Factory for ASR models.
    VADModelFactory: Factory for VAD models.
    SpeakerModelFactory: Factory for speaker recognition models.
"""

from abc import ABC, abstractmethod

from cream.core.exceptions import ModelNotAvailableError
from cream.core.logging import get_logger

logger = get_logger(__name__)


class BaseModel(ABC):
    """Base class for all AI models.
    
    This abstract class defines the common interface that all AI models
    must implement. It provides basic lifecycle management and configuration
    handling capabilities.
    
    Args:
        model_config: Configuration dictionary for the model.
        
    Attributes:
        config: Model configuration dictionary.
        is_loaded: Whether the model is currently loaded.
    """
    
    def __init__(self, model_config: dict[str, str | int | float | bool | list]) -> None:
        """Initialize the base model.
        
        Args:
            model_config: Configuration dictionary containing model parameters.
        """
        self.config = model_config
        self.is_loaded = False
    
    @abstractmethod
    def load(self) -> None:
        """Load the model into memory.
        
        This method should be implemented by each specific model type to handle
        the loading of model weights and initialization of inference components.
        
        Raises:
            ModelNotAvailableError: If the model cannot be loaded.
        """
        pass
    
    def unload(self) -> None:
        """Unload the model from memory.
        
        Default implementation does nothing as most external models
        handle resource cleanup automatically. Override if needed.
        """
        pass
    


class BaseModelFactory(ABC):
    """Abstract base class for all model factories.
    
    This class provides the foundation for creating specific model factories
    that handle different types of AI models. Each factory is responsible
    for model creation, registration, and lifecycle management.
    
    Attributes:
        _model_registry: Dictionary mapping model names to model classes.
    """
    
    def __init__(self) -> None:
        """Initialize the base model factory."""
        self._model_registry: dict[str, type] = {}
        self._register_default_models()
    
    @abstractmethod
    def _register_default_models(self) -> None:
        """Register default models for this factory.
        
        This method should be implemented by each specific factory to register
        the default set of models that it can create.
        """
        pass
    
    def register_model(self, name: str, model_class: type) -> None:
        """Register a new model class with the factory.
        
        Args:
            name: Unique name for the model.
            model_class: Class that implements the model interface.
        """
        self._model_registry[name] = model_class
        logger.info(f"Registered model '{name}' in {self.__class__.__name__}")
    
    def create_model(self, model_name: str, model_config: dict[str, str | int | float | bool | list]) -> BaseModel:
        """Create a model instance.
        
        Args:
            model_name: Name of the model to create.
            model_config: Configuration dictionary for the model.
            
        Returns:
            Instance of the requested model.
            
        Raises:
            ModelNotAvailableError: If the model is not registered or available.
        """
        if model_name not in self._model_registry:
            available_models = list(self._model_registry.keys())
            raise ModelNotAvailableError(
                f"Model '{model_name}' not found. Available models: {available_models}"
            )
        
        model_class = self._model_registry[model_name]
        try:
            return model_class(model_config)
        except Exception as e:
            logger.exception(f"Failed to create model '{model_name}'")
            raise ModelNotAvailableError(f"Failed to create model '{model_name}': {str(e)}")
    
    def list_models(self) -> list[str]:
        """Get list of registered model names.
        
        Returns:
            List of available model names.
        """
        return list(self._model_registry.keys())


class SeparationModelFactory(BaseModelFactory):
    """Factory for audio separation models.
    
    This factory manages creation and registration of audio separation models
    including python-audio-separator models and other separation systems.
    
    Example:
        Creating separation models:
        
        >>> factory = SeparationModelFactory()
        >>> model = factory.create_model("audio-separator-vr", config)
    """
    
    def _register_default_models(self) -> None:
        """Register default separation models."""
        from cream.audio.models.separation import (
            AudioSeparatorVRModel,
            AudioSeparatorMDXModel,
            AudioSeparatorHTDemucsModel,
        )
        
        self.register_model("audio-separator-vr", AudioSeparatorVRModel)
        self.register_model("audio-separator-mdx", AudioSeparatorMDXModel)
        self.register_model("audio-separator-htdemucs", AudioSeparatorHTDemucsModel)


class EnhancementModelFactory(BaseModelFactory):
    """Factory for audio enhancement models.
    
    This factory manages creation and registration of audio enhancement models
    including ClearerVoice-Studio models and other enhancement systems.
    
    Example:
        Creating enhancement models:
        
        >>> factory = EnhancementModelFactory()
        >>> model = factory.create_model("frcrn", config)
    """
    
    def _register_default_models(self) -> None:
        """Register default enhancement models."""
        from cream.audio.models.enhancement import FRCRNModel
        
        self.register_model("frcrn", FRCRNModel)


class ASRModelFactory(BaseModelFactory):
    """Factory for ASR models.
    
    This factory manages creation and registration of Automatic Speech Recognition
    models including FunASR Paraformer models and other ASR systems.
    
    Example:
        Creating ASR models:
        
        >>> factory = ASRModelFactory()
        >>> model = factory.create_model("paraformer-zh", config)
    """
    
    def _register_default_models(self) -> None:
        """Register default ASR models."""
        from cream.audio.models.asr import ParaformerZhModel
        
        self.register_model("paraformer-zh", ParaformerZhModel)


class VADModelFactory(BaseModelFactory):
    """Factory for VAD models.
    
    This factory manages creation and registration of Voice Activity Detection
    models including FunASR VAD models and other VAD systems.
    
    Example:
        Creating VAD models:
        
        >>> factory = VADModelFactory()
        >>> model = factory.create_model("funasr-vad", config)
    """
    
    def _register_default_models(self) -> None:
        """Register default VAD models."""
        from cream.audio.models.vad import FunASRVADModel
        
        self.register_model("funasr-vad", FunASRVADModel)


class SpeakerModelFactory(BaseModelFactory):
    """Factory for speaker recognition models.
    
    This factory manages creation and registration of speaker recognition models
    including 3D-Speaker cam++ and ERes2NetV2 models.
    
    Example:
        Creating speaker models:
        
        >>> factory = SpeakerModelFactory()
        >>> model = factory.create_model("3d-speaker-cam++", config)
    """
    
    def _register_default_models(self) -> None:
        """Register default speaker models."""
        from cream.audio.models.speaker import (
            Speaker3DCamPlusPlusModel,
            Speaker3DERes2NetV2Model,
        )
        
        self.register_model("3d-speaker-cam++", Speaker3DCamPlusPlusModel)
        self.register_model("3d-speaker-eres2netv2", Speaker3DERes2NetV2Model)


# Global factory instances
separation_factory = SeparationModelFactory()
enhancement_factory = EnhancementModelFactory()
asr_factory = ASRModelFactory()
vad_factory = VADModelFactory()
speaker_factory = SpeakerModelFactory()