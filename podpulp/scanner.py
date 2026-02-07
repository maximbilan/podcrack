"""Scan for TTML transcript files in Apple Podcasts cache directory."""

from pathlib import Path
from typing import List

# Apple Podcasts cache directory
TTML_DIR = Path.home() / "Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Library/Cache/Assets/TTML"
SQLITE_DB = Path.home() / "Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Documents/MTLibrary.sqlite"


def scan_ttml_files() -> List[Path]:
    """
    Scan the TTML directory recursively for all .ttml files.

    Returns:
        List of Path objects to TTML files, sorted by modification time (newest first).

    Raises:
        FileNotFoundError: If the TTML directory doesn't exist.
        PermissionError: If access to the directory is denied.
    """
    if not TTML_DIR.exists():
        raise FileNotFoundError(
            f"TTML directory not found: {TTML_DIR}\n"
            "Make sure Apple Podcasts has cached transcripts. "
            "Open a transcript in the Podcasts app first."
        )

    if not TTML_DIR.is_dir():
        raise NotADirectoryError(f"Expected directory but found: {TTML_DIR}")

    # Recursively search for .ttml files in subdirectories
    ttml_files = list(TTML_DIR.rglob("*.ttml"))
    
    # Filter out any non-file entries (shouldn't happen, but be safe)
    ttml_files = [f for f in ttml_files if f.is_file()]
    
    # Sort by modification time, newest first
    ttml_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return ttml_files


def get_sqlite_db_path() -> Path:
    """Get the path to the SQLite metadata database."""
    return SQLITE_DB


def check_sqlite_db_exists() -> bool:
    """Check if the SQLite database exists."""
    return SQLITE_DB.exists() and SQLITE_DB.is_file()
