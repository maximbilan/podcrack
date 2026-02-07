# podcrack — Apple Podcast Transcript Extractor

Extract and export full transcripts from Apple Podcasts' locally cached TTML files on macOS. Bypass Apple's 200-word copy limit and get complete transcripts with timestamps.

**podcrack** is a Python CLI tool that reads Apple Podcasts' cached transcript files and provides an interactive interface to browse, search, and export full transcripts.

## Features

- 🔍 **Browse & Search** — Find transcripts by podcast name or episode title
- 📄 **Full Transcripts** — Extract complete transcript text from cached TTML files
- ⏱️ **Timestamps** — View or export transcripts with timestamp markers
- 📋 **Copy to Clipboard** — One-click copy for easy pasting
- 💾 **Export to File** — Save transcripts as text files (with or without timestamps)
- 🎨 **Beautiful CLI** — Rich terminal UI with colors and formatting

## Requirements

- **macOS** (Apple Podcasts desktop app required)
- **Python 3.10+**
- **Apple Podcasts** must have cached transcripts locally (open a transcript in the app first)

## Quick Start

Just run:

```bash
./run.sh
```

The script will:
1. Check for Python 3.10+
2. Create a virtual environment (if needed)
3. Install dependencies (if needed)
4. Launch podcrack

## How It Works

Apple Podcasts caches transcript files locally when you view them in the app:

- **TTML files** are stored at:
  ```
  ~/Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Library/Cache/Assets/TTML/
  ```

- **Episode metadata** (titles, dates) is in a SQLite database at:
  ```
  ~/Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Documents/MTLibrary.sqlite
  ```

podcrack reads these files (read-only) to extract and display transcripts.

## Usage

### Basic Flow

1. **Launch the app**: `./run.sh`
2. **Browse transcripts**: See a numbered list sorted by date (newest first)
3. **Search**: Type keywords to filter by podcast name or episode title
4. **Select**: Enter a number to view a transcript
5. **Choose action**:
   - **View** — Display transcript in terminal (with optional timestamps)
   - **Copy** — Copy full text to clipboard
   - **Save** — Export as `.txt` file (default: `~/Desktop/`)
   - **Save with timestamps** — Export with `[HH:MM:SS]` markers

### Example

```
$ ./run.sh

🍎 podcrack — Apple Podcast Transcript Extractor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found 47 transcripts.

🔍 Search (or press Enter to browse all): freestyle media

 # │ Podcast          │ Episode                              │ Date       │ Duration
───┼──────────────────┼──────────────────────────────────────┼────────────┼─────────
 1 │ Freestyle Media  │ #170: Can AI Make You A Faster...    │ 2026-01-27 │ ~43 min
 2 │ Freestyle Media  │ #169: Swimming the Channel           │ 2026-01-20 │ ~51 min

Select transcript [1-2]: 1

━━━ #170: Can AI Make You A Faster Swimmer? ━━━

  [a] View transcript
  [b] Copy to clipboard
  [c] Save as text file
  [d] Save with timestamps
  [q] Back to list

Choice: b

✅ Transcript copied to clipboard! (4,832 words)
```

## Project Structure

```
podcrack/
├── run.sh                # One-command setup & run script
├── requirements.txt      # Pinned dependencies
├── pyproject.toml        # Package configuration
├── podcrack/             # Main package
│   ├── __init__.py
│   ├── __main__.py       # Module entry point
│   ├── main.py          # Entry point, CLI flow
│   ├── scanner.py        # Scan TTML directory, discover files
│   ├── parser.py         # Parse TTML XML into transcript objects
│   ├── metadata.py       # Query SQLite DB for episode metadata
│   ├── display.py        # Rich-based terminal rendering
│   ├── export.py         # Clipboard copy, file save
│   └── models.py         # Dataclasses for Transcript, Segment
└── README.md
```

## Installation

### Homebrew (Recommended)

Install via Homebrew:

```bash
brew tap maximbilan/podcrack
brew install podcrack
```

Or in one command:
```bash
brew install maximbilan/podcrack/podcrack
```

### Manual Installation

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python -m podcrack
```

## Running Tests

The easiest way to run tests is using the test script:

```bash
# Run all tests
./test.sh

# Run with coverage
./test.sh --cov=podcrack --cov-report=html

# Run specific test file
./test.sh tests/test_parser.py

# Run specific test
./test.sh tests/test_parser.py::TestParseTimestamp::test_hours_minutes_seconds

# Pass any pytest arguments
./test.sh -v --tb=short
```

Alternatively, if you've already set up the environment:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=podcrack --cov-report=html
```

The test suite includes 47 tests covering parser, models, scanner, metadata, and export functionality.

## Troubleshooting

### "No transcripts found"

Make sure you've opened at least one transcript in the Apple Podcasts app. Transcripts are only cached locally after you view them in the app.

### "TTML directory not found"

The Apple Podcasts cache directory may not exist if:
- You haven't opened Apple Podcasts yet
- You haven't viewed any transcripts
- The app is installed in a non-standard location

### "Permission denied"

Make sure you have read access to `~/Library/Group Containers/`. On macOS, this should work by default, but some security settings may restrict access.

### SQLite database not found

If the metadata database isn't available, podcrack will fall back to using filenames for episode titles. The app will still work, but episode metadata (podcast name, publish date) may be missing.

## Technical Details

### TTML Parsing

- Handles XML namespaces (`http://www.w3.org/ns/ttml`)
- Extracts text from `<p>` elements with `begin`/`end` timestamps
- Groups segments into paragraphs based on time gaps (>2 seconds)
- Preserves speaker labels if present

### Metadata Resolution

- Queries SQLite database to match TTML files with episode metadata
- Falls back to filename and file modification date if database unavailable
- Handles various database schema variations gracefully

## License

See LICENSE file.

## Notes

- **Read-only access**: podcrack never modifies Apple Podcasts files
- **macOS only**: This tool is designed specifically for macOS
- **Privacy**: All processing is local — no data is sent anywhere
