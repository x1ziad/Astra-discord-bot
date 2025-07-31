# 🚀 Astra Discord Bot

A sophisticated Stellaris-themed astronomy bot with slash commands, AI chat capabilities, Notion integration, gamified quizzes, and server tools.

## 🌟 Features
- **🤖 AI Commands** – Chat with Astra using OpenAI GPT models (`/ai`, `/testapi`, `/setpersonality`)
- **🎮 Interactive Quiz** – Space/Stellaris quiz with gamification (`/quiz`)
- **🌌 Space Commands** – NASA Astronomy Picture of the Day (`/apod`)
- **🏛️ Stellaris Integration** – Role picker for Stellaris empires (`/empire`)
- **📝 Task Management** – Notion task syncing (`/reminders`, `/todo`)
- **📊 Server Tools** – Bot & server insights (`/stats`, `/uptime`)
- **🛠️ Admin Tools** – Role-based help embeds and server management

## 🚧 Setup

### 🐳 Docker Setup (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/x1ziad/Astra-discord-bot.git
cd Astra-discord-bot
```

2. **Set up environment variables**
```bash
cp .env.example .env
```

3. **Configure your API keys in `.env`**
```env
# Required
DISCORD_TOKEN=your-discord-bot-token-here
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional
NASA_API_KEY=your-nasa-api-key-or-DEMO_KEY
NOTION_TOKEN=your-notion-token
NOTION_DATABASE_ID=your-notion-database-id
```

4. **Run with Docker Compose**
```bash
# Production
docker-compose up -d

# Development (with live code reloading)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### 🔧 Manual Setup

1. **Clone and install**
```bash
git clone https://github.com/x1ziad/Astra-discord-bot.git
### 🔧 Manual Setup

1. **Clone and install**
```bash
git clone https://github.com/x1ziad/Astra-discord-bot.git
cd Astra-discord-bot
pip install -r requirements.txt
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run the bot**
```bash
python bot.1.0.py
```

## 🔑 API Keys Setup

### Discord Bot Token (Required)
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token and add to your `.env` file

### OpenAI API Key (Required for AI features)
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Add to your `.env` as `OPENAI_API_KEY=sk-your-key-here`

### NASA API Key (Optional)
1. Visit [NASA API](https://api.nasa.gov/)
2. Generate an API key (free)
3. Add to your `.env` or use `DEMO_KEY` (limited usage)

### Notion Integration (Optional)
1. Go to [Notion Developers](https://developers.notion.com/)
2. Create an integration and get the token
3. Share a database with the integration and get the database ID

## 🐳 Docker Commands

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down

# Rebuild after changes
docker-compose up --build -d

# Development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 🤖 AI Commands

The bot includes 16 AI commands powered by OpenAI:

- `/ai <question>` - Ask Astra anything
- `/testapi` - Test OpenAI API connection
- `/setpersonality <personality>` - Change AI personality
- `/personalities` - List available personalities
- `/aiconfig` - Configure AI settings
- `/clearhistory` - Clear conversation history

## 🔧 Troubleshooting

### "OpenAI API key is not configured"
- Ensure `OPENAI_API_KEY` is set in your `.env` file
- Check that the key starts with `sk-`
- Verify the key is valid at [OpenAI Platform](https://platform.openai.com/)

### Docker Issues
- Make sure Docker and Docker Compose are installed
- Check that no other services are using the same ports
- Verify your `.env` file exists and has the correct values

### Bot Not Responding
- Check bot permissions in your Discord server
- Ensure the bot token is correct and the bot is online
- Check logs with `docker-compose logs -f`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
