"""Parse TTML XML files into Transcript objects."""

import re
from pathlib import Path
from typing import List, Optional
from xml.etree import ElementTree as ET

from podpulp.models import Segment, Transcript


# TTML namespace
TTML_NS = "{http://www.w3.org/ns/ttml}"


def parse_timestamp(timestamp_str: str) -> float:
    """
    Parse a TTML timestamp string to seconds.

    Formats supported:
    - "00:01:23.456" (hours:minutes:seconds.milliseconds)
    - "01:23.456" (minutes:seconds.milliseconds)
    - "123.456" (seconds.milliseconds)
    """
    # Remove any whitespace
    timestamp_str = timestamp_str.strip()

    # Split by colon
    parts = timestamp_str.split(":")
    total_seconds = 0.0

    if len(parts) == 3:  # HH:MM:SS.mmm
        hours, minutes, seconds = parts
        total_seconds = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    elif len(parts) == 2:  # MM:SS.mmm
        minutes, seconds = parts
        total_seconds = float(minutes) * 60 + float(seconds)
    else:  # SS.mmm or just SS
        total_seconds = float(timestamp_str)

    return total_seconds


def extract_text_from_element(elem: ET.Element) -> str:
    """
    Extract and concatenate all text from an element and its children.
    
    This recursively traverses all nested <span> elements to extract text,
    matching the approach used by Apple Podcasts TTML files.
    """
    text_parts = []
    
    def collect_text(e):
        """Recursively collect text from element and all descendants."""
        # Get direct text content
        if e.text and e.text.strip():
            text_parts.append(e.text.strip())
        # Recursively process all children
        for child in e:
            collect_text(child)
        # Get tail text (text after this element, before next sibling)
        if e.tail and e.tail.strip():
            text_parts.append(e.tail.strip())
    
    collect_text(elem)
    
    # Join and normalize whitespace
    text = " ".join(text_parts)
    # Replace multiple spaces/newlines with single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def group_segments_into_paragraphs(segments: List[Segment], gap_threshold: float = 2.0) -> List[str]:
    """
    Group consecutive segments into paragraphs based on time gaps.

    Args:
        segments: List of segments with timestamps
        gap_threshold: Minimum gap in seconds to start a new paragraph

    Returns:
        List of paragraph strings
    """
    if not segments:
        return []

    paragraphs = []
    current_paragraph = []

    for i, segment in enumerate(segments):
        if not current_paragraph:
            current_paragraph.append(segment.text)
        else:
            # Check gap from previous segment
            prev_segment = segments[i - 1]
            if prev_segment.end and segment.begin:
                try:
                    prev_end = parse_timestamp(prev_segment.end)
                    curr_begin = parse_timestamp(segment.begin)
                    gap = curr_begin - prev_end

                    if gap > gap_threshold:
                        # Start new paragraph
                        paragraphs.append(" ".join(current_paragraph))
                        current_paragraph = [segment.text]
                    else:
                        current_paragraph.append(segment.text)
                except (ValueError, TypeError):
                    # If timestamp parsing fails, just append
                    current_paragraph.append(segment.text)
            else:
                current_paragraph.append(segment.text)

    # Add final paragraph
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    return paragraphs


def parse_ttml(file_path: Path) -> Transcript:
    """
    Parse a TTML file into a Transcript object.

    Args:
        file_path: Path to the .ttml file

    Returns:
        Transcript object with parsed segments

    Raises:
        ET.ParseError: If the XML is malformed
        FileNotFoundError: If the file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"TTML file not found: {file_path}")

    tree = ET.parse(file_path)
    root = tree.getroot()

    segments = []
    last_timestamp = None

    # Find all <p> elements in the body
    # TTML structure: <tt><body><div><p>...</p></div></body></tt>
    body = root.find(f".//{TTML_NS}body")
    if body is None:
        # Try without namespace
        body = root.find(".//body")

    if body is not None:
        for div in body.findall(f"{TTML_NS}div") + body.findall("div"):
            for p in div.findall(f"{TTML_NS}p") + div.findall("p"):
                begin = p.get("begin") or p.get(f"{{{TTML_NS}}}begin")
                end = p.get("end") or p.get(f"{{{TTML_NS}}}end")

                # Extract speaker if present
                # Apple Podcasts uses ttm:agent attribute with namespace
                speaker = None
                # Check all attributes for speaker-related ones
                for key, value in p.attrib.items():
                    if "agent" in key.lower() or "speaker" in key.lower():
                        speaker = value
                        break
                # Also try the standard ttm:agent namespace
                ttm_ns = "{http://www.w3.org/ns/ttml#metadata}"
                if not speaker:
                    speaker = p.get(f"{ttm_ns}agent")

                # Extract text
                text = extract_text_from_element(p)

                if text:  # Only add non-empty segments
                    segment = Segment(
                        text=text,
                        begin=begin,
                        end=end,
                        speaker=speaker,
                    )
                    segments.append(segment)

                    # Track last timestamp for duration
                    if end:
                        try:
                            timestamp_seconds = parse_timestamp(end)
                            if last_timestamp is None or timestamp_seconds > last_timestamp:
                                last_timestamp = timestamp_seconds
                        except (ValueError, TypeError):
                            pass

    return Transcript(
        file_path=file_path,
        segments=segments,
        duration_seconds=last_timestamp,
    )
