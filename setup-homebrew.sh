#!/bin/bash
# Setup script for creating a Homebrew tap for podcrack

set -e

TAP_NAME="homebrew-podcrack"
GITHUB_USER="maximbilan"
REPO_NAME="podcrack"

echo "🍺 Setting up Homebrew tap for podcrack"
echo ""

# Check if tap repo already exists locally
if [ -d "../$TAP_NAME" ]; then
    echo "⚠️  Tap directory already exists: ../$TAP_NAME"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create tap directory structure
TAP_DIR="../$TAP_NAME"
mkdir -p "$TAP_DIR/Formula"

# Copy formula
echo "📋 Copying formula..."
cp Formula/podcrack.rb "$TAP_DIR/Formula/"

# Check if we need to create a git tag
if ! git tag -l | grep -q "^v1.0.0$"; then
    echo ""
    echo "⚠️  Git tag v1.0.0 not found."
    read -p "Create tag v1.0.0 now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag v1.0.0
        echo "✅ Created tag v1.0.0"
        echo "   Don't forget to push it: git push origin v1.0.0"
    fi
fi

# Calculate SHA256 if tag exists
if git tag -l | grep -q "^v1.0.0$"; then
    echo ""
    echo "📦 Calculating SHA256 for release tarball..."
    TARBALL_URL="https://github.com/$GITHUB_USER/$REPO_NAME/archive/refs/tags/v1.0.0.tar.gz"
    SHA256=$(curl -sL "$TARBALL_URL" | shasum -a 256 | awk '{print $1}')
    
    if [ -n "$SHA256" ]; then
        echo "✅ SHA256: $SHA256"
        echo ""
        echo "Updating formula with SHA256..."
        sed -i '' "s/sha256 \"\"/sha256 \"$SHA256\"/" "$TAP_DIR/Formula/podcrack.rb"
        echo "✅ Formula updated"
    else
        echo "⚠️  Could not calculate SHA256. Make sure the GitHub release exists."
        echo "   You'll need to update the sha256 field manually in Formula/podcrack.rb"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create GitHub repository: $TAP_NAME"
echo "2. Initialize git in tap directory:"
echo "   cd $TAP_DIR"
echo "   git init"
echo "   git add Formula/podcrack.rb"
echo "   git commit -m 'Add podcrack formula'"
echo "   git remote add origin git@github.com:$GITHUB_USER/$TAP_NAME.git"
echo "   git push -u origin main"
echo ""
echo "3. Create a GitHub release for podcrack (if not already done):"
echo "   https://github.com/$GITHUB_USER/$REPO_NAME/releases/new"
echo ""
echo "4. Users can then install with:"
echo "   brew tap $GITHUB_USER/podcrack"
echo "   brew install podcrack"
