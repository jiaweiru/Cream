"""Text processing CLI commands.

Improvements:
- Filters methods to text-only using registry base class.
- Supports single-file and directory batch processing with workers.
- Wires model/config options and clearer error handling.
"""

import typer
from pathlib import Path
from rich.console import Console

from cream.text.text_processor import TextProcessorInterface, BaseTextProcessor
from cream.core.config import config
from cream.core.processor import processor_registry
from cream.core.exceptions import CreamError

console = Console()
app = typer.Typer(help="Text processing commands")


@app.command("process")
def process_text(
    input_path: Path = typer.Argument(..., help="Input file or directory"),
    method: str = typer.Argument(..., help="Processing method to use"),
    output_path: Path | None = typer.Option(
        None, "--output", "-o", help="Output file/dir"
    ),
    num_workers: int = typer.Option(1, "--workers", "-w", help="Workers for batch"),
    model_path: str | None = typer.Option(
        None, "--model-path", help="Path to local model"
    ),
):
    """Process text for a single file or an entire directory."""
    console.print(f"[green]Processing text using {method}[/green]")

    try:
        config.set_parallel_config(num_workers=num_workers)

        cfg: dict[str, str] = {}
        if model_path:
            cfg["model_path"] = model_path

        interface = TextProcessorInterface(method=method, config=cfg or None)

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
                files, output_dir=output_path, num_workers=num_workers
            )
            console.print(f"[blue]Processed {len(results)} files[/blue]")
        else:
            out_file = output_path
            if output_path is not None and output_path.is_dir():
                out_file = output_path / input_path.name
            result = interface.process_file(input_path, out_file)
            console.print(f"[blue]Processing completed: {result}[/blue]")

    except CreamError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list-methods")
def list_methods():
    """List available text processing methods (text-only)."""
    names = processor_registry.list_processors_by_base(BaseTextProcessor)
    if not names:
        console.print("[yellow]No text methods are registered[/yellow]")
        return
    console.print("[green]Available text processing methods:[/green]")
    for name in sorted(names):
        console.print(f"  • {name}")
