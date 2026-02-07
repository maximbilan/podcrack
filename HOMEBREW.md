# Homebrew Installation Guide

This guide explains how to install podcrack via Homebrew. The formula is included directly in this repository, so no separate tap repository is needed.

## Option 1: Tap and Install (Recommended)

Tap this repository and install:

```bash
brew tap maximbilan/podcrack https://github.com/maximbilan/podcrack.git
brew install podcrack
```

After tapping once, you can use `brew install podcrack` and `brew upgrade podcrack` normally.

## Option 2: Direct Formula Installation

Install directly from the formula URL without tapping:

```bash
brew install --formula https://raw.githubusercontent.com/maximbilan/podcrack/main/Formula/podcrack.rb
```

This method doesn't add a tap, but you'll need to use the full URL for upgrades.

## Option 3: Install from Local Formula (Development)

For testing or development, you can install directly from a local formula file:

```bash
brew install --build-from-source /path/to/podcrack/Formula/podcrack.rb
```

## Updating the Formula

When you release a new version:

1. Create a new git tag (e.g., `v1.1.0`) and push it:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

2. Create a GitHub release for the tag

3. Update the `url` and `sha256` in `Formula/podcrack.rb`:
   - Calculate the new SHA256:
     ```bash
     curl -L https://github.com/maximbilan/podcrack/archive/refs/tags/v1.1.0.tar.gz | shasum -a 256
     ```
   - Update the formula file with the new version and SHA256

4. Commit and push the changes to this repository

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
3. Update the formula in this repository

### Installation Issues

If installation fails:
- Check that Python 3.10+ is available: `python3 --version`
- Try installing with verbose output: `brew install -v --formula <url>`
- Check Homebrew logs: `brew install --debug --formula <url>`
- Make sure you're using the latest formula from the main branch

### Formula Not Found

If Homebrew can't find the formula:
- Ensure you're using the correct URL format
- Check that the `Formula/podcrack.rb` file exists in the main branch
- Try the direct URL installation method instead of tapping
