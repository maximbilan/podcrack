"""Tests for file scanner."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from podcrack.scanner import check_sqlite_db_exists, scan_ttml_files


class TestScanTTMLFiles:
    """Test TTML file scanning."""

    def test_scan_ttml_files_not_found(self):
        """Test error when TTML directory doesn't exist."""
        with patch('podcrack.scanner.TTML_DIR', Path("/nonexistent/dir")):
            with pytest.raises(FileNotFoundError):
                scan_ttml_files()

    def test_scan_ttml_files_empty_directory(self):
        """Test scanning empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ttml_dir = Path(tmpdir) / "TTML"
            ttml_dir.mkdir()
            
            with patch('podcrack.scanner.TTML_DIR', ttml_dir):
                files = scan_ttml_files()
                assert len(files) == 0

    def test_scan_ttml_files_finds_files(self):
        """Test finding TTML files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ttml_dir = Path(tmpdir) / "TTML"
            ttml_dir.mkdir()
            
            # Create test TTML files
            (ttml_dir / "test1.ttml").write_text("test")
            (ttml_dir / "test2.ttml").write_text("test")
            (ttml_dir / "not_ttml.txt").write_text("test")
            
            with patch('podcrack.scanner.TTML_DIR', ttml_dir):
                files = scan_ttml_files()
                assert len(files) == 2
                assert all(f.suffix == ".ttml" for f in files)

    def test_scan_ttml_files_recursive(self):
        """Test recursive scanning in subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ttml_dir = Path(tmpdir) / "TTML"
            ttml_dir.mkdir()
            subdir = ttml_dir / "subdir"
            subdir.mkdir()
            
            # Create files in subdirectory
            (subdir / "test.ttml").write_text("test")
            
            with patch('podcrack.scanner.TTML_DIR', ttml_dir):
                files = scan_ttml_files()
                assert len(files) == 1
                assert "subdir" in str(files[0])

    def test_scan_ttml_files_sorted_by_mtime(self):
        """Test files are sorted by modification time."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ttml_dir = Path(tmpdir) / "TTML"
            ttml_dir.mkdir()
            
            file1 = ttml_dir / "old.ttml"
            file2 = ttml_dir / "new.ttml"
            
            file1.write_text("old")
            file2.write_text("new")
            
            # Make file2 newer
            import time
            time.sleep(0.1)
            file2.touch()
            
            with patch('podcrack.scanner.TTML_DIR', ttml_dir):
                files = scan_ttml_files()
                # Newest first
                assert files[0].name == "new.ttml"
                assert files[1].name == "old.ttml"


class TestCheckSQLiteDBExists:
    """Test SQLite database existence check."""

    def test_check_sqlite_db_exists_true(self):
        """Test when database exists."""
        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as f:
            db_path = Path(f.name)
        
        try:
            with patch('podcrack.scanner.SQLITE_DB', db_path):
                assert check_sqlite_db_exists() is True
        finally:
            db_path.unlink()

    def test_check_sqlite_db_exists_false(self):
        """Test when database doesn't exist."""
        fake_path = Path("/nonexistent/db.sqlite")
        with patch('podcrack.scanner.SQLITE_DB', fake_path):
            assert check_sqlite_db_exists() is False
