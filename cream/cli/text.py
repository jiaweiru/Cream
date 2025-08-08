"""Text processing CLI commands."""

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
app = typer.Typer(help="Text processing commands")


@app.command("stats")
def text_stats(
    input_file: Path = typer.Argument(..., help="Input text file to analyze"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file for statistics")
):
    """Analyze text length distribution statistics."""
    from cream.text.stats import TextStatistics
    
    console.print(f"[green]Analyzing text statistics for {input_file}[/green]")
    
    analyzer = TextStatistics()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing text...", total=None)
        stats = analyzer.analyze_file(input_file)
        progress.update(task, description="✅ Analysis completed")
    
    console.print(f"[blue]Total lines: {stats['total_lines']}[/blue]")
    console.print(f"[blue]Total characters: {stats['total_characters']}[/blue]")
    console.print(f"[blue]Average length: {stats['average_length']:.2f}[/blue]")
    console.print(f"[blue]Min length: {stats['min_length']}[/blue]")
    console.print(f"[blue]Max length: {stats['max_length']}[/blue]")
    
    if output:
        import json
        output.write_text(json.dumps(stats, indent=2))
        console.print(f"[blue]Statistics saved to {output}[/blue]")


@app.command("normalize")
def normalize_text(
    input_file: Path = typer.Argument(..., help="Input text file to normalize"),
    output_file: Path = typer.Argument(..., help="Output file for normalized text"),
    method: str = typer.Option("basic", "--method", "-m", help="Normalization method"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing output file")
):
    """Normalize text content."""
    from cream.text.normalization import TextNormalizer
    
    console.print(f"[green]Normalizing text using {method} method[/green]")
    
    normalizer = TextNormalizer()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Normalizing text...", total=None)
        normalizer.normalize_file(input_file, output_file, method, overwrite)
        progress.update(task, description="✅ Normalization completed")
    
    console.print(f"[blue]Normalized text saved to {output_file}[/blue]")