#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"
MARKER=".deps_installed"

# Check Python version
PYTHON=$(command -v python3 || true)
if [ -z "$PYTHON" ]; then
    echo "❌ Python 3 not found. Install it with: brew install python"
    exit 1
fi

VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$(echo "$VERSION" | cut -d. -f1)
MINOR=$(echo "$VERSION" | cut -d. -f2)
if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]; }; then
    echo "❌ Python 3.10+ required (found $VERSION)"
    exit 1
fi

# Create venv if needed
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
fi

# Activate
source "$VENV_DIR/bin/activate"

# Install deps if needed
if [ ! -f "$MARKER" ] || [ "requirements.txt" -nt "$MARKER" ]; then
    echo "📦 Installing dependencies..."
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    touch "$MARKER"
fi

# Run
echo ""
python -m podpulp "$@"
