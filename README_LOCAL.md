# 🚀 AstraBot Local Deployment - Ready to Launch!

## Quick Start (3 Steps)

### Step 1: Configure Your Bot ⚙️
```bash
python3 setup_bot.py
```
This interactive script will help you:
- Set up Discord bot token
- Configure AI provider
- Generate bot invite link

### Step 2: Deploy Locally 🚀
```bash
./deploy_local.sh
```
This will:
- Install dependencies automatically
- Start the bot with auto-restart
- Keep running as long as your device is on

### Step 3: Invite to Discord 🤖
Use the invite link from Step 1 to add your bot to a server.

---

## What You Get

### 🤖 **Enhanced AI Companion**
- Natural conversation flow with context awareness
- Dynamic personality that adapts to conversation
- Multiple AI provider support (OpenAI, Google Gemini, GitHub Models, etc.)
- Smart response generation with conversation history

### 🔄 **Continuous Operation**
- Auto-restart if bot crashes
- Runs 24/7 as long as your device is on
- Comprehensive error handling and recovery
- Real-time status monitoring

### 📊 **Performance Optimized**
- Fast response times (sub-second)
- Intelligent caching system
- Memory optimization
- Enhanced logging and monitoring

### 🛡️ **Production Ready**
- Secure configuration management
- Rate limiting and spam protection
- Comprehensive error handling
- Local SQLite database

---

## Scripts Available

| Script | Purpose |
|--------|---------|
| `setup_bot.py` | Interactive setup for Discord and AI configuration |
| `check_config.py` | Verify your configuration is correct |
| `deploy_local.sh` | Full deployment with auto-restart |
| `start_astra.py` | Direct bot startup (manual) |

---

## File Structure

```
AstraBot/
├── 🚀 deploy_local.sh      # Main deployment script
├── ⚙️ setup_bot.py         # Interactive configuration
├── 🔍 check_config.py      # Configuration checker
├── 📋 LOCAL_DEPLOYMENT_GUIDE.md  # Detailed guide
├── .env                    # Your configuration
├── bot.1.0.py             # Main bot application
├── requirements.txt       # Dependencies
├── data/                  # Local database
├── logs/                  # Log files
└── cogs/                  # Bot features
```

---

## Troubleshooting

### Configuration Issues
- Run `python3 check_config.py` to verify setup
- Edit `.env` file directly if needed
- Re-run `python3 setup_bot.py` to reconfigure

### Bot Not Responding
1. Check terminal for error messages
2. Verify bot has permissions in Discord server
3. Ensure API keys are valid
4. Check internet connection

### Performance Issues
- Monitor `logs/` directory for errors
- Ensure adequate RAM (2GB+ recommended)
- Use SSD storage for better performance

---

## Getting API Keys

### Discord Bot Token (Required)
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create new application
3. Bot section → Reset Token

### AI Providers (At least one required)

**Free Options:**
- **GitHub Models**: [GitHub Settings](https://github.com/settings/personal-access-tokens/tokens)
- **Google Gemini**: [AI Studio](https://aistudio.google.com/app/apikey)

**Paid Options:**
- **OpenAI**: [Platform](https://platform.openai.com/api-keys)
- **OpenRouter**: [Keys](https://openrouter.ai/keys)

---

## Ready to Deploy? 🎯

1. **Run Setup**: `python3 setup_bot.py`
2. **Deploy**: `./deploy_local.sh` 
3. **Enjoy**: Your AI bot is now running locally!

Your AstraBot will have:
- ✅ Enhanced conversation capabilities
- ✅ Multiple AI provider support
- ✅ Auto-restart functionality
- ✅ Comprehensive monitoring
- ✅ 24/7 operation (while device is on)

Need help? Check `LOCAL_DEPLOYMENT_GUIDE.md` for detailed instructions!