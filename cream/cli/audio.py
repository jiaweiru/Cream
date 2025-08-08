"""Audio processing and analysis CLI commands."""

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
app = typer.Typer(help="Audio processing and analysis commands")

# Audio processing commands
processing_app = typer.Typer(help="Audio processing commands")
app.add_typer(processing_app, name="process")

# Audio analysis commands
analysis_app = typer.Typer(help="Audio analysis commands")
app.add_typer(analysis_app, name="analyze")


@processing_app.command("resample")
def resample_audio(
    input_dir: Path = typer.Argument(..., help="Input directory containing audio files"),
    output_dir: Path = typer.Argument(..., help="Output directory for resampled audio"),
    sample_rate: int = typer.Option(16000, "--sample-rate", "-sr", help="Target sample rate"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files")
):
    """Resample audio files to specified sample rate."""
    from cream.audio.processing.resample import AudioResampler
    
    console.print(f"[green]Resampling audio files from {input_dir} to {sample_rate}Hz[/green]")
    
    resampler = AudioResampler()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing files...", total=None)
        resampler.resample_directory(input_dir, output_dir, sample_rate, overwrite)
        progress.update(task, description="✅ Resampling completed")


@processing_app.command("segment")
def segment_audio(
    input_dir: Path = typer.Argument(..., help="Input directory containing audio files"),
    output_dir: Path = typer.Argument(..., help="Output directory for segmented audio"),
    method: str = typer.Option("fixed", "--method", "-m", help="Segmentation method: fixed or vad"),
    length: float = typer.Option(10.0, "--length", "-l", help="Segment length in seconds (for fixed method)"),
    model: str = typer.Option("silero-vad", "--model", help="VAD model name (for vad method)"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files")
):
    """Segment audio files using fixed length or VAD."""
    from cream.audio.processing.segmentation import AudioSegmenter
    
    console.print(f"[green]Segmenting audio files using {method} method[/green]")
    
    segmenter = AudioSegmenter()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing files...", total=None)
        if method == "fixed":
            segmenter.segment_fixed_length(input_dir, output_dir, length, overwrite)
        elif method == "vad":
            segmenter.segment_vad(input_dir, output_dir, model, overwrite)
        else:
            console.print(f"[red]Unknown segmentation method: {method}[/red]")
            raise typer.Exit(1)
        progress.update(task, description="✅ Segmentation completed")


@processing_app.command("normalize")
def normalize_audio(
    input_dir: Path = typer.Argument(..., help="Input directory containing audio files"),
    output_dir: Path = typer.Argument(..., help="Output directory for normalized audio"),
    method: str = typer.Option("energy", "--method", "-m", help="Normalization method: energy or loudness"),
    target: float | None = typer.Option(None, "--target", "-t", help="Target level (dB)"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files")
):
    """Normalize audio files using energy or loudness normalization."""
    from cream.audio.processing.normalization import AudioNormalizer
    
    console.print(f"[green]Normalizing audio files using {method} method[/green]")
    
    normalizer = AudioNormalizer()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing files...", total=None)
        normalizer.normalize_directory(input_dir, output_dir, method, target, overwrite)
        progress.update(task, description="✅ Normalization completed")


@analysis_app.command("mos")
def analyze_mos(
    input_dir: Path = typer.Argument(..., help="Input directory containing audio files"),
    model: str = typer.Option("nisqa", "--model", "-m", help="MOS evaluation model: nisqa or utmosv2"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file for results")
):
    """Evaluate audio quality using MOS scoring models."""
    from cream.audio.analysis.mos import MOSEvaluator
    
    console.print(f"[green]Evaluating audio quality using {model} model[/green]")
    
    evaluator = MOSEvaluator()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing files...", total=None)
        results = evaluator.evaluate_directory(input_dir, model)
        progress.update(task, description="✅ Analysis completed")
    
    if output:
        import json
        output.write_text(json.dumps(results, indent=2))
        console.print(f"[blue]Results saved to {output}[/blue]")
    else:
        console.print(f"[blue]Average MOS: {sum(results.values()) / len(results):.2f}[/blue]")


@analysis_app.command("asr")
def analyze_asr(
    input_dir: Path = typer.Argument(..., help="Input directory containing audio files"),
    reference: Path | None = typer.Option(None, "--reference", "-r", help="Reference text file"),
    model: str = typer.Option("paraformer", "--model", "-m", help="ASR model: paraformer or whisper"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file for results")
):
    """Evaluate ASR pronunciation accuracy."""
    from cream.audio.analysis.intelligibility import IntelligibilityEvaluator
    
    console.print(f"[green]Evaluating pronunciation accuracy using {model} model[/green]")
    
    evaluator = IntelligibilityEvaluator()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing files...", total=None)
        results = evaluator.evaluate_directory(input_dir, reference, model)
        progress.update(task, description="✅ Analysis completed")
    
    if output:
        import json
        output.write_text(json.dumps(results, indent=2))
        console.print(f"[blue]Results saved to {output}[/blue]")
    else:
        console.print(f"[blue]Analysis completed for {len(results)} files[/blue]")


@analysis_app.command("speaker")
def analyze_speaker(
    input_dir: Path = typer.Argument(..., help="Input directory containing audio files"),
    cluster: bool = typer.Option(False, "--cluster", help="Perform speaker clustering"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file for results")
):
    """Analyze speaker similarity and perform clustering."""
    from cream.audio.analysis.similarity import SpeakerAnalyzer
    
    console.print("[green]Analyzing speaker similarity[/green]")
    
    analyzer = SpeakerAnalyzer()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing files...", total=None)
        results = analyzer.analyze_directory(input_dir, cluster)
        progress.update(task, description="✅ Analysis completed")
    
    if output:
        import json
        output.write_text(json.dumps(results, indent=2))
        console.print(f"[blue]Results saved to {output}[/blue]")
    else:
        console.print(f"[blue]Analysis completed for {len(results)} files[/blue]")


@analysis_app.command("duration")
def analyze_duration(
    input_dir: Path = typer.Argument(..., help="Input directory containing audio files"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output file for statistics")
):
    """Analyze audio duration statistics."""
    from cream.audio.analysis.duration_stats import DurationAnalyzer
    
    console.print("[green]Analyzing audio duration statistics[/green]")
    
    analyzer = DurationAnalyzer()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing files...", total=None)
        stats = analyzer.analyze_directory(input_dir)
        progress.update(task, description="✅ Analysis completed")
    
    console.print(f"[blue]Total files: {stats['total_files']}[/blue]")
    console.print(f"[blue]Total duration: {stats['total_duration']:.2f} seconds[/blue]")
    console.print(f"[blue]Average duration: {stats['average_duration']:.2f} seconds[/blue]")
    
    if output:
        import json
        output.write_text(json.dumps(stats, indent=2))
        console.print(f"[blue]Statistics saved to {output}[/blue]")


@app.command("enhance")
def enhance_audio(
    input_dir: Path = typer.Argument(..., help="Input directory containing audio files"),
    output_dir: Path = typer.Argument(..., help="Output directory for enhanced audio"),
    method: str = typer.Option("uvr", "--method", "-m", help="Enhancement method: uvr or deep-filter-net"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files")
):
    """Perform audio enhancement and source separation using acoustic frontend."""
    from cream.audio.analysis.acoustic_frontend import AcousticFrontend
    
    console.print(f"[green]Performing audio enhancement using {method} method[/green]")
    
    frontend = AcousticFrontend()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing files...", total=None)
        frontend.separate_directory(input_dir, output_dir, method, overwrite)
        progress.update(task, description="✅ Enhancement completed")