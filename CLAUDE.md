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
- `process_files()` - Utility function for file batch processing
**Usage Examples**:

```python
# Clean unified interfaces
from cream import AudioProcessor, TextProcessor

# Single interface for all audio operations
audio_processor = AudioProcessor(method="audio_separator_vr")
result = audio_processor.process_file(input_path, output_path)

# Works with any audio processing method
enhancer = AudioProcessor(method="frcrn_enhancer")
enhanced = enhancer.process_file(input_path, output_path)

# Single interface for all text operations  
text_processor = TextProcessor(method="basic_text_normalizer")
normalized = text_processor.process_file(input_path, output_path)

# Works with any text processing method
translator = TextProcessor(method="text_translator")
translated = translator.process_file(input_path, output_path)

# List all available methods by category
audio_methods = AudioProcessor.list_all_methods()
print(audio_methods["separation"])      # ["audio_separator_vr", "audio_separator_mdx", "spleeter"]
print(audio_methods["enhancement"])     # ["frcrn_enhancer", "deepfilternet_enhancer"]
print(audio_methods["basic_processing"]) # ["audio_resampler", "audio_normalizer", "audio_segmenter"]
print(audio_methods["analysis"])        # ["mos_evaluator", "intelligibility_evaluator", ...]

text_methods = TextProcessor.list_all_methods()
print(text_methods["normalization"])    # ["basic_text_normalizer", "chinese_text_normalizer", ...]
print(text_methods["processing"])       # ["text_translator", "text_summarizer", "text_cleaner"]
print(text_methods["analysis"])         # ["text_statistics_analyzer", "language_detector", ...]
```

**Template Implementation**: All processors are template implementations that raise `AudioProcessingError` or `CreamError`. Replace with actual model integration code.

**Configuration**: Default num_workers is 1, progress bars are mandatory. Configuration can be updated through `config.set_parallel_config()`.

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

# List available methods grouped by category
python -m cream audio list-methods
python -m cream text list-methods
```

### Adding New Processors

To add a new processor implementation:

1. **Create processor class** inheriting from `AudioProcessor` or `TextProcessor`
2. **Implement `process_single` method** with your algorithm
3. **Register the processor** using `processor_registry.register(name, class)`
4. **Import in `processors/__init__.py`** to trigger registration

Example:
```python
from cream.core.processor import AudioProcessor, processor_registry

class MyCustomProcessor(AudioProcessor):
    def process_single(self, input_path, output_path=None, **kwargs):
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
