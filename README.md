# Astra Discord Bot

A sophisticated AI-powered Discord bot with advanced image generation capabilities and comprehensive server management features.

## 🚀 Quick Start

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-7289da?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/pdxPDhjS)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/x1ziad/Astra-discord-bot)

**[🎮 Join Our Discord Server](https://discord.gg/pdxPDhjS)** to get support, see the bot in action, and connect with the community!

## Features

### 🤖 AI Integration
- **Advanced AI Chat**: Powered by multiple AI providers through OpenRouter
- **Image Generation**: MagicHour.ai integration for high-quality image creation
- **Smart Responses**: Context-aware conversations with personality customization
- **User Profiling**: Intelligent user interaction tracking and preferences

### 🎯 Core Commands
- **Nexus System**: Central AI control and monitoring
- **Admin Tools**: Comprehensive server management and moderation
- **Analytics**: Performance tracking and usage statistics
- **Help System**: Interactive command guidance and documentation

### 🛠️ Technical Features
- **Modular Architecture**: Clean cog-based command organization
- **Database Integration**: SQLite for persistent data storage
- **Error Handling**: Comprehensive logging and error recovery
- **Performance Optimization**: Efficient resource management and caching

## Installation

1. Clone the repository:
```bash
git clone https://github.com/x1ziad/Astra-discord-bot.git
cd AstraBot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Run the bot:
```bash
python bot.1.0.py
```

## Configuration

### Required Environment Variables
- `DISCORD_TOKEN`: Your Discord bot token
- `OPENROUTER_API_KEY`: OpenRouter API key for AI features
- `MAGICHOUR_API_KEY`: MagicHour.ai API key for image generation

### Optional Configuration
- `GEMINI_API_KEY`: Google Gemini API key for additional AI features
- Database configurations in `config/config.json`

## Commands

### AI Commands
- `/chat` - Interact with the AI assistant
- `/image` - Generate images using AI
- `/personality` - Customize AI personality settings

### Admin Commands
- `/nexus` - Access the AI control center
- `/admin` - Server administration tools
- `/analytics` - View bot performance statistics

### Utility Commands
- `/help` - Get command information and usage
- `/status` - Check bot and service status

## Deployment

### Railway (Recommended)
The bot is configured for easy deployment on Railway with the included `railway.toml` configuration.

### Docker
```bash
docker build -t astra-bot .
docker run -d --env-file .env astra-bot
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please join our [Discord server](https://discord.gg/pdxPDhjS) or create an issue on GitHub.

### 🔗 Quick Links
- **Discord Server**: [Join our community](https://discord.gg/pdxPDhjS)
- **GitHub Issues**: [Report bugs or request features](https://github.com/x1ziad/Astra-discord-bot/issues)
