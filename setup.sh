#!/bin/bash

# Astra Discord Bot - Setup Script
# This script helps you set up the bot with Docker

set -e

echo "🚀 Astra Discord Bot Setup"
echo "========================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit the .env file with your API keys:"
    echo "   - DISCORD_TOKEN=your-discord-bot-token"
    echo "   - OPENAI_API_KEY=sk-your-openai-api-key"
    echo ""
    echo "   Open .env in your text editor and add your keys."
    echo "   Then run this script again."
    exit 0
fi

# Check if required environment variables are set
source .env

if [ -z "$DISCORD_TOKEN" ] || [ "$DISCORD_TOKEN" = "your-discord-bot-token-here" ]; then
    echo "❌ DISCORD_TOKEN is not set in .env file"
    echo "   Get your token from: https://discord.com/developers/applications"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-openai-api-key-here" ]; then
    echo "❌ OPENAI_API_KEY is not set in .env file"
    echo "   Get your key from: https://platform.openai.com/api-keys"
    exit 1
fi

echo "✅ Environment variables configured"

# Choose deployment mode
echo ""
echo "Choose deployment mode:"
echo "1) Production (recommended)"
echo "2) Development (live code reloading)"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "🚀 Starting in production mode..."
        docker-compose up -d
        echo ""
        echo "✅ Bot is running in the background!"
        echo "   View logs: docker-compose logs -f"
        echo "   Stop bot: docker-compose down"
        ;;
    2)
        echo "🔧 Starting in development mode..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac