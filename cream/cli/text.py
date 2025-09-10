"""Text processing CLI commands."""

import typer
from pathlib import Path
from rich.console import Console

from cream.text.text_processor import TextProcessorInterface

console = Console()
app = typer.Typer(help="Text processing commands")




@app.command("process")
def process_text(
    input_file: Path = typer.Argument(..., help="Input text file"),
    method: str = typer.Argument(..., help="Processing method to use"),
    output_file: Path = typer.Option(None, "--output", "-o", help="Output file"),
    num_workers: int = typer.Option(1, "--workers", "-w", help="Number of parallel workers"),
    model_path: str | None = typer.Option(None, "--model-path", help="Path to local model"),
):
    """Process text using any available method."""
    console.print(f"[green]Processing text using {method}[/green]")
    
    try:
        cfg: dict[str, str] = {}
        if model_path:
            cfg["model_path"] = model_path

        processor = TextProcessorInterface(method=method, config=cfg or None)
        result = processor.process_file(input_file, output_file)
        console.print(f"[blue]Processing completed: {result}[/blue]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("list-methods")
def list_methods():
    """List available text processing methods."""
    console.print("[green]Available text processing methods:[/green]")
    
    methods = TextProcessorInterface.list_all_methods()
    
    console.print("\n[bold]Normalization methods:[/bold]")
    for method in methods["normalization"]:
        console.print(f"  • {method}")
    
    console.print("\n[bold]Processing methods:[/bold]")
    for method in methods["processing"]:
        console.print(f"  • {method}")
    
    console.print("\n[bold]Analysis methods:[/bold]")
    for method in methods["analysis"]:
        console.print(f"  • {method}")
