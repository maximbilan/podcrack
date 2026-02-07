"""Export transcripts to clipboard or file."""

import re
import subprocess
from pathlib import Path
from typing import Optional

try:
    import pyperclip
except ImportError:
    pyperclip = None

from podpulp.models import Transcript


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to the system clipboard.

    Args:
        text: Text to copy

    Returns:
        True if successful, False otherwise
    """
    if pyperclip:
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            pass

    # Fallback to pbcopy on macOS
    try:
        process = subprocess.Popen(
            ["pbcopy"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.communicate(input=text.encode("utf-8"))
        return process.returncode == 0
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def save_to_file(transcript: Transcript, file_path: Optional[Path] = None, include_timestamps: bool = False) -> Path:
    """
    Save transcript to a text file.

    Args:
        transcript: Transcript to save
        file_path: Destination path (if None, generates default)
        include_timestamps: Whether to include timestamps in the output

    Returns:
        Path to the saved file
    """
    if file_path is None:
        # Generate default filename
        podcast_name = transcript.podcast_name or "Unknown_Podcast"
        episode_title = transcript.episode_title or transcript.file_path.stem

        filename = f"{sanitize_filename(podcast_name)}_{sanitize_filename(episode_title)}.txt"
        file_path = Path.home() / "Desktop" / filename

    # Ensure directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Get text content
    if include_timestamps:
        content = transcript.text_with_timestamps
    else:
        content = transcript.full_text

    # Write file
    file_path.write_text(content, encoding="utf-8")

    return file_path
