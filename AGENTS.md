# AGENTS Guidelines

These guidelines apply to the entire repository.

- Keep changes minimal and focused. Do not add features beyond the explicit task.
- Prefer small, surgical fixes over broad refactors. Maintain existing public APIs.
- Follow the current code style: standard Python typing, dataclasses, and simple modules.
- Use the global processor registry for method discovery and registration:
  - Register processors via `from cream.core.processor import register_processor`.
  - Decorate classes with `@register_processor("unique_name")`.
- Processors should subclass the appropriate base class:
  - Audio: `cream.audio.audio_processor.BaseAudioProcessor`
  - Text: `cream.text.text_processor.BaseTextProcessor`
  - Generic: `cream.core.processor.BaseProcessor` or `ModelBackedProcessor`
- Validation: reuse `BaseProcessor.validate_input` and domain-specific validation in base classes.
- Parallelism: use `cream.core.parallel.ParallelProcessor` and `config.max_workers`.
- Logging: use `cream.core.logging.get_logger()` and avoid printing directly.
- Progress: use `cream.core.progress.create_progress` and honor `config.enable_progress_bars`.
- CLI: Typer apps live under `cream/cli`. Keep commands thin; delegate to processors.
- Configuration: read from `cream.core.config.config`; update via CLI flags only.

When updating files:

- Mind imports used for side effects (e.g., importing `analysis`/`processing` submodules to trigger registrations).
- Avoid adding global caches or singletons beyond `config` and the registry provided.
- If adding a new processor, include a clear error message for unimplemented parts instead of stubs that silently pass.
