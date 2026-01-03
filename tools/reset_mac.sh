#!/bin/bash

# Define the target directory
TARGET="$HOME/.yat"

echo "=================================="
echo "    Y.A.T. FACTORY RESET (MAC)    "
echo "=================================="
echo "Target: $TARGET"
echo ""

if [ -d "$TARGET" ]; then
    echo "⚠️  WARNING: This will delete ALL data in .yat:"
    echo "   - API Keys (.env)"
    echo "   - Provider Settings (provider_config.json)"
    echo "   - User Preferences (user_config.json)"
    echo "   - Chat History"
    echo ""
    read -p "Are you sure you want to proceed? (y/N): " CONFIRM

    if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
        rm -rf "$TARGET"
        echo "✅ [OK] Directory deleted. App is effectively new."
    else
        echo "🚫 [INFO] Aborted."
    fi
else
    echo "ℹ️  [INFO] Directory $TARGET does not exist. Already clean."
fi
echo ""
