"""Main CLI entry point for cream package.

This module provides the command-line interface for the Cream audio and text
processing toolkit. It uses Typer for CLI management and Rich for enhanced
console output.

Example:
    Run the CLI:
        $ cream --version
        $ cream audio separate input.wav output/
        $ cream text normalize input.txt output.txt

For help:
        $ cream --help
        $ cream audio --help
"""

import typer
from pathlib import Path
from rich.console import Console
from cream.cli import audio, text, utils
from cream.core.logging import setup, logger

console = Console()

app = typer.Typer(
    name="cream",
    help="Simple and convenient audio data analysis and processing toolkit",
    rich_markup_mode="rich",
)

app.add_typer(audio.app, name="audio", help="Audio processing and analysis commands")
app.add_typer(text.app, name="text", help="Text processing commands")
app.add_typer(utils.app, name="utils", help="Utility commands")


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show version information"
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        "-l",
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
    log_file: str | None = typer.Option(None, "--log-file", help="Path to log file"),
    no_color: bool = typer.Option(
        False, "--no-color", help="Disable colored console output"
    ),
):
    """Cream: Simple and convenient audio data analysis and processing toolkit.

    This is the main entry point callback that configures global settings like
    logging and handles version display.

    Args:
        version (bool): If True, display version information and exit.
        log_level (str): Logging level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file (str | None): Optional path to log file for output.
        no_color (bool): If True, disable colored console output.

    Raises:
        typer.Exit: When version flag is used.
    """
    setup(
        level=log_level.upper(),
        file=Path(log_file) if log_file else None,
        colorize=not no_color,
    )

    logger.debug(f"Starting cream CLI with log level: {log_level}")

    if version:
        from cream import __version__

        logger.info("Displaying version information")
        console.print(
            f"[bold green]cream[/bold green] version [blue]{__version__}[/blue]"
        )
        raise typer.Exit()


if __name__ == "__main__":
    app()
