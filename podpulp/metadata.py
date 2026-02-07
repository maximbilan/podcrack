"""Query SQLite database for episode metadata."""

import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

from podpulp.scanner import SQLITE_DB

if TYPE_CHECKING:
    from podpulp.models import Transcript


def get_transcript_identifier(ttml_file_path: Path) -> str:
    """
    Extract the transcript identifier (relative path) from a TTML file path.

    This matches the format stored in ZTRANSCRIPTIDENTIFIER in the database.
    Example: PodcastContent221/v4/f4/df/8a/f4df8a4a-9adb-ecf7-1325-fa148c876490/transcript_1000746774876.ttml

    The filename may have a duplicate pattern like transcript_123.ttml-123.ttml
    which should be normalized to transcript_123.ttml
    """
    # Get relative path from TTML base directory
    ttml_base = Path.home() / "Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Library/Cache/Assets/TTML"

    try:
        relative_path = ttml_file_path.relative_to(ttml_base)
        identifier = str(relative_path)

        # Handle duplicate filename pattern (e.g., transcript_123.ttml-123.ttml -> transcript_123.ttml)
        # Match pattern: anything.ttml-number.ttml at the end
        identifier = re.sub(r"(.+\.ttml)-\d+\.ttml$", r"\1", identifier)

        return identifier
    except ValueError:
        # If path is not relative to base, return just the filename (also handle duplicate pattern)
        filename = ttml_file_path.name
        filename = re.sub(r"(.+\.ttml)-\d+\.ttml$", r"\1", filename)
        return filename


def get_episode_metadata(ttml_file_path: Path) -> Tuple[Optional[str], Optional[str], Optional[datetime]]:
    """
    Query the SQLite database to find episode metadata for a TTML file.

    Args:
        ttml_file_path: Path to the TTML file

    Returns:
        Tuple of (podcast_name, episode_title, publish_date)
        Returns (None, None, None) if not found or database unavailable
    """
    if not SQLITE_DB.exists():
        return None, None, None

    try:
        conn = sqlite3.connect(str(SQLITE_DB))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get transcript identifier (relative path from TTML base)
        transcript_identifier = get_transcript_identifier(ttml_file_path)

        # Query using the standard Apple Podcasts schema
        # Join ZMTEPISODE with ZMTPODCAST to get both episode and podcast info
        query = """
        SELECT
            e.ZTITLE as episode_title,
            e.ZPUBDATE,
            e.ZDURATION,
            p.ZTITLE as podcast_title,
            p.ZAUTHOR as podcast_author
        FROM ZMTEPISODE e
        JOIN ZMTPODCAST p ON e.ZPODCASTUUID = p.ZUUID
        WHERE e.ZTRANSCRIPTIDENTIFIER = ?
        LIMIT 1
        """

        cursor.execute(query, (transcript_identifier,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None, None, None

        # Extract values
        episode_title = row["episode_title"] if row["episode_title"] else None
        podcast_name = row["podcast_title"] if row["podcast_title"] else None
        publish_date = None

        # Convert ZPUBDATE (seconds since 2001-01-01) to datetime
        if row["ZPUBDATE"]:
            try:
                # Apple uses seconds since 2001-01-01 00:00:00 UTC
                base_date = datetime(2001, 1, 1)
                timestamp = row["ZPUBDATE"]
                if isinstance(timestamp, (int, float)):
                    publish_date = datetime.fromtimestamp(base_date.timestamp() + timestamp)
            except (ValueError, TypeError, OSError):
                pass

        conn.close()

        return podcast_name, episode_title, publish_date

    except sqlite3.OperationalError as e:
        # Table or column doesn't exist - schema might be different
        # Try fallback approach
        try:
            conn = sqlite3.connect(str(SQLITE_DB))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('ZMTEPISODE', 'ZMTPODCAST')")
            tables = [row[0] for row in cursor.fetchall()]

            if "ZMTEPISODE" not in tables or "ZMTPODCAST" not in tables:
                conn.close()
                return None, None, None

            # Try alternative column names
            transcript_identifier = get_transcript_identifier(ttml_file_path)

            # Try with ZCLEANEDTITLE instead of ZTITLE for podcast
            query = """
            SELECT
                e.ZTITLE as episode_title,
                e.ZPUBDATE,
                p.ZCLEANEDTITLE as podcast_title,
                p.ZAUTHOR as podcast_author
            FROM ZMTEPISODE e
            JOIN ZMTPODCAST p ON e.ZPODCASTUUID = p.ZUUID
            WHERE e.ZTRANSCRIPTIDENTIFIER = ?
            LIMIT 1
            """

            cursor.execute(query, (transcript_identifier,))
            row = cursor.fetchone()

            if row:
                episode_title = row["episode_title"] if row["episode_title"] else None
                podcast_name = row["podcast_title"] if row["podcast_title"] else None
                publish_date = None

                if row["ZPUBDATE"]:
                    try:
                        base_date = datetime(2001, 1, 1)
                        timestamp = row["ZPUBDATE"]
                        if isinstance(timestamp, (int, float)):
                            publish_date = datetime.fromtimestamp(base_date.timestamp() + timestamp)
                    except (ValueError, TypeError, OSError):
                        pass

                conn.close()
                return podcast_name, episode_title, publish_date

            conn.close()
            return None, None, None

        except Exception:
            return None, None, None

    except (sqlite3.Error, Exception):
        # Silently fail and return None values
        # The app will fall back to filename-based display
        return None, None, None


def enrich_transcript_metadata(transcript: "Transcript", podcast_name: Optional[str] = None, episode_title: Optional[str] = None, publish_date: Optional[datetime] = None):
    """
    Enrich a Transcript object with metadata.

    Args:
        transcript: Transcript object to enrich
        podcast_name: Podcast name (if already known)
        episode_title: Episode title (if already known)
        publish_date: Publish date (if already known)
    """
    # Try to get from database if not all metadata provided
    if not (podcast_name and episode_title and publish_date):
        db_podcast, db_title, db_date = get_episode_metadata(transcript.file_path)
        transcript.podcast_name = podcast_name or db_podcast
        transcript.episode_title = episode_title or db_title
        transcript.publish_date = publish_date or db_date
    else:
        transcript.podcast_name = podcast_name
        transcript.episode_title = episode_title
        transcript.publish_date = publish_date

    # Fallback to filename if no title found
    if not transcript.episode_title:
        transcript.episode_title = transcript.file_path.stem
