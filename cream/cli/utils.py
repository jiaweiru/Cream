"""Utility CLI commands."""

import typer
from pathlib import Path
from rich.console import Console
from cream.utils.progress import create_file_progress

console = Console()
app = typer.Typer(help="Utility commands")


@app.command("sample")
def sample_files(
    input_dir: Path = typer.Argument(..., help="Input directory containing files"),
    output_dir: Path = typer.Argument(..., help="Output directory for sampled files"),
    count: int = typer.Option(100, "--count", "-c", help="Number of files to sample"),
    pattern: str = typer.Option("*", "--pattern", "-p", help="File pattern to match"),
    seed: int | None = typer.Option(None, "--seed", help="Random seed for reproducibility")
):
    """Randomly sample files from input directory."""
    from cream.utils.file_ops import FileSampler
    
    console.print(f"[green]Sampling {count} files from {input_dir}[/green]")
    
    sampler = FileSampler(seed)
    with create_file_progress() as progress:
        task = progress.add_task("Sampling files...", total=None)
        sampled_files = sampler.sample_directory(input_dir, output_dir, count, pattern)
        progress.update(task, description="✅ Sampling completed")
    
    console.print(f"[blue]Sampled {len(sampled_files)} files to {output_dir}[/blue]")


@app.command("index-match")
def index_match(
    source: Path = typer.Argument(..., help="Source file or directory with indices"),
    target: Path = typer.Argument(..., help="Target file or directory to match"),
    pattern: str = typer.Option(".*", "--pattern", "-p", help="Regex pattern for matching"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file for matches")
):
    """Match indices between source and target using regex patterns."""
    from cream.utils.indexing import IndexMatcher
    
    console.print(f"[green]Matching indices between {source} and {target}[/green]")
    
    matcher = IndexMatcher()
    with create_file_progress() as progress:
        task = progress.add_task("Matching indices...", total=None)
        matches = matcher.match_indices(source, target, pattern)
        progress.update(task, description="✅ Matching completed")
    
    console.print(f"[blue]Found {len(matches)} matches[/blue]")
    
    if output:
        import json
        output.write_text(json.dumps(matches, indent=2))
        console.print(f"[blue]Matches saved to {output}[/blue]")
    else:
        for match in matches[:10]:
            console.print(f"  {match['source']} -> {match['target']}")
        if len(matches) > 10:
            console.print(f"  ... and {len(matches) - 10} more matches")