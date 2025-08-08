"""Main CLI entry point for cream package."""

import typer
from rich.console import Console
from cream.cli import audio, text, utils

console = Console()

app = typer.Typer(
    name="cream",
    help="Simple and convenient audio data analysis and processing toolkit",
    rich_markup_mode="rich"
)

app.add_typer(audio.app, name="audio", help="Audio processing and analysis commands")
app.add_typer(text.app, name="text", help="Text processing commands")
app.add_typer(utils.app, name="utils", help="Utility commands")


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", help="Show version information")
):
    """Cream: Simple and convenient audio data analysis and processing toolkit."""
    if version:
        from cream import __version__
        console.print(f"[bold green]cream[/bold green] version [blue]{__version__}[/blue]")
        raise typer.Exit()


if __name__ == "__main__":
    app()