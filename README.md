# 🚀 Astra Discord Bot

A sophisticated Stellaris-themed astronomy bot with slash commands, AI chat capabilities, Notion integration, gamified quizzes, and server tools.

## 🌟 Features
- 🤖 **AI Commands** (16 total) - Chat with AI using OpenAI
  - `/ai` – Ask Astra's AI something directly
  - `/testapi` – Test your OpenAI API connection
  - `/setpersonality` – Change Astra's personality
  - `/personalities` – List available personality profiles
  - `/aiconfig` – Configure AI behavior
  - `/clearhistory` – Clear conversation history
- `/quiz` – Interactive space/Stellaris quiz
- `/apod` – NASA Astronomy Picture of the Day
- `/empire` – Role picker for Stellaris empires
- `/reminders`, `/todo` – Notion task syncing
- `/stats`, `/uptime` – Bot & server insights
- Role-based help embeds and admin tools

## 🚧 Setup

### Prerequisites
- [Discord Bot Token](https://discord.com/developers/applications)
- [OpenAI API Key](https://platform.openai.com/api-keys) (for AI commands)
- Docker and Docker Compose (recommended) OR Python 3.10+

### Option 1: Docker Setup (Recommended)

#### 1. Clone the repository
#### 2. Get your API keys

**Discord Bot Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select existing one
3. Go to "Bot" section
4. Copy the bot token

**OpenAI API Key:**
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### 3. Configure environment variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your actual keys
nano .env  # or use your preferred editor
```

#### 4. Run with Docker Compose
```bash
docker-compose up -d
```

#### Alternative: Run with Docker directly
```bash
# Build the image
docker build -t astra-bot .

# Run the container
docker run -d \
  --name astra-discord-bot \
  -e DISCORD_BOT_TOKEN=your_discord_bot_token_here \
  -e OPENAI_API_KEY=sk-your_openai_api_key_here \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  astra-bot
```

### Option 2: Local Python Setup

#### 1. Install dependencies
```bash
git clone https://github.com/x1ziad/Astra-discord-bot.git
cd Astra-discord-bot
pip install -r requirements.txt
```

#### 2. Set environment variables
```bash
# Linux/macOS
export DISCORD_BOT_TOKEN="your_discord_bot_token_here"
export OPENAI_API_KEY="sk-your_openai_api_key_here"

# Windows
set DISCORD_BOT_TOKEN=your_discord_bot_token_here
set OPENAI_API_KEY=sk-your_openai_api_key_here
```

#### 3. Run the bot
```bash
python bot.1.0.py
```

## 🔧 Configuration

### AI Personality Profiles
The bot supports custom AI personalities. Place `.json` files in the `personality_profiles/` directory:

```json
{
  "system_prompt": "You are Astra, a helpful space exploration assistant.",
  "description": "Helpful space assistant",
  "temperature": 0.7,
  "max_tokens": 500,
  "openai_model": "gpt-4o-mini"
}
```

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_BOT_TOKEN` | ✅ | Your Discord bot token |
| `OPENAI_API_KEY` | ✅ | Your OpenAI API key (for AI commands) |
| `NASA_API_KEY` | ❌ | NASA API key (defaults to DEMO_KEY) |
| `NOTION_TOKEN` | ❌ | Notion integration token |
| `NOTION_DATABASE_ID` | ❌ | Notion database ID |

## 🧪 Testing AI Commands

After setup, test the AI functionality:

1. Use `/testapi` command to verify OpenAI connection
2. Try `/ai question="Hello, how are you?"` 
3. Use `/personalities` to see available AI personalities
4. Configure AI with `/aiconfig`

## 🔍 Troubleshooting

### Common Issues

**"OpenAI API key is not configured"**
- Ensure `OPENAI_API_KEY` environment variable is set
- Verify the API key starts with `sk-`
- Check your OpenAI account has available credits

**Bot doesn't respond to commands**
- Verify `DISCORD_BOT_TOKEN` is correct
- Ensure bot has proper permissions in your server
- Check bot is online and slash commands are synchronized

**Docker container exits immediately**
- Check logs: `docker logs astra-discord-bot`
- Verify environment variables are properly set
- Ensure all required keys are provided

### Logs and Debugging
```bash
# View container logs
docker logs astra-discord-bot

# View live logs
docker logs -f astra-discord-bot

# Check container status
docker ps
```

## 📁 Project Structure
```
Astra-discord-bot/
├── bot.1.0.py              # Main bot file
├── ai_chat.py               # AI chat handler
├── cogs/                    # Bot command modules
│   ├── ai_commands.py       # AI-related commands
│   └── ...
├── personality_profiles/    # AI personality configurations
├── data/                    # Persistent data storage
├── logs/                    # Application logs
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── .env.example            # Environment variables template
```

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
Made with ❤️ by x1ziadbash
git clone https://github.com/x1ziad/Astra-discord-bot.git
cd Astra-discord-bot
