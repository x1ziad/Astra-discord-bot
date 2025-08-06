# 🔧 Configuration Setup Guide

## Quick Setup with Environment Variables

The easiest way to configure Astra Bot is using a `.env` file:

1. **Create a `.env` file** in the root directory:
   ```bash
   touch .env
   ```

2. **Add your API keys** to the `.env` file:
   ```env
   # Discord Bot Configuration
   DISCORD_TOKEN=your_discord_bot_token_here
   DISCORD_CLIENT_ID=your_discord_client_id_here

   # AI Services
   OPENAI_API_KEY=your_openai_api_key_here
   OPENROUTER_API_KEY=your_openrouter_key_here

   # Image Generation
   FREEPIK_API_KEY=your_freepik_api_key_here

   # NASA API (Optional)
   NASA_API_KEY=your_nasa_api_key_here
   ```

## 🔑 Where to Get API Keys

### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select existing one
3. Go to "Bot" section
4. Copy the bot token
5. Enable necessary intents (Message Content Intent, Server Members Intent)

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

### OpenRouter API Key (Alternative to OpenAI)
1. Go to [OpenRouter](https://openrouter.ai/keys)
2. Sign up and create an API key
3. Provides access to multiple AI models

### Freepik API Key (For Image Generation)
1. Visit [Freepik API](https://www.freepik.com/api)
2. Sign up for developer access
3. Create an API key

### NASA API Key (Optional)
1. Go to [NASA Open Data Portal](https://api.nasa.gov/)
2. Sign up for a free API key
3. Used for space-related content

## 🛡️ Security Best Practices

- ✅ **Never commit the `.env` file** - it's automatically ignored by git
- ✅ **Use different keys for development and production**
- ✅ **Regularly rotate your API keys**
- ✅ **Monitor API usage and costs**
- ❌ **Don't share API keys in screenshots or logs**
- ❌ **Don't commit real keys to version control**

## 🚀 Alternative Configuration Methods

### Method 2: Environment Variables (Production)
Set environment variables directly on your hosting platform:
```bash
export DISCORD_TOKEN="your_token_here"
export OPENAI_API_KEY="your_key_here"
# ... etc
```

### Method 3: Config File (Not Recommended)
If you must use a config file:
1. Copy `config/config.json` to `config/config.local.json`
2. Edit `config.local.json` with your keys
3. The `.local.json` file is automatically ignored by git

## 🔧 Testing Your Setup

1. **Start the bot**:
   ```bash
   python bot.1.0.py
   ```

2. **Check the logs** for any configuration errors

3. **Test basic commands** in Discord:
   - `/ai_status` - Check AI system status
   - `/ai_test` - Test AI response generation
   - `astra generate sunset` - Test image generation

## 🆘 Troubleshooting

### Common Issues:
- **"Invalid Token"**: Check your Discord bot token
- **"API Key Error"**: Verify your API keys are correct
- **"Permission Denied"**: Ensure bot has necessary Discord permissions
- **"Rate Limited"**: Check API usage limits

### Getting Help:
- Check the console logs for specific error messages
- Verify all required permissions are granted
- Test API keys independently
- Ensure all dependencies are installed

## 📋 Required Bot Permissions

Ensure your Discord bot has these permissions:
- ✅ Send Messages
- ✅ Use Slash Commands
- ✅ Embed Links
- ✅ Attach Files
- ✅ Read Message History
- ✅ Add Reactions
- ✅ Use External Emojis
