"""Audio processing CLI commands."""

import typer
from pathlib import Path
from rich.console import Console

from cream.audio.audio_processor import AudioProcessorInterface

console = Console()
app = typer.Typer(help="Audio processing commands")


@app.command("process")
def process_audio(
    input_path: Path = typer.Argument(..., help="Input audio file"),
    method: str = typer.Argument(..., help="Processing method to use"),
    output_path: Path = typer.Option(
        None, "--output", "-o", help="Output file or directory"
    ),
    num_workers: int = typer.Option(
        1, "--workers", "-w", help="Number of parallel workers"
    ),
    model_path: str | None = typer.Option(None, "--model-path", help="Path to local model"),
):
    """Process audio using any available method."""
    console.print(f"[green]Processing audio using {method}[/green]")

    try:
        cfg: dict[str, str] = {}
        if model_path:
            cfg["model_path"] = model_path

        processor = AudioProcessorInterface(method=method, config=cfg or None)
        result = processor.process_file(input_path, output_path)
        console.print(f"[blue]Processing completed: {result}[/blue]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list-methods")
def list_methods():
    """List available audio processing methods."""
    console.print("[green]Available audio processing methods:[/green]")

    methods = AudioProcessorInterface.list_all_methods()

    console.print("\n[bold]Separation methods:[/bold]")
    for method in methods["separation"]:
        console.print(f"  • {method}")

    console.print("\n[bold]Enhancement methods:[/bold]")
    for method in methods["enhancement"]:
        console.print(f"  • {method}")

    console.print("\n[bold]Basic processing methods:[/bold]")
    for method in methods["basic_processing"]:
        console.print(f"  • {method}")

    console.print("\n[bold]Analysis methods:[/bold]")
    for method in methods["analysis"]:
        console.print(f"  • {method}")
