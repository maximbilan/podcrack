"""Main entry point for PodPulp CLI."""

import sys
from pathlib import Path
from typing import List, Optional

import questionary
from rich.console import Console

from podpulp.display import (
    display_transcript,
    print_banner,
    print_error,
    print_info,
    print_success,
    print_transcript_list,
)
from podpulp.export import copy_to_clipboard, save_to_file
from podpulp.metadata import enrich_transcript_metadata
from podpulp.models import Transcript
from podpulp.parser import parse_ttml
from podpulp.scanner import check_sqlite_db_exists, scan_ttml_files

console = Console()


def fuzzy_match(query: str, text: str) -> bool:
    """Simple fuzzy matching - check if query words appear in text."""
    if not query:
        return True
    query_lower = query.lower()
    text_lower = text.lower()
    return query_lower in text_lower


def filter_transcripts(transcripts: List[Transcript], query: str) -> List[Transcript]:
    """Filter transcripts by search query."""
    if not query:
        return transcripts

    filtered = []
    for transcript in transcripts:
        podcast = transcript.podcast_name or ""
        episode = transcript.episode_title or transcript.file_path.stem
        if fuzzy_match(query, podcast) or fuzzy_match(query, episode):
            filtered.append(transcript)

    return filtered


def load_all_transcripts() -> List[Transcript]:
    """Scan and parse all TTML files, enriching with metadata."""
    try:
        ttml_files = scan_ttml_files()
    except FileNotFoundError as e:
        print_error(str(e))
        sys.exit(1)
    except PermissionError:
        print_error(
            "Permission denied accessing Apple Podcasts cache directory.\n"
            "Make sure you have read access to ~/Library/Group Containers/"
        )
        sys.exit(1)

    if not ttml_files:
        print_error(
            "No transcripts found.\n"
            "Open Apple Podcasts and view a transcript first to cache it locally."
        )
        sys.exit(1)

    console.print(f"[green]Found {len(ttml_files)} transcripts.[/green]\n")

    transcripts = []
    db_available = check_sqlite_db_exists()

    if not db_available:
        print_info("SQLite database not found. Using filenames for episode titles.\n")

    for ttml_file in ttml_files:
        try:
            transcript = parse_ttml(ttml_file)
            if db_available:
                enrich_transcript_metadata(transcript)
            else:
                # Fallback to filename
                transcript.episode_title = ttml_file.stem
            transcripts.append(transcript)
        except Exception as e:
            # Skip corrupt files
            console.print(f"[yellow]⚠️  Skipping {ttml_file.name}: {e}[/yellow]")
            continue

    # Sort by date (newest first)
    transcripts.sort(
        key=lambda t: (
            t.publish_date.timestamp() if t.publish_date else 0,
            t.file_path.stat().st_mtime,
        ),
        reverse=True,
    )

    return transcripts


def transcript_action_menu(transcript: Transcript) -> str:
    """Show action menu for a selected transcript."""
    title = transcript.episode_title or transcript.file_path.stem
    podcast = transcript.podcast_name or "Unknown Podcast"

    console.print(f"\n[bold cyan]━━━ {title} ━━━[/bold cyan]")
    console.print(f"[dim]{podcast}[/dim]\n")

    choice = questionary.select(
        "What would you like to do?",
        choices=[
            questionary.Choice("View transcript", value="view"),
            questionary.Choice("Copy to clipboard", value="copy"),
            questionary.Choice("Save as text file", value="save"),
            questionary.Choice("Save with timestamps", value="save_timestamps"),
            questionary.Choice("Back to list", value="back"),
        ],
    ).ask()

    return choice or "back"


def main():
    """Main CLI entry point."""
    print_banner()

    # Load all transcripts
    transcripts = load_all_transcripts()

    current_page = 1
    per_page = 20
    search_query = ""

    while True:
        # Filter by search query
        filtered = filter_transcripts(transcripts, search_query)

        if not filtered:
            console.print("[yellow]No transcripts match your search.[/yellow]\n")
            search_query = ""
            continue

        # Display list
        total_pages = (len(filtered) + per_page - 1) // per_page
        print_transcript_list(filtered, page=current_page, per_page=per_page)

        # Get user input
        if search_query:
            prompt_text = f"🔍 Search: '{search_query}' (Enter=clear, number=select, n/p=page, q=quit)"
        else:
            prompt_text = "🔍 Search, number to select, 'n'/'p' to page, 'q' to quit"

        user_input = questionary.text(prompt_text, default="").ask()

        if user_input is None or user_input.lower() == "q":
            console.print("\n[dim]Goodbye![/dim]")
            sys.exit(0)

        user_input = user_input.strip().lower()

        # Handle pagination
        if user_input == "n" or user_input == "next":
            if current_page < total_pages:
                current_page += 1
            else:
                print_info("Already on last page")
            continue
        elif user_input == "p" or user_input == "prev":
            if current_page > 1:
                current_page -= 1
            else:
                print_info("Already on first page")
            continue

        # Handle search (empty or non-numeric)
        if not user_input:
            search_query = ""
            current_page = 1
            continue

        # Try to parse as number
        try:
            selection = int(user_input)
            # Check if selection is within current page range
            start_idx = (current_page - 1) * per_page
            end_idx = min(start_idx + per_page, len(filtered))
            
            if 1 <= selection <= len(filtered):
                # Map selection to actual index in filtered list
                selected_transcript = filtered[selection - 1]

                # Action menu loop
                while True:
                    action = transcript_action_menu(selected_transcript)

                    if action == "back":
                        break
                    elif action == "view":
                        console.print()
                        show_timestamps = questionary.confirm(
                            "Show timestamps?", default=False
                        ).ask()
                        display_transcript(selected_transcript, show_timestamps=show_timestamps)
                    elif action == "copy":
                        text = selected_transcript.full_text
                        if copy_to_clipboard(text):
                            word_count = selected_transcript.word_count
                            print_success(f"Transcript copied to clipboard! ({word_count:,} words)")
                        else:
                            print_error("Failed to copy to clipboard.")
                    elif action == "save":
                        file_path = save_to_file(selected_transcript, include_timestamps=False)
                        print_success(f"Saved to: {file_path}")
                    elif action == "save_timestamps":
                        file_path = save_to_file(selected_transcript, include_timestamps=True)
                        print_success(f"Saved to: {file_path}")

                    console.print()
            else:
                print_error(f"Please select a number between 1 and {len(filtered)}")
        except ValueError:
            # Not a number, treat as search query
            search_query = user_input
            current_page = 1


if __name__ == "__main__":
    main()
