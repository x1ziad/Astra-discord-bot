#!/bin/bash
# Astra Bot Environment Setup Script
# This script helps you set up all necessary environment variables

echo "🚀 Astra Bot Environment Setup"
echo "================================"
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "📄 Found existing .env file"
    echo "Current contents:"
    echo "----------------"
    cat .env
    echo "----------------"
    echo ""
    read -p "Do you want to edit the existing .env file? (y/n): " edit_existing
    if [ "$edit_existing" != "y" ]; then
        exit 0
    fi
    echo ""
else
    echo "📄 Creating new .env file..."
fi

# Create or update .env file
echo "# Astra Bot Environment Variables" > .env
echo "# Generated on $(date)" >> .env
echo "" >> .env

# Required variables
echo "🔸 REQUIRED VARIABLES"
echo "--------------------"

echo "# Discord Bot Token (REQUIRED - Get from https://discord.com/developers/applications)" >> .env
read -p "Enter your Discord Bot Token: " discord_token
if [ -n "$discord_token" ]; then
    echo "DISCORD_TOKEN=$discord_token" >> .env
else
    echo "DISCORD_TOKEN=your_discord_bot_token_here" >> .env
    echo "⚠️ WARNING: Discord token is required for the bot to work!"
fi
echo "" >> .env

# Optional but recommended variables
echo ""
echo "🔸 OPTIONAL BUT RECOMMENDED"
echo "---------------------------"

echo "# NASA API Key (Optional - Get from https://api.nasa.gov/)" >> .env
read -p "Enter your NASA API Key (or press Enter to use DEMO_KEY): " nasa_key
if [ -n "$nasa_key" ]; then
    echo "NASA_API_KEY=$nasa_key" >> .env
else
    echo "# NASA_API_KEY=your_nasa_api_key_here" >> .env
    echo "💡 Using DEMO_KEY (limited to 50 requests/day)"
fi
echo "" >> .env

# AI Features
echo ""
echo "🔸 AI FEATURES (Optional)"
echo "------------------------"

echo "# OpenAI API Key (Optional - Get from https://platform.openai.com/api-keys)" >> .env
read -p "Enter your OpenAI API Key (or press Enter to skip): " openai_key
if [ -n "$openai_key" ]; then
    echo "OPENAI_API_KEY=$openai_key" >> .env
else
    echo "# OPENAI_API_KEY=your_openai_api_key_here" >> .env
fi
echo "" >> .env

echo "# Anthropic API Key (Optional - Get from https://console.anthropic.com/)" >> .env
read -p "Enter your Anthropic API Key (or press Enter to skip): " anthropic_key
if [ -n "$anthropic_key" ]; then
    echo "ANTHROPIC_API_KEY=$anthropic_key" >> .env
else
    echo "# ANTHROPIC_API_KEY=your_anthropic_api_key_here" >> .env
fi
echo "" >> .env

# Notion Integration
echo ""
echo "🔸 NOTION INTEGRATION (Optional)"
echo "-------------------------------"

echo "# Notion API Token (Optional - Get from https://www.notion.so/my-integrations)" >> .env
read -p "Enter your Notion API Token (or press Enter to skip): " notion_token
if [ -n "$notion_token" ]; then
    echo "NOTION_TOKEN=$notion_token" >> .env
else
    echo "# NOTION_TOKEN=your_notion_token_here" >> .env
fi

echo "# Notion Database ID (Optional)" >> .env
read -p "Enter your Notion Database ID (or press Enter to skip): " notion_db
if [ -n "$notion_db" ]; then
    echo "NOTION_DATABASE_ID=$notion_db" >> .env
else
    echo "# NOTION_DATABASE_ID=your_notion_database_id_here" >> .env
fi

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "📄 Generated .env file:"
echo "======================"
cat .env
echo "======================"
echo ""

# Check if Discord token is set
if grep -q "DISCORD_TOKEN=your_discord_bot_token_here" .env || ! grep -q "DISCORD_TOKEN=" .env; then
    echo "⚠️  WARNING: Discord token not set!"
    echo "🚫 The bot cannot start without a valid Discord token."
    echo ""
    echo "To get a Discord bot token:"
    echo "1. Go to https://discord.com/developers/applications"
    echo "2. Create a new application"
    echo "3. Go to the 'Bot' section"
    echo "4. Create a bot and copy the token"
    echo "5. Add the token to your .env file"
    echo ""
else
    echo "🎉 Bot is ready to start!"
    echo ""
    echo "To run the bot:"
    echo "==============="
    echo "python bot.1.0.py"
    echo ""
fi

echo "📋 Feature Status:"
echo "=================="
echo "✅ Space Features: Ready (6 commands available)"
echo "✅ AI Conversation: Ready (advanced features)"
echo "✅ ISS Tracking: Ready (real-time data)"
echo "✅ NASA Integration: Ready (APOD, space data)"
echo "⭕ Advanced AI: Depends on API keys"
echo "⭕ Notion Integration: Depends on tokens"
echo ""
echo "🔗 Documentation:"
echo "================="
echo "• Environment Setup: ENVIRONMENT_SETUP.md"
echo "• AI Features: AI_FEATURES_SUMMARY.md" 
echo "• Complete Guide: ENHANCED_AI_COMPLETE.md"
echo ""
echo "🚀 Available Commands:"
echo "====================="
echo "• /space apod - NASA Astronomy Picture of the Day"
echo "• /space fact - Random space fact"
echo "• /space iss - Track the International Space Station"
echo "• /space meteor - Meteor shower information"
echo "• /space launch - Space launch information"
echo "• /space planets [name] - Solar system information"
echo "• /ai_stats - AI conversation statistics"
echo "• /ai_mood - Conversation mood analysis"
echo "• /ai_topics - Trending conversation topics"
echo "• /ai_personality - Customize AI personality"
echo "• /ai_engage - Manual AI engagement"
