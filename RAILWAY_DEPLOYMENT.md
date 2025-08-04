# 🚄 Astra Bot - Railway Deployment Guide

## Quick Railway Setup

### 1. **Environment Variables Setup**
Set these variables in your Railway dashboard:

#### Required Variables
```
DISCORD_TOKEN=your_discord_bot_token
DISCORD_CLIENT_ID=your_discord_application_id
OPENAI_API_KEY=your_openai_api_key
```

#### Optional Variables
```
OPENAI_MODEL=gpt-4                    # Default: gpt-4
OPENAI_MAX_TOKENS=2000                # Default: 2000
OPENAI_TEMPERATURE=0.7                # Default: 0.7
NASA_API_KEY=your_nasa_api_key        # Default: DEMO_KEY
DEBUG_MODE=false                      # Default: false
LOG_LEVEL=INFO                        # Default: INFO
```

### 2. **Discord Bot Setup**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select existing one
3. Go to "Bot" section
4. Copy the bot token → Set as `DISCORD_TOKEN`
5. Go to "General Information"
6. Copy Application ID → Set as `DISCORD_CLIENT_ID`

### 3. **OpenAI API Setup**
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an API key
3. Copy the key → Set as `OPENAI_API_KEY`

### 4. **Railway Deployment**
1. Connect your GitHub repository to Railway
2. Deploy from the main branch
3. Railway will automatically:
   - Detect Dockerfile
   - Build the container
   - Deploy with your environment variables

---

## Advanced Configuration

### NASA API (Optional)
For enhanced space content:
```
NASA_API_KEY=your_nasa_api_key
```
Get your key at: https://api.nasa.gov/

### Notion Integration (Optional)
For reminder and task features:
```
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
```

### Performance Tuning
```
MAX_CONCURRENT_REQUESTS=10    # Concurrent API requests
REQUEST_TIMEOUT=30            # API timeout in seconds
CACHE_TTL=3600               # Cache time-to-live in seconds
```

---

## Deployment Features

### ✅ What's Included
- **24/7 Uptime** - Runs continuously on Railway
- **Auto-restart** - Automatic recovery from crashes
- **Environment Management** - Easy variable configuration
- **Logging** - Centralized logging in Railway dashboard
- **Health Monitoring** - Built-in health checks
- **OpenAI Integration** - Full AI chat, image, analysis features
- **Discord OAuth2** - Proper bot invitation system
- **Database** - Persistent SQLite database
- **Error Handling** - Comprehensive error recovery

### 🤖 Available Commands
Once deployed, your bot will have:

#### AI Commands
- `/chat` - Chat with AI assistant
- `/image` - Generate AI images
- `/analyze` - Analyze content with AI
- `/translate` - Translate text
- `/summarize` - Summarize long text
- `/personality` - Change AI personality

#### Space & Astronomy
- `/apod` - NASA Picture of the Day
- `/fact` - Random space facts
- `/meteor` - Meteor shower info
- `/iss` - ISS location tracking
- `/launch` - Rocket launch info
- `/planets` - Planet information

#### Server Management
- `/ping` - Bot latency
- `/uptime` - Bot uptime
- `/server` - Server statistics
- `/health` - System health check
- `/info` - Bot information

#### Admin Commands (Admins only)
- `/admin reload` - Reload bot components
- `/admin config` - Configure settings
- `/admin logs` - View bot logs
- `/admin extensions` - Manage extensions
- `/admin purge` - Bulk delete messages

---

## Troubleshooting

### Common Issues

#### ❌ "DISCORD_TOKEN not found"
- Ensure `DISCORD_TOKEN` is set in Railway environment variables
- Check the token is correct and hasn't been regenerated

#### ❌ "OpenAI API key not configured"
- Set `OPENAI_API_KEY` in Railway environment variables
- Verify your OpenAI account has API access and credits

#### ❌ Bot not responding to commands
- Wait 2-3 minutes after deployment for full startup
- Check Railway logs for errors
- Ensure bot has proper permissions in Discord server

#### ❌ Permission errors
- Bot needs "Send Messages", "Use Slash Commands" permissions
- For admin commands, bot needs appropriate server permissions

### Railway Dashboard
Monitor your bot via Railway dashboard:
- **Logs** - Real-time application logs
- **Metrics** - CPU, memory, network usage
- **Variables** - Environment variable management
- **Deployments** - Deployment history and rollbacks

### Bot Invitation
Use the `/invite` command to get the proper bot invitation link with all required permissions.

---

## Cost Optimization

### Railway Costs
- Railway provides $5/month free tier
- Typical bot usage: ~$3-8/month depending on activity

### OpenAI Costs  
- Chat: ~$0.01-0.06 per 1K tokens
- Image generation: ~$0.016-0.020 per image
- Typical monthly cost: $5-20 for active servers

### Cost Saving Tips
1. Set `OPENAI_MAX_TOKENS=1000` for lower costs
2. Use `gpt-3.5-turbo` instead of `gpt-4` for cheaper chat
3. Monitor usage in OpenAI dashboard
4. Set usage limits in OpenAI account settings

---

## Support

### Need Help?
- Check Railway deployment logs first
- Test commands in a development server
- Review environment variable configuration
- Ensure all required APIs are configured

### Updates
The bot auto-updates when you push to the main branch. Railway will:
1. Pull latest code
2. Rebuild container
3. Deploy with zero downtime

---

## Security Notes

### ⚠️ Important
- Never share your `DISCORD_TOKEN` or `OPENAI_API_KEY`
- Use Railway's environment variables, not hardcoded values
- Regularly rotate API keys
- Monitor usage for unauthorized access

### Production Ready
This deployment is production-ready with:
- Proper error handling
- Automatic restarts
- Health monitoring
- Secure environment variable handling
- Rate limiting and cooldowns

---

🎉 **Your Astra Bot is now ready for 24/7 operation on Railway!**
