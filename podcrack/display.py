"""Rich-based terminal UI for displaying transcripts and menus."""

from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from podcrack.models import Transcript

console = Console()


def print_banner():
    """Print the podcrack banner."""
    banner = """
🍎 podcrack — Apple Podcast Transcript Extractor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    console.print(banner, style="bold cyan")


def print_transcript_list(transcripts: List[Transcript], page: int = 1, per_page: int = 20):
    """
    Display a paginated list of transcripts.

    Args:
        transcripts: List of Transcript objects
        page: Current page number (1-indexed)
        per_page: Number of items per page
    """
    total = len(transcripts)
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total)
    page_transcripts = transcripts[start_idx:end_idx]

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Podcast", style="cyan", width=25)
    table.add_column("Episode", style="white", width=40)
    table.add_column("Date", style="green", width=12)
    table.add_column("Duration", style="yellow", width=10)

    for idx, transcript in enumerate(page_transcripts, start=start_idx + 1):
        podcast = transcript.podcast_name or "Unknown"
        episode = transcript.episode_title or transcript.file_path.stem

        if transcript.publish_date:
            date_str = transcript.publish_date.strftime("%Y-%m-%d")
        else:
            try:
                mtime = transcript.file_path.stat().st_mtime
                date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
            except (OSError, ValueError):
                date_str = "Unknown"

        duration = transcript.duration_formatted

        table.add_row(str(idx), podcast, episode, date_str, duration)

    console.print(table)

    if total > per_page:
        total_pages = (total + per_page - 1) // per_page
        console.print(f"\n[dim]Page {page} of {total_pages} ({total} total transcripts)[/dim]")


def display_transcript(transcript: Transcript, show_timestamps: bool = False):
    """
    Display a full transcript in the terminal.

    Args:
        transcript: Transcript to display
        show_timestamps: Whether to show timestamps
    """
    title = transcript.episode_title or transcript.file_path.stem
    podcast = transcript.podcast_name or "Unknown Podcast"

    header = f"━━━ {title} ━━━"
    console.print(Panel(header, style="bold cyan", title=podcast))

    if show_timestamps:
        content = transcript.text_with_timestamps
    else:
        content = transcript.full_text

    # Split into pages for readability
    words = content.split()
    words_per_page = 500
    total_pages = (len(words) + words_per_page - 1) // words_per_page

    for page_num in range(total_pages):
        start_idx = page_num * words_per_page
        end_idx = min(start_idx + words_per_page, len(words))
        page_content = " ".join(words[start_idx:end_idx])

        if total_pages > 1:
            console.print(f"\n[dim]--- Page {page_num + 1} of {total_pages} ---[/dim]\n")

        # Use Markdown for better formatting
        console.print(Markdown(page_content))

        if page_num < total_pages - 1:
            console.print("\n[dim]Press Enter to continue...[/dim]")
            input()


def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red]❌ Error:[/bold red] {message}")


def print_success(message: str):
    """Print a success message."""
    console.print(f"[bold green]✅ {message}[/bold green]")


def print_info(message: str):
    """Print an info message."""
    console.print(f"[cyan]ℹ️  {message}[/cyan]")
