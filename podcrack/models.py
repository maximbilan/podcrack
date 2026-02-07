"""Data models for transcripts and episodes."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class Segment:
    """A single timestamped text segment from a transcript."""

    text: str
    begin: Optional[str] = None  # Timestamp like "00:01:23.456"
    end: Optional[str] = None
    speaker: Optional[str] = None  # Speaker label if present


@dataclass
class Transcript:
    """A complete transcript with metadata."""

    file_path: Path
    segments: List[Segment]
    podcast_name: Optional[str] = None
    episode_title: Optional[str] = None
    publish_date: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    @property
    def full_text(self) -> str:
        """Get the full transcript text without timestamps."""
        return " ".join(segment.text for segment in self.segments)

    @property
    def text_with_timestamps(self) -> str:
        """Get the transcript text with timestamps formatted as [HH:MM:SS]."""
        lines = []
        for segment in self.segments:
            timestamp = ""
            if segment.begin:
                # Convert timestamp to [HH:MM:SS] format
                try:
                    parts = segment.begin.split(":")
                    if len(parts) == 3:
                        h, m, s = parts
                        s = s.split(".")[0]  # Remove milliseconds
                        timestamp = f"[{h}:{m}:{s}]"
                except (ValueError, IndexError):
                    pass

            speaker_prefix = f"{segment.speaker}: " if segment.speaker else ""
            lines.append(f"{timestamp} {speaker_prefix}{segment.text}".strip())

        return "\n".join(lines)

    @property
    def word_count(self) -> int:
        """Get approximate word count."""
        return len(self.full_text.split())

    @property
    def duration_formatted(self) -> str:
        """Get formatted duration estimate."""
        if not self.duration_seconds:
            return "Unknown"
        minutes = int(self.duration_seconds / 60)
        return f"~{minutes} min"
