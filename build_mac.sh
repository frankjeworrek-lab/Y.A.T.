#!/bin/bash
set -e

echo "🏗️  Building Y.A.T. macOS App..."

# Ensure pyinstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
fi

# 1. Prepare Icon
echo "🎨 Generating .icns from logo/dock.png..."
rm -rf build/icon.iconset
mkdir -p build/icon.iconset

sips -z 16 16     logo/dock.png --out build/icon.iconset/icon_16x16.png > /dev/null
sips -z 32 32     logo/dock.png --out build/icon.iconset/icon_16x16@2x.png > /dev/null
sips -z 32 32     logo/dock.png --out build/icon.iconset/icon_32x32.png > /dev/null
sips -z 64 64     logo/dock.png --out build/icon.iconset/icon_32x32@2x.png > /dev/null
sips -z 128 128   logo/dock.png --out build/icon.iconset/icon_128x128.png > /dev/null
sips -z 256 256   logo/dock.png --out build/icon.iconset/icon_128x128@2x.png > /dev/null
sips -z 256 256   logo/dock.png --out build/icon.iconset/icon_256x256.png > /dev/null
sips -z 512 512   logo/dock.png --out build/icon.iconset/icon_256x256@2x.png > /dev/null
sips -z 512 512   logo/dock.png --out build/icon.iconset/icon_512x512.png > /dev/null
# Note: 1024x1024 requires source image to be large enough, defaulting to 512 if not
sips -z 512 512   logo/dock.png --out build/icon.iconset/icon_512x512@2x.png > /dev/null

iconutil -c icns build/icon.iconset -o build/YAT.icns

# 2. Build App
echo "🔨 Running PyInstaller..."
# Note: We use --collect-all nicegui to ensure all templates are included
# We manually add data folders.

pyinstaller main.py \
    --name "Y.A.T." \
    --windowed \
    --icon "build/YAT.icns" \
    --add-data "logo:logo" \
    --add-data "ui_nicegui:ui_nicegui" \
    --add-data "core:core" \
    --add-data "plugins:plugins" \
    --add-data "storage:storage" \
    --add-data ".env:." \
    --add-data "docs:docs" \
    --collect-all nicegui \
    --collect-all webview \
    --clean \
    --noconfirm

echo "✨ Build Complete!"
echo "👉 You can now drag 'dist/Y.A.T.app' to your Applications folder or Dock."
