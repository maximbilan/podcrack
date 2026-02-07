"""Tests for data models."""

from datetime import datetime
from pathlib import Path

import pytest

from podcrack.models import Segment, Transcript


class TestSegment:
    """Test Segment dataclass."""

    def test_create_segment(self):
        """Test creating a segment."""
        segment = Segment(
            text="Hello world",
            begin="0",
            end="5",
            speaker="SPEAKER_1"
        )
        assert segment.text == "Hello world"
        assert segment.begin == "0"
        assert segment.end == "5"
        assert segment.speaker == "SPEAKER_1"

    def test_segment_optional_fields(self):
        """Test segment with optional fields."""
        segment = Segment(text="Hello")
        assert segment.text == "Hello"
        assert segment.begin is None
        assert segment.end is None
        assert segment.speaker is None


class TestTranscript:
    """Test Transcript dataclass."""

    def test_full_text(self):
        """Test full_text property."""
        file_path = Path("/test/file.ttml")
        segments = [
            Segment(text="Hello"),
            Segment(text="world"),
            Segment(text="!")
        ]
        transcript = Transcript(file_path=file_path, segments=segments)
        assert transcript.full_text == "Hello world !"

    def test_word_count(self):
        """Test word_count property."""
        file_path = Path("/test/file.ttml")
        segments = [
            Segment(text="Hello world"),
            Segment(text="This is a test")
        ]
        transcript = Transcript(file_path=file_path, segments=segments)
        assert transcript.word_count == 6

    def test_duration_formatted(self):
        """Test duration_formatted property."""
        file_path = Path("/test/file.ttml")
        transcript = Transcript(
            file_path=file_path,
            segments=[],
            duration_seconds=125.5
        )
        assert transcript.duration_formatted == "~2 min"

    def test_duration_formatted_unknown(self):
        """Test duration_formatted with no duration."""
        file_path = Path("/test/file.ttml")
        transcript = Transcript(file_path=file_path, segments=[])
        assert transcript.duration_formatted == "Unknown"

    def test_text_with_timestamps(self):
        """Test text_with_timestamps property."""
        file_path = Path("/test/file.ttml")
        segments = [
            Segment(text="Hello", begin="00:00:01", end="00:00:02"),
            Segment(text="world", begin="00:00:03", end="00:00:04")
        ]
        transcript = Transcript(file_path=file_path, segments=segments)
        result = transcript.text_with_timestamps
        assert "[00:00:01]" in result
        assert "[00:00:03]" in result
        assert "Hello" in result
        assert "world" in result

    def test_text_with_timestamps_no_timestamps(self):
        """Test text_with_timestamps without timestamps."""
        file_path = Path("/test/file.ttml")
        segments = [
            Segment(text="Hello"),
            Segment(text="world")
        ]
        transcript = Transcript(file_path=file_path, segments=segments)
        result = transcript.text_with_timestamps
        assert "Hello" in result
        assert "world" in result

    def test_text_with_timestamps_speaker(self):
        """Test text_with_timestamps with speaker labels."""
        file_path = Path("/test/file.ttml")
        segments = [
            Segment(
                text="Hello",
                begin="00:00:01",
                speaker="SPEAKER_1"
            )
        ]
        transcript = Transcript(file_path=file_path, segments=segments)
        result = transcript.text_with_timestamps
        assert "SPEAKER_1" in result
        assert "Hello" in result

    def test_metadata_fields(self):
        """Test metadata fields."""
        file_path = Path("/test/file.ttml")
        publish_date = datetime(2026, 1, 27)
        transcript = Transcript(
            file_path=file_path,
            segments=[],
            podcast_name="Test Podcast",
            episode_title="Test Episode",
            publish_date=publish_date
        )
        assert transcript.podcast_name == "Test Podcast"
        assert transcript.episode_title == "Test Episode"
        assert transcript.publish_date == publish_date
