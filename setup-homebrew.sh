#!/bin/bash
# Helper script for updating the Homebrew formula in this repository

set -e

GITHUB_USER="maximbilan"
REPO_NAME="podcrack"
FORMULA_FILE="Formula/podcrack.rb"

echo "🍺 Homebrew Formula Helper"
echo ""
echo "This script helps update the formula SHA256 when releasing a new version."
echo "The formula is included directly in this repository - no separate tap needed!"
echo ""

# Get current version from formula
CURRENT_VERSION=$(grep -E '^\s*url.*tags/v' "$FORMULA_FILE" | sed -E 's/.*tags\/v([0-9]+\.[0-9]+\.[0-9]+).*/\1/')

if [ -z "$CURRENT_VERSION" ]; then
    echo "⚠️  Could not detect current version from formula"
    CURRENT_VERSION="unknown"
else
    echo "📋 Current version in formula: v$CURRENT_VERSION"
fi

echo ""
read -p "Enter new version tag (e.g., 1.1.0) or press Enter to update SHA256 for current version: " NEW_VERSION

if [ -z "$NEW_VERSION" ]; then
    VERSION="$CURRENT_VERSION"
    echo "Updating SHA256 for v$VERSION..."
else
    VERSION="$NEW_VERSION"
    echo "Updating formula for v$VERSION..."
fi

# Check if tag exists locally
if ! git tag -l | grep -q "^v$VERSION$"; then
    echo ""
    echo "⚠️  Git tag v$VERSION not found locally."
    read -p "Create tag v$VERSION now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag "v$VERSION"
        echo "✅ Created tag v$VERSION"
        echo "   Don't forget to push it: git push origin v$VERSION"
    fi
fi

# Calculate SHA256
echo ""
echo "📦 Calculating SHA256 for release tarball..."
TARBALL_URL="https://github.com/$GITHUB_USER/$REPO_NAME/archive/refs/tags/v$VERSION.tar.gz"
SHA256=$(curl -sL "$TARBALL_URL" | shasum -a 256 | awk '{print $1}')

if [ -z "$SHA256" ] || [ "$SHA256" = "" ]; then
    echo "⚠️  Could not calculate SHA256. Make sure:"
    echo "   1. The tag v$VERSION exists on GitHub: git push origin v$VERSION"
    echo "   2. A GitHub release exists for v$VERSION"
    echo "   3. The tarball URL is accessible: $TARBALL_URL"
    exit 1
fi

echo "✅ SHA256: $SHA256"

# Update formula
if [ "$VERSION" != "$CURRENT_VERSION" ]; then
    # Update version in URL
    sed -i '' "s|url \".*tags/v.*\.tar\.gz\"|url \"https://github.com/$GITHUB_USER/$REPO_NAME/archive/refs/tags/v$VERSION.tar.gz\"|" "$FORMULA_FILE"
    echo "✅ Updated URL to v$VERSION"
fi

# Update SHA256
sed -i '' "s/sha256 \"[^\"]*\"/sha256 \"$SHA256\"/" "$FORMULA_FILE"
echo "✅ Updated SHA256 in formula"

echo ""
echo "✅ Formula updated successfully!"
echo ""
echo "Next steps:"
echo "1. Review the changes: git diff $FORMULA_FILE"
echo "2. Commit the update: git commit -m 'Update formula to v$VERSION' $FORMULA_FILE"
echo "3. Push to GitHub: git push"
echo ""
echo "Users can then install with:"
echo "   brew install --formula https://raw.githubusercontent.com/$GITHUB_USER/$REPO_NAME/main/$FORMULA_FILE"
