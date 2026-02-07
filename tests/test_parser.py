"""Tests for TTML parser."""

import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from podcrack.models import Segment, Transcript
from podcrack.parser import (
    extract_text_from_element,
    parse_timestamp,
    parse_ttml,
)


class TestParseTimestamp:
    """Test timestamp parsing."""

    def test_hours_minutes_seconds(self):
        """Test HH:MM:SS format."""
        assert parse_timestamp("01:23:45.678") == pytest.approx(5025.678)

    def test_minutes_seconds(self):
        """Test MM:SS format."""
        assert parse_timestamp("23:45.678") == pytest.approx(1425.678)

    def test_seconds_only(self):
        """Test SS format."""
        assert parse_timestamp("123.456") == pytest.approx(123.456)

    def test_seconds_integer(self):
        """Test integer seconds."""
        assert parse_timestamp("60") == pytest.approx(60.0)

    def test_with_whitespace(self):
        """Test timestamp with whitespace."""
        assert parse_timestamp("  01:23:45.678  ") == pytest.approx(5025.678)


class TestExtractTextFromElement:
    """Test text extraction from XML elements."""

    def test_simple_text(self):
        """Test simple text extraction."""
        elem = ET.Element("p")
        elem.text = "Hello world"
        assert extract_text_from_element(elem) == "Hello world"

    def test_nested_spans(self):
        """Test nested span elements."""
        p = ET.Element("p")
        span1 = ET.SubElement(p, "span")
        span1.text = "Hello"
        span2 = ET.SubElement(p, "span")
        span2.text = "world"
        assert extract_text_from_element(p) == "Hello world"

    def test_deeply_nested(self):
        """Test deeply nested structure."""
        p = ET.Element("p")
        outer_span = ET.SubElement(p, "span")
        inner_span = ET.SubElement(outer_span, "span")
        inner_span.text = "Hello"
        inner_span2 = ET.SubElement(outer_span, "span")
        inner_span2.text = "world"
        result = extract_text_from_element(p)
        assert "Hello" in result
        assert "world" in result

    def test_with_tail_text(self):
        """Test element with tail text."""
        p = ET.Element("p")
        span = ET.SubElement(p, "span")
        span.text = "Hello"
        span.tail = " world"
        assert extract_text_from_element(p) == "Hello world"

    def test_empty_element(self):
        """Test empty element."""
        elem = ET.Element("p")
        assert extract_text_from_element(elem) == ""

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        elem = ET.Element("p")
        elem.text = "Hello    world\n\n\n"
        assert extract_text_from_element(elem) == "Hello world"


class TestParseTTML:
    """Test TTML file parsing."""

    def create_sample_ttml(self, content: str) -> Path:
        """Create a temporary TTML file with given content."""
        ttml_ns = "{http://www.w3.org/ns/ttml}"
        root = ET.Element(f"{ttml_ns}tt")
        root.set("xmlns", "http://www.w3.org/ns/ttml")
        head = ET.SubElement(root, f"{ttml_ns}head")
        body = ET.SubElement(root, f"{ttml_ns}body")
        div = ET.SubElement(body, f"{ttml_ns}div")
        
        # Parse the content string as XML and add to div
        div_elem = ET.fromstring(f"<div xmlns='http://www.w3.org/ns/ttml'>{content}</div>")
        for child in div_elem:
            div.append(child)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttml', delete=False) as f:
            tree = ET.ElementTree(root)
            tree.write(f.name, encoding='unicode', xml_declaration=True)
            return Path(f.name)

    def test_simple_paragraph(self):
        """Test parsing a simple paragraph."""
        content = '<p begin="0" end="5">Hello world</p>'
        ttml_file = self.create_sample_ttml(content)
        
        try:
            transcript = parse_ttml(ttml_file)
            assert len(transcript.segments) == 1
            assert transcript.segments[0].text == "Hello world"
            assert transcript.segments[0].begin == "0"
            assert transcript.segments[0].end == "5"
        finally:
            ttml_file.unlink()

    def test_multiple_paragraphs(self):
        """Test parsing multiple paragraphs."""
        content = '''
        <p begin="0" end="5">First paragraph</p>
        <p begin="5" end="10">Second paragraph</p>
        '''
        ttml_file = self.create_sample_ttml(content)
        
        try:
            transcript = parse_ttml(ttml_file)
            assert len(transcript.segments) == 2
            assert transcript.segments[0].text == "First paragraph"
            assert transcript.segments[1].text == "Second paragraph"
        finally:
            ttml_file.unlink()

    def test_with_speaker(self):
        """Test parsing with speaker attribute."""
        ttml_ns = "{http://www.w3.org/ns/ttml}"
        ttm_ns = "{http://www.w3.org/ns/ttml#metadata}"
        
        root = ET.Element(f"{ttml_ns}tt")
        root.set("xmlns", "http://www.w3.org/ns/ttml")
        root.set(f"xmlns:ttm", "http://www.w3.org/ns/ttml#metadata")
        body = ET.SubElement(root, f"{ttml_ns}body")
        div = ET.SubElement(body, f"{ttml_ns}div")
        p = ET.SubElement(div, f"{ttml_ns}p")
        p.set("begin", "0")
        p.set("end", "5")
        p.set(f"{ttm_ns}agent", "SPEAKER_1")
        p.text = "Hello world"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ttml', delete=False) as f:
            tree = ET.ElementTree(root)
            tree.write(f.name, encoding='unicode', xml_declaration=True)
            ttml_file = Path(f.name)
        
        try:
            transcript = parse_ttml(ttml_file)
            assert len(transcript.segments) == 1
            assert transcript.segments[0].speaker == "SPEAKER_1"
        finally:
            ttml_file.unlink()

    def test_duration_calculation(self):
        """Test duration calculation from timestamps."""
        content = '<p begin="0" end="125.5">Test</p>'
        ttml_file = self.create_sample_ttml(content)
        
        try:
            transcript = parse_ttml(ttml_file)
            assert transcript.duration_seconds == pytest.approx(125.5)
        finally:
            ttml_file.unlink()

    def test_nested_spans(self):
        """Test parsing nested span elements."""
        content = '''
        <p begin="0" end="5">
            <span>Hello</span>
            <span>world</span>
        </p>
        '''
        ttml_file = self.create_sample_ttml(content)
        
        try:
            transcript = parse_ttml(ttml_file)
            assert len(transcript.segments) == 1
            assert "Hello" in transcript.segments[0].text
            assert "world" in transcript.segments[0].text
        finally:
            ttml_file.unlink()

    def test_empty_paragraphs_skipped(self):
        """Test that empty paragraphs are skipped."""
        content = '<p begin="0" end="5"></p><p begin="5" end="10">Not empty</p>'
        ttml_file = self.create_sample_ttml(content)
        
        try:
            transcript = parse_ttml(ttml_file)
            assert len(transcript.segments) == 1
            assert transcript.segments[0].text == "Not empty"
        finally:
            ttml_file.unlink()

    def test_file_not_found(self):
        """Test error handling for missing file."""
        fake_path = Path("/nonexistent/file.ttml")
        with pytest.raises(FileNotFoundError):
            parse_ttml(fake_path)
