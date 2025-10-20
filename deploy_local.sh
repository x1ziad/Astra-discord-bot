#!/bin/bash

# ================================
# 🚀 ASTRA BOT LOCAL DEPLOYMENT SCRIPT
# ================================
# This script sets up and runs AstraBot locally on your machine
# It will keep running as long as your device is on

echo "🚀 AstraBot Local Deployment Starting..."
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "bot.1.0.py" ]; then
    print_error "bot.1.0.py not found. Please run this script from the AstraBot directory."
    exit 1
fi

print_status "Found AstraBot directory"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_info "Python version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 0 ]]; then
    print_error "Python 3.8 or higher required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv .venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment found"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source .venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_status "Pip upgraded"

# Install dependencies
print_info "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    mkdir -p data
    print_status "Data directory created"
fi

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    mkdir -p logs
    print_status "Logs directory created"
fi

# Check .env configuration
print_info "Checking configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f "config/.env.template" ]; then
        cp config/.env.template .env
        print_warning "Please edit .env file with your API keys before running the bot"
        print_info "Required: DISCORD_TOKEN and at least one AI provider API key"
        read -p "Press Enter to open .env file for editing, or Ctrl+C to exit..."
        ${EDITOR:-nano} .env
    else
        print_error "No .env template found"
        exit 1
    fi
fi

# Validate essential environment variables
print_info "Validating configuration..."
source .env

if [ -z "$DISCORD_TOKEN" ] || [ "$DISCORD_TOKEN" = "your_discord_bot_token_here" ]; then
    print_error "DISCORD_TOKEN not configured in .env file"
    print_info "Please set your Discord bot token in .env file"
    exit 1
fi

# Check if at least one AI provider is configured
AI_CONFIGURED=false
if [ ! -z "$OPENAI_API_KEY" ] && [ "$OPENAI_API_KEY" != "your_openai_api_key_here" ]; then
    AI_CONFIGURED=true
    print_status "OpenAI API configured"
fi

if [ ! -z "$GOOGLE_API_KEY" ] && [ "$GOOGLE_API_KEY" != "your_google_gemini_api_key_here" ]; then
    AI_CONFIGURED=true
    print_status "Google Gemini API configured"
fi

if [ ! -z "$OPENROUTER_API_KEY" ] && [ "$OPENROUTER_API_KEY" != "your_openrouter_api_key_here" ]; then
    AI_CONFIGURED=true
    print_status "OpenRouter API configured"
fi

if [ ! -z "$MISTRAL_API_KEY" ] && [ "$MISTRAL_API_KEY" != "your_mistral_api_key_here" ]; then
    AI_CONFIGURED=true
    print_status "Mistral AI API configured"
fi

if [ ! -z "$GITHUB_TOKEN" ] && [ "$GITHUB_TOKEN" != "your_github_personal_access_token_here" ]; then
    AI_CONFIGURED=true
    print_status "GitHub Models API configured"
fi

if [ "$AI_CONFIGURED" = false ]; then
    print_error "No AI provider configured. Please set at least one API key in .env file"
    print_info "Supported providers: OpenAI, Google Gemini, OpenRouter, Mistral, GitHub Models"
    exit 1
fi

print_status "Configuration validated"

# Function to handle graceful shutdown
cleanup() {
    print_info "Shutting down AstraBot..."
    if [ ! -z "$BOT_PID" ]; then
        kill $BOT_PID 2>/dev/null
    fi
    print_status "AstraBot stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the bot
print_status "Configuration complete! Starting AstraBot..."
echo "================================="
print_info "🤖 AstraBot will now start and run continuously"
print_info "📱 The bot will stay online as long as this device is on"
print_info "🔄 Press Ctrl+C to stop the bot gracefully"
print_info "📋 Logs will be saved to the logs/ directory"
echo "================================="

# Start the bot with automatic restart on failure
RESTART_COUNT=0
MAX_RESTARTS=5

while true; do
    print_info "Starting AstraBot (attempt $((RESTART_COUNT + 1)))..."
    
    # Start the bot
    python3 start_astra.py &
    BOT_PID=$!
    
    # Wait for the bot process
    wait $BOT_PID
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        print_status "AstraBot exited normally"
        break
    else
        print_warning "AstraBot crashed with exit code $EXIT_CODE"
        
        # Increment restart counter
        RESTART_COUNT=$((RESTART_COUNT + 1))
        
        if [ $RESTART_COUNT -ge $MAX_RESTARTS ]; then
            print_error "Maximum restart attempts reached ($MAX_RESTARTS). Stopping."
            break
        fi
        
        print_info "Restarting in 10 seconds... (attempt $((RESTART_COUNT + 1))/$MAX_RESTARTS)"
        sleep 10
    fi
done

cleanup