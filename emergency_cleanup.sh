#!/bin/bash
# Emergency API key cleanup script

echo "🚨 EMERGENCY: Removing exposed API key from all files..."

# The old exposed key that needs to be removed
OLD_KEY="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"
PLACEHOLDER="YOUR_OPENROUTER_API_KEY_HERE"

# Files to clean
files=(
    "ai/universal_ai_client.py"
    "ai/openrouter_client.py"
    "OPENROUTER_SETUP.md"
    "UNIVERSAL_AI_SETUP.md"
    "AI_TESTING_RESULTS.md"
    "test_universal_ai_integration.py"
    "test_discord_ai_commands.py"
    "ISSUE_RESOLUTION_SUMMARY.md"
    "railway_diagnostic.py"
    "fix_railway_env.py"
    "railway_setup_guide.py"
    "DEPLOYMENT_READY.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "🔧 Cleaning $file..."
        sed -i.bak "s/$OLD_KEY/$PLACEHOLDER/g" "$file"
        rm "$file.bak" 2>/dev/null || true
    fi
done

echo "✅ All files cleaned. The old API key has been replaced with placeholder."
echo "🔑 Don't forget to:"
echo "   1. Revoke the old key at https://openrouter.ai/keys"
echo "   2. Generate a new key"
echo "   3. Set the new key in Railway dashboard"
