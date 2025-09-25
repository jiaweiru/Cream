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

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from cream.cli import audio, text
from cream.core.logging import setup, logger
from cream.core.config import config

console = Console()

app = typer.Typer(
    name="cream",
    help="Simple and convenient audio data analysis and processing toolkit",
    rich_markup_mode="rich",
)

app.add_typer(audio.app, name="audio", help="Audio processing and analysis commands")
app.add_typer(text.app, name="text", help="Text processing commands")


@app.callback(invoke_without_command=True)
def main(
    version: Annotated[
        bool,
        typer.Option("--version", "-v", help="Show version information"),
    ] = False,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level",
            "-l",
            help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        ),
    ] = "INFO",
    log_file: Annotated[
        str | None, typer.Option("--log-file", help="Path to log file")
    ] = None,
    no_color: Annotated[
        bool, typer.Option("--no-color", help="Disable colored console output")
    ] = False,
    workers: Annotated[
        int,
        typer.Option(
            "--workers", "-w", help="Default max workers for batch processing"
        ),
    ] = 1,
    no_progress: Annotated[
        bool, typer.Option("--no-progress", help="Disable progress bars")
    ] = False,
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

    # Apply global config from CLI
    try:
        config.set_parallel_config(
            num_workers=workers, enable_progress_bars=not no_progress
        )
    except Exception:
        # Config is defensive; ignore failures silently here
        pass

    if version:
        from cream import __version__

        logger.debug("Displaying version information")
        console.print(
            f"[bold green]cream[/bold green] version [blue]{__version__}[/blue]"
        )
        raise typer.Exit()


if __name__ == "__main__":
    app()
