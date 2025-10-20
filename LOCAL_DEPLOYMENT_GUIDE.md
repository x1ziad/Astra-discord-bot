# 🚀 AstraBot Local Deployment Guide

## Quick Start - Deploy Locally Right Now!

### 1. **One-Command Deployment** ⚡
```bash
./deploy_local.sh
```

This script will:
- ✅ Check Python version (3.8+ required)
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Set up configuration
- ✅ Start the bot with auto-restart
- ✅ Keep running as long as your device is on

### 2. **Required Configuration** 🔑

Before running, you need to configure these essential settings in your `.env` file:

#### **Discord Bot Setup** (Required)
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Copy the token and add to `.env`:
```bash
DISCORD_TOKEN=your_actual_discord_bot_token
DISCORD_CLIENT_ID=your_client_id
```

#### **AI Provider Setup** (At least one required)
Choose any of these AI providers:

**Option A: OpenAI (Recommended)**
```bash
OPENAI_API_KEY=sk-your-openai-api-key
```

**Option B: Google Gemini (Free tier available)**
```bash
GOOGLE_API_KEY=your-google-gemini-api-key
```

**Option C: GitHub Models (Free)**
```bash
GITHUB_TOKEN=your-github-personal-access-token
```

**Option D: OpenRouter (Multiple models)**
```bash
OPENROUTER_API_KEY=your-openrouter-api-key
```

### 3. **Optional Enhancements** 🎯

Add these to your `.env` for additional features:

```bash
# Your Discord User ID (for admin commands)
OWNER_ID=your_discord_user_id

# NASA API for space commands
NASA_API_KEY=your_nasa_api_key

# Performance optimization
MAX_WORKERS=4
ENABLE_PERFORMANCE_MONITORING=true
```

### 4. **Invite Bot to Your Server** 🤖

After starting the bot, use this URL format to invite it:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands
```

Replace `YOUR_CLIENT_ID` with your actual client ID.

### 5. **Local Deployment Features** 🌟

Your local deployment includes:

- **🔄 Auto-Restart**: Bot automatically restarts if it crashes
- **📱 Always Online**: Runs as long as your device is on
- **🚀 Performance Optimized**: Enhanced AI conversation flow
- **📋 Comprehensive Logging**: All activity logged to `logs/` directory
- **🛡️ Error Handling**: Graceful error recovery and reporting
- **💾 Local Database**: SQLite database in `data/` directory

### 6. **Managing Your Local Bot** ⚙️

#### **Start the Bot**
```bash
./deploy_local.sh
```

#### **Stop the Bot**
Press `Ctrl+C` in the terminal where it's running

#### **View Logs**
```bash
tail -f logs/astra.log
```

#### **Check Bot Status**
The terminal will show real-time status updates

### 7. **Troubleshooting** 🔧

#### **Common Issues:**

**"DISCORD_TOKEN not configured"**
- Edit `.env` file and add your Discord bot token

**"No AI provider configured"**
- Add at least one AI API key to `.env` file

**"Permission denied"**
- Run: `chmod +x deploy_local.sh`

**Bot not responding in Discord:**
- Check if bot has proper permissions in your server
- Verify the bot is online (green dot in Discord)

#### **Get Help:**
1. Check the `logs/` directory for error messages
2. Ensure all API keys are valid
3. Verify Discord bot permissions

### 8. **Performance Tips** ⚡

For optimal performance:

- **Use SSD storage** for faster database operations
- **Keep terminal open** while bot is running
- **Monitor memory usage** in Activity Monitor
- **Use stable internet connection** for AI responses

### 9. **Local vs Cloud Deployment** 🌐

**Local Deployment (This Guide):**
- ✅ Free hosting
- ✅ Full control
- ✅ Instant updates
- ❌ Requires device to stay on
- ❌ Dependent on home internet

**Cloud Deployment:**
- ✅ 24/7 uptime
- ✅ Better reliability
- ❌ Monthly hosting costs
- ❌ More complex setup

### 10. **Advanced Configuration** 🔬

#### **Custom Settings in `.env`:**
```bash
# Bot behavior
COMMAND_PREFIX=!
AUTO_RESPONSE_ENABLED=true
NATURAL_CONVERSATION=true

# Performance
MAX_RESPONSE_TIME=30
ENABLE_RESPONSE_CACHING=true
CACHE_SIZE=1000

# Security
RATE_LIMIT_ENABLED=true
MAX_REQUESTS_PER_MINUTE=60
```

#### **Multiple AI Providers:**
You can configure multiple AI providers for redundancy:
```bash
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
OPENROUTER_API_KEY=your_openrouter_key
```

The bot will automatically switch between providers if one fails.

---

## 🎉 You're Ready to Deploy!

Run this command to start your local AstraBot deployment:

```bash
./deploy_local.sh
```

Your bot will be online and ready to chat with enhanced AI conversation capabilities! 🚀