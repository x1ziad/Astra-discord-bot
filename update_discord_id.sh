#!/bin/bash
# Discord ID Update Script
# Run this script after getting your real Discord ID

echo "🔧 Discord ID Update Script"
echo "=========================="
echo ""
echo "Current owner_id in config.json: $(grep 'owner_id' config/config.json)"
echo ""
echo "Please enter your REAL Discord User ID:"
read -p "Discord ID: " DISCORD_ID

# Validate that it's a number and reasonable length
if [[ $DISCORD_ID =~ ^[0-9]{17,19}$ ]]; then
    echo ""
    echo "✅ Valid Discord ID format: $DISCORD_ID"
    echo "Updating config.json..."
    
    # Backup current config
    cp config/config.json config/config.json.backup
    
    # Update the owner_id in config.json
    sed -i '' "s/\"owner_id\": \"[0-9]*\"/\"owner_id\": \"$DISCORD_ID\"/" config/config.json
    
    echo "✅ Updated config.json successfully!"
    echo "📋 Backup saved as config/config.json.backup"
    echo ""
    echo "New owner_id: $(grep 'owner_id' config/config.json)"
    echo ""
    echo "🚀 Your bot is now configured with YOUR Discord ID!"
    echo "🔐 The /admin shutdown command will now work only for you."
else
    echo "❌ Invalid Discord ID format. Discord IDs should be 17-19 digits."
    echo "Please run the script again with your correct Discord ID."
    exit 1
fi
