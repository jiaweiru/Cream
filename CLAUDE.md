# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cream is an audio and text processing toolkit that provides comprehensive tools for audio analysis, processing, and manipulation. It's built as a Python package with a CLI interface using Typer and Rich for enhanced console output.

## CLI Usage

The main entry point is through the `cream` CLI command:

```bash
python3 -m cream --help
python3 -m cream audio --help
python3 -m cream text --help
python3 -m cream utils --help
```

Main command structure:
- `cream audio` - Audio processing and analysis commands
- `cream text` - Text processing commands  
- `cream utils` - Utility commands

Global options:
- `--version, -v` - Show version information
- `--log-level, -l` - Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file` - Path to log file
- `--no-color` - Disable colored console output

## Core Architecture

### New Unified Processing Framework

Cream now uses a unified processing framework that decouples analysis/processing logic from specific implementations:

**Core Features**:
- **Processor Registry**: Centralized registration system for all processors
- **Base Classes**: `BaseProcessor`, `AudioProcessor`, `TextProcessor` provide common interface
- **Parallel Processing**: Integrated multiprocessing with progress bars using `Pool.imap`
- **Configuration Management**: Unified config system with processor-specific settings
- **Extensible Design**: Easy to add new processors and algorithms

**Key Classes**:
- `BaseProcessor` - Abstract base class for all processors
- `AudioProcessor` - Base class for audio processors with format validation
- `TextProcessor` - Base class for text processors with format validation
- `ProcessorRegistry` - Registry for managing processor implementations
- `ParallelProcessor` - Simple parallel processor with progress bars
**Usage Examples**:

```python
# Clean unified interfaces
from cream.audio.audio_processor import AudioProcessorInterface
from cream.text.text_processor import TextProcessorInterface

# Single interface for all audio operations
audio_processor = AudioProcessorInterface(method="audio_separator_vr")
result = audio_processor.process_file(input_path, output_path)

# Works with any audio processing method
enhancer = AudioProcessorInterface(method="frcrn_enhancer")
enhanced = enhancer.process_file(input_path, output_path)

# Single interface for all text operations  
text_processor = TextProcessorInterface(method="basic_text_normalizer")
normalized = text_processor.process_file(input_path, output_path)

# Works with any text processing method
translator = TextProcessorInterface(method="text_translator")
translated = translator.process_file(input_path, output_path)

# List all available methods (simplified - no categories)
audio_methods = AudioProcessorInterface.list_all_methods()
print(audio_methods)  # ["audio_separator_vr", "frcrn_enhancer", "audio_resampler", "mos_evaluator", ...]

text_methods = TextProcessorInterface.list_all_methods()
print(text_methods)   # ["basic_text_normalizer", "text_translator", "text_statistics_analyzer", ...]

# Batch processing with parallel support
audio_processor.process_batch(
    input_files=[Path("file1.wav"), Path("file2.wav")],
    output_dir=Path("output/"),
    num_workers=4
)
```

**Key Features**:
- **Template Implementation**: All processors are template implementations that raise `AudioProcessingError` or `TextProcessingError`. Replace with actual model integration code.
- **Modern Type Annotations**: Uses Python 3.10+ union syntax (`int | None`) for better type safety
- **Centralized Configuration**: File format support and settings managed through `config` module
- **Error Logging**: All exceptions are logged before being raised for better debugging
- **Simplified API**: `list_all_methods()` returns a simple list instead of categorized dict for better extensibility

**Configuration**: 
- Default num_workers is 1, progress bars are mandatory
- File format support: Audio formats (`.wav`, `.flac`, `.mp3`, `.ogg`, `.opus`, `.m4a`, `.aiff`, `.ac3`, `.wma`) and text formats (`.txt`, `.csv`, `.srt`, `.vtt`, `.json`) are centrally managed in `config.py`
- Configuration can be updated through `config.set_parallel_config()`
- Supported formats are dynamically loaded from config using `@property` decorators

### Simplified Package Structure

```
cream/
├── core/                    # Core framework
│   ├── processor.py        # Base processor classes and registry
│   ├── parallel.py         # Parallel processing with progress bars
│   ├── config.py           # Configuration management
│   ├── exceptions.py       # Custom exceptions
│   └── logging.py          # Logging setup
├── audio/                  # Audio processing
│   ├── audio_processor.py  # Unified audio interface
│   ├── processing.py       # Audio processing templates (separation, enhancement, basic)
│   └── analysis.py         # Audio analysis templates  
├── text/                   # Text processing
│   ├── text_processor.py   # Unified text interface
│   ├── processing.py       # Text processing templates (normalization, translation, etc.)
│   └── analysis.py         # Text analysis templates
├── cli/                    # Command line interface
│   ├── main.py            # Main CLI entry point
│   ├── audio.py           # Audio CLI commands
│   ├── text.py            # Text CLI commands
│   └── utils.py           # Utility CLI commands
└── utils/                  # Utilities
    ├── file_ops.py        # File operations
    ├── indexing.py        # Index matching
    └── progress.py        # Progress bar utilities
### CLI Usage

```bash
# Clean unified processing commands
python -m cream audio process input.wav audio_separator_vr --output output_dir
python -m cream audio process input.wav frcrn_enhancer --output enhanced.wav
python -m cream audio process input.wav mos_evaluator

python -m cream text process input.txt basic_text_normalizer --output output.txt
python -m cream text process input.txt text_translator --output translated.txt
python -m cream text process input.txt text_statistics_analyzer

# List available methods (all methods in a single list)
python -m cream audio list-methods
python -m cream text list-methods
```

### Adding New Processors

To add a new processor implementation:

1. **Create processor class** inheriting from `BaseAudioProcessor` or `BaseTextProcessor`
2. **Implement `process_single` method** with your algorithm
3. **Register using decorator** - much cleaner than manual registration!
4. **Import in processing/analysis modules** to trigger registration

**Recommended approach using decorator:**
```python
from pathlib import Path
from cream.core.processor import register_processor
from cream.audio.audio_processor import BaseAudioProcessor

@register_processor("my_custom_processor")
class MyCustomProcessor(BaseAudioProcessor):
    def process_single(self, input_path: Path, output_path: Path | None = None, **kwargs):
        """Custom audio processing implementation."""
        self.validate_input(input_path)
        
        try:
            # Your implementation here
            result = your_custom_logic(input_path, output_path, **kwargs)
            return result
        except Exception as e:
            error_msg = f"Custom processor failed: {str(e)}"
            self.logger.error(error_msg)
            raise AudioProcessingError(error_msg)
```

**Alternative manual registration (if needed):**
```python
from cream.core.processor import processor_registry
from cream.audio.audio_processor import BaseAudioProcessor

class MyCustomProcessor(BaseAudioProcessor):
    def process_single(self, input_path: Path, output_path: Path | None = None, **kwargs):
        # Your implementation here
        pass

processor_registry.register("my_custom_processor", MyCustomProcessor)
```

## Summary

Cream is now a clean, extensible framework for audio and text processing:

- **Simplified Architecture**: Removed complex factory patterns and legacy code
- **Template-Based**: All specific implementations are templates waiting for your code
- **Unified Interface**: Single entry point for each processing type
- **Easy Extension**: Add new processors by inheriting base classes
- **CLI Support**: Simple commands for all processing operations
- **Progress Tracking**: Mandatory progress bars for better UX
