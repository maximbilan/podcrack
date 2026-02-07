# Homebrew Installation Guide

This guide explains how to set up podcrack as a Homebrew formula.

## Option 1: Create a Homebrew Tap (Recommended)

A Homebrew tap is a separate GitHub repository that contains your formula. This is the standard way to distribute personal or third-party formulas.

### Step 1: Create the Tap Repository

1. Create a new GitHub repository named `homebrew-podcrack` (or `homebrew-tap` if you want to host multiple formulas)
2. Clone it locally:
   ```bash
   git clone git@github.com:maximbilan/homebrew-podcrack.git
   cd homebrew-podcrack
   ```

### Step 2: Add the Formula

1. Copy the formula file:
   ```bash
   mkdir -p Formula
   cp /path/to/podcrack/Formula/podcrack.rb Formula/
   ```

2. Update the SHA256 hash in the formula:
   - First, create a GitHub release with tag `v1.0.0`:
     ```bash
     cd /path/to/podcrack
     git tag v1.0.0
     git push origin v1.0.0
     ```
   - Then create a release on GitHub (https://github.com/maximbilan/podcrack/releases/new)
   - Download the tarball and calculate its SHA256:
     ```bash
     curl -L https://github.com/maximbilan/podcrack/archive/refs/tags/v1.0.0.tar.gz | shasum -a 256
     ```
   - Update the `sha256` field in `Formula/podcrack.rb` with this value

3. Commit and push:
   ```bash
   git add Formula/podcrack.rb
   git commit -m "Add podcrack formula"
   git push origin main
   ```

### Step 3: Install from Tap

Users can now install podcrack with:
```bash
brew tap maximbilan/podcrack
brew install podcrack
```

Or in one command:
```bash
brew install maximbilan/podcrack/podcrack
```

## Option 2: Install from Local Formula

For testing, you can install directly from the local formula:

```bash
brew install --build-from-source /path/to/podcrack/Formula/podcrack.rb
```

## Updating the Formula

When you release a new version:

1. Create a new git tag and GitHub release
2. Update the `url` and `sha256` in the formula
3. Update the version number if needed
4. Commit and push the changes to your tap repository

## Formula Details

The formula:
- Uses Python 3.10+ (as required by podcrack)
- Installs the package using pip
- Creates a `podcrack` command in the user's PATH
- Includes a basic test to verify installation

## Troubleshooting

### SHA256 Mismatch

If you get a SHA256 mismatch error:
1. Make sure the GitHub release tarball URL is correct
2. Recalculate the SHA256: `curl -L <url> | shasum -a 256`
3. Update the formula

### Installation Issues

If installation fails:
- Check that Python 3.10+ is available: `python3 --version`
- Try installing with verbose output: `brew install -v podcrack`
- Check Homebrew logs: `brew install --debug podcrack`
