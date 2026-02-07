"""Tests for export functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from podcrack.export import sanitize_filename
from podcrack.models import Segment, Transcript


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_sanitize_filename_normal(self):
        """Test normal filename."""
        assert sanitize_filename("test.txt") == "test.txt"

    def test_sanitize_filename_invalid_chars(self):
        """Test removing invalid characters."""
        assert sanitize_filename("test<>file.txt") == "test__file.txt"
        assert sanitize_filename("test:file.txt") == "test_file.txt"
        assert sanitize_filename("test/file.txt") == "test_file.txt"
        assert sanitize_filename("test\\file.txt") == "test_file.txt"
        assert sanitize_filename("test|file.txt") == "test_file.txt"
        assert sanitize_filename("test?file.txt") == "test_file.txt"
        assert sanitize_filename("test*file.txt") == "test_file.txt"

    def test_sanitize_filename_leading_trailing_dots(self):
        """Test removing leading/trailing dots and spaces."""
        assert sanitize_filename(".test.txt") == "test.txt"
        assert sanitize_filename("test.txt.") == "test.txt"
        assert sanitize_filename(" test.txt ") == "test.txt"

    def test_sanitize_filename_length_limit(self):
        """Test length limiting."""
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) == 200

    def test_sanitize_filename_multiple_invalid(self):
        """Test multiple invalid characters."""
        result = sanitize_filename("test<>:\"/\\|?*file.txt")
        # All invalid chars should be replaced with underscores
        assert "_" in result
        assert "test" in result
        assert "file.txt" in result
        # Should not contain any invalid characters
        invalid_chars = '<>:"/\\|?*'
        assert not any(char in result for char in invalid_chars)


class TestSaveToFile:
    """Test file saving functionality."""

    def test_save_to_file_default_path(self, tmp_path):
        """Test saving with default path generation."""
        from podcrack.export import save_to_file
        
        transcript = Transcript(
            file_path=Path("/test/file.ttml"),
            segments=[Segment(text="Hello world")],
            podcast_name="Test Podcast",
            episode_title="Test Episode"
        )
        
        # Mock home directory
        with patch('podcrack.export.Path.home', return_value=tmp_path):
            desktop = tmp_path / "Desktop"
            desktop.mkdir(exist_ok=True)
            
            file_path = save_to_file(transcript)
            
            assert file_path.exists()
            assert file_path.read_text() == "Hello world"
            # Filename sanitization replaces spaces with underscores
            assert "Test" in file_path.name and "Podcast" in file_path.name
            assert "Episode" in file_path.name

    def test_save_to_file_custom_path(self, tmp_path):
        """Test saving to custom path."""
        from podcrack.export import save_to_file
        
        transcript = Transcript(
            file_path=Path("/test/file.ttml"),
            segments=[Segment(text="Hello world")]
        )
        
        custom_path = tmp_path / "custom.txt"
        file_path = save_to_file(transcript, file_path=custom_path)
        
        assert file_path == custom_path
        assert file_path.exists()
        assert file_path.read_text() == "Hello world"

    def test_save_to_file_with_timestamps(self, tmp_path):
        """Test saving with timestamps."""
        from podcrack.export import save_to_file
        
        transcript = Transcript(
            file_path=Path("/test/file.ttml"),
            segments=[
                Segment(text="Hello", begin="00:00:01"),
                Segment(text="world", begin="00:00:02")
            ]
        )
        
        custom_path = tmp_path / "with_timestamps.txt"
        file_path = save_to_file(transcript, file_path=custom_path, include_timestamps=True)
        
        content = file_path.read_text()
        assert "[00:00:01]" in content or "[00:00:02]" in content
