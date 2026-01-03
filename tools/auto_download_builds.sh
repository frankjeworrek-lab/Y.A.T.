#!/bin/bash
# Auto-Download GitHub Actions Build Artifacts
# Usage: ./tools/auto_download_builds.sh [tag]
# Example: ./tools/auto_download_builds.sh v0.2.11

set -e  # Exit on error

TAG=${1:-$(git describe --tags --abbrev=0)}  # Use provided tag or latest

echo "🚀 Y.A.T. Build Auto-Download"
echo "================================"
echo "Tag: $TAG"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found!"
    echo "Install: brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub!"
    echo "Run: gh auth login"
    exit 1
fi

echo "⏳ Waiting for builds to complete..."
echo "   This may take 5-10 minutes. You can continue working."
echo ""

# Watch the latest workflow run (blocks until complete)
# If no runs are in progress, 'gh run watch' exits with 1. We assume this means they are done.
echo "   Checking build status..."
gh run watch --exit-status || {
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 1 ]; then
        echo "   ℹ️  No active builds found. Assuming builds are already complete."
    else
        echo "❌ Build failed or was cancelled!"
        exit 1
    fi
}

echo ""
echo "📥 Downloading build artifacts..."

# Create builds directory
mkdir -p builds/windows builds/mac

# Download Windows build
echo "   → Windows Edition..."
gh run download --name "Y.A.T.-Windows-Edition" --dir builds/windows 2>/dev/null || {
    echo "     ⚠️  Windows build not found (workflow may have failed)"
}

# Download Mac builds
echo "   → Mac Edition (App Bundle)..."
gh run download --name "Y.A.T.-Mac-Edition-App" --dir builds/mac 2>/dev/null || {
    echo "     ⚠️  Mac App build not found (workflow may have failed)"
}

echo "   → Mac Edition (DMG)..."
gh run download --name "Y.A.T.-Mac-Edition-DMG" --dir builds/mac 2>/dev/null || {
    echo "     ⚠️  Mac DMG build not found (workflow may have failed)"
}

echo ""
echo "✅ Build download complete!"
echo ""
echo "📂 Builds available at:"
echo "   Windows: ./builds/windows/"
echo "   Mac:     ./builds/mac/"
echo ""

# macOS Desktop Notification (silent fail if not on macOS)
osascript -e 'display notification "Builds downloaded and ready!" with title "Y.A.T. Build Complete"' 2>/dev/null || true

# List downloaded files
echo "📋 Downloaded files:"
ls -lh builds/windows/ 2>/dev/null || echo "   (no Windows builds)"
ls -lh builds/mac/ 2>/dev/null || echo "   (no Mac builds)"
