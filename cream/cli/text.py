"""Text processing CLI commands.

Improvements:
- Filters methods to text-only using registry base class.
- Supports single-file and directory batch processing with workers.
- Wires model/config options and clearer error handling.
"""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from cream.text.text_processor import TextProcessorInterface, BaseTextProcessor
from cream.core.config import config
from cream.core.processor import processor_registry
from cream.core.exceptions import CreamError

console = Console()
app = typer.Typer(help="Text processing commands")


def _parse_params(param_entries: list[str]) -> dict[str, str]:
    """Parse key=value CLI parameters into a dictionary."""
    params: dict[str, str] = {}
    for entry in param_entries:
        if "=" not in entry:
            raise typer.BadParameter(
                "Use --param key=value to pass processor arguments"
            )
        key, value = entry.split("=", 1)
        key = key.strip()
        if not key:
            raise typer.BadParameter("Parameter key cannot be empty")
        params[key] = value.strip()
    return params


@app.command("process")
def process_text(
    input_path: Annotated[Path, typer.Argument(..., help="Input file or directory")],
    method: Annotated[str, typer.Argument(..., help="Processing method to use")],
    output_path: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output file/dir"),
    ] = None,
    params: Annotated[
        list[str],
        typer.Option(
            "--param", help="Processor parameter in key=value form (repeatable)"
        ),
    ] = [],
):
    """Process text for a single file or an entire directory."""
    console.print(f"[green]Processing text using {method}[/green]")

    try:
        extra_args = _parse_params(params)
        interface = TextProcessorInterface(method=method)

        if input_path.is_dir():
            files = [
                p
                for p in input_path.rglob("*")
                if p.is_file() and config.is_text_file(p)
            ]
            if not files:
                console.print(
                    f"[yellow]No supported text files under {input_path}[/yellow]"
                )
                raise typer.Exit(0)

            if (
                output_path is not None
                and output_path.exists()
                and not output_path.is_dir()
            ):
                console.print("[red]--output must be a directory for batch mode[/red]")
                raise typer.Exit(2)

            if output_path is not None:
                output_path.mkdir(parents=True, exist_ok=True)
            results = interface.process_batch(
                files,
                output_dir=output_path,
                num_workers=config.max_workers,
                **extra_args,
            )
            console.print(f"[blue]Processed {len(results)} files[/blue]")
        else:
            out_file = output_path
            if output_path is not None and output_path.is_dir():
                out_file = output_path / input_path.name
            result = interface.process_file(input_path, out_file, **extra_args)
            console.print(f"[blue]Processing completed: {result}[/blue]")

    except CreamError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_methods():
    """List available text processing methods (text-only)."""
    names = processor_registry.list_processors_by_base(BaseTextProcessor)
    if not names:
        console.print("[yellow]No text methods are registered[/yellow]")
        return
    console.print("[green]Available text processing methods:[/green]")
    for name in sorted(names):
        console.print(f"  • {name}")
