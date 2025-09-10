# Repository Guidelines

## Project Structure & Module Organization
- Source lives under `cream/`:
  - `cream/cli/` (Typer CLI entry points), `cream/core/` (config, logging, processor framework),
    `cream/audio/`, `cream/text/` (domain processors), `cream/utils/` (helpers).
- No `tests/` yet — add new tests under `tests/` mirroring package paths (e.g., `tests/core/`, `tests/audio/`).
- Models/config cache in `~/.cream/models` is created on demand by `cream.core.config`.

## Build, Test, and Development Commands
- Environment: managed by Pixi (conda-forge) with Python 3.13.
  - First-time setup: `pixi install`
  - Enter env shell: `pixi shell`
- Run CLI locally:
  - Help: `pixi run python -m cream.cli.main --help`
  - Audio methods: `pixi run python -m cream.cli.audio list-methods`
  - Text process: `pixi run python -m cream.cli.text process input.txt basic_normalization -o out.txt`
- Testing (when added): `pixi run pytest -q` (add `pytest` as a dev dependency first).

## Coding Style & Naming Conventions
- Python with type hints; 4-space indentation; docstrings in triple quotes.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Logging via `cream.core.logging` (`setup`, `get_logger`, `logger`). Do not use `print` in library code; use Rich/console only in CLI.
- Processor registration: use `processor_registry.register_decorator("my_method")` and place implementations in the domain package (`audio/processing.py`, `text/processing.py`, etc.).

Type hints
- Prefer modern built-in generics and unions: use `list[str]`, `dict[str, int]`, `Path | None`.
- Avoid legacy `typing.List/Dict/Optional/Union` forms; rely on Python ≥3.11 syntax (this repo targets 3.13).
- Only use `typing` extras when necessary (e.g., `Literal`, `Protocol`, `TypedDict`).

## Testing Guidelines
- Framework: prefer `pytest` with structure `tests/<area>/test_*.py`.
- Aim for unit tests on processors and CLI smoke tests (e.g., `--help` runs).
- Keep fixtures small; mock filesystem and long-running operations.

## Model-Backed Processors
- Load models in `__init__` to avoid repeated loads. Use the provided base: `cream.core.processor.ModelBackedProcessor`.
- The base caches models by a resolved key (by default `config['model_path']` or class name), so identical models are reused across instances.

Cache key resolution
- Priority: `model_id`[+`model_version`] → `model_name`[+`model_version`] → `model_path` (absolute) → class name.
- Example config: `{"model_id": "whisper-large", "model_version": "v3"}` or `{"model_path": "~/models/mymodel.bin"}`.

Example
```python
from pathlib import Path
from cream.core.processor import ModelBackedProcessor, processor_registry

@processor_registry.register_decorator("my_model_proc")
class MyProcessor(ModelBackedProcessor):
    def load_model(self) -> object:
        # prefer id/name+version; fall back to model_path
        mid = self.config.get("model_id")
        if mid:
            return load_by_id(mid, self.config.get("model_version"))
        path = Path(self.config.get("model_path")).expanduser()
        return load_my_model(path)  # implement actual loader

    def process_single(self, input_path: Path, output_path: Path | None = None, **kwargs):
        model = self.model  # loaded once in __init__
        # ... perform processing ...
```

## Commit & Pull Request Guidelines
- Commits: short imperative subject (<= 72 chars), optional scope, concise body when needed.
  - Example: `core: add ParallelProcessor and batch wrapper`
- PRs: clear description, linked issues, reproduction steps, and before/after CLI examples.
  - Include commands used (e.g., `python -m cream.cli.audio process ...`) and screenshots of Rich output if useful.
- CI/readiness: ensure code runs under `pixi shell`; no unrelated refactors in feature PRs.

## Security & Configuration Tips
- No secrets in repo; large models/configs live under `~/.cream/models` (auto-created).
- Validate inputs with provided helpers; respect `config.max_workers` for parallelism.
