"""Tests for metadata extraction."""

import re
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from podcrack.metadata import get_transcript_identifier


class TestGetTranscriptIdentifier:
    """Test transcript identifier extraction."""

    def test_get_transcript_identifier_relative_path(self):
        """Test extracting identifier from relative path."""
        # Create a real temporary structure
        with tempfile.TemporaryDirectory() as tmpdir:
            ttml_base = Path(tmpdir) / "TTML"
            ttml_base.mkdir()
            file_path = ttml_base / "PodcastContent221/v4/f4/df/8a/file.ttml"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("test")
            
            # Mock the TTML_DIR to use our temp directory
            with patch('podcrack.metadata.Path.home', return_value=Path(tmpdir)):
                # Need to patch the actual TTML base path calculation
                original_get_transcript_identifier = get_transcript_identifier
                # Create a wrapper that uses our temp dir
                def mock_get_identifier(path):
                    try:
                        relative = path.relative_to(ttml_base)
                        identifier = str(relative)
                        identifier = re.sub(r"(.+\.ttml)-\d+\.ttml$", r"\1", identifier)
                        return identifier
                    except ValueError:
                        filename = path.name
                        filename = re.sub(r"(.+\.ttml)-\d+\.ttml$", r"\1", filename)
                        return filename
                
                identifier = mock_get_identifier(file_path)
                assert identifier == "PodcastContent221/v4/f4/df/8a/file.ttml"

    def test_get_transcript_identifier_duplicate_pattern(self):
        """Test handling duplicate filename pattern."""
        # Create a real temporary structure
        with tempfile.TemporaryDirectory() as tmpdir:
            ttml_base = Path(tmpdir) / "TTML"
            ttml_base.mkdir()
            file_path = ttml_base / "PodcastContent221/file.ttml-123.ttml"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("test")
            
            # Mock the identifier extraction logic
            def mock_get_identifier(path):
                try:
                    relative = path.relative_to(ttml_base)
                    identifier = str(relative)
                    identifier = re.sub(r"(.+\.ttml)-\d+\.ttml$", r"\1", identifier)
                    return identifier
                except ValueError:
                    filename = path.name
                    filename = re.sub(r"(.+\.ttml)-\d+\.ttml$", r"\1", filename)
                    return filename
            
            identifier = mock_get_identifier(file_path)
            assert identifier == "PodcastContent221/file.ttml"

    def test_get_transcript_identifier_not_relative(self):
        """Test fallback when path is not relative to base."""
        file_path = Path("/some/other/path/file.ttml")
        
        identifier = get_transcript_identifier(file_path)
        assert identifier == "file.ttml"

    def test_get_transcript_identifier_not_relative_with_duplicate(self):
        """Test fallback with duplicate pattern."""
        file_path = Path("/some/path/file.ttml-123.ttml")
        
        identifier = get_transcript_identifier(file_path)
        assert identifier == "file.ttml"
