# Gemini Image Generation System

## 🎨 Overview

The Gemini Image Generation System is a powerful, isolated AI image generation feature for Astra Bot, powered by Google's Gemini AI. This system provides high-quality image generation with comprehensive Discord integration, rate limiting, and robust error handling.

## ✨ Features

### 🤖 Core Features
- **Google Gemini AI Integration**: Uses `gemini-2.0-flash-preview-image-generation` model
- **Isolated Architecture**: Completely separate from main AI systems to prevent conflicts
- **Multiple Image Styles**: Realistic, Artistic, Cartoon, Anime, Photographic, Abstract, Vintage
- **Flexible Sizing**: Square HD, Portrait, Landscape, Wide formats
- **Advanced Rate Limiting**: Per-user, per-role limits with different tiers
- **Comprehensive Error Handling**: Graceful degradation and detailed error reporting
- **Statistics Tracking**: Generation counts, success rates, and performance metrics

### 🔧 Discord Integration
- **Slash Commands**: `/gemini-image`, `/gemini-status`, `/gemini-test`, `/gemini-help`
- **Rich Embeds**: Beautiful status displays and error messages
- **File Attachments**: Direct image delivery to Discord
- **Permission System**: Role-based access control and channel restrictions
- **Admin Tools**: System testing and diagnostics

## 📁 System Architecture

```
ai/
├── gemini_image_generator.py      # Core Gemini AI interface
├── gemini_discord_integration.py  # Discord-specific integration layer
└── ...

cogs/
├── gemini_image.py               # Discord bot cog with commands
└── ...
```

### Core Components

#### 1. **GeminiImageGenerator** (`ai/gemini_image_generator.py`)
- Main interface to Google Gemini AI
- Handles image generation requests
- Manages rate limiting and statistics
- Provides connection testing and health checks

#### 2. **GeminiImageDiscord** (`ai/gemini_discord_integration.py`)
- Discord-specific wrapper around core generator
- Handles Discord permissions and channel restrictions
- Creates Discord embeds and manages file attachments
- Provides Discord-formatted status information

#### 3. **GeminiImageCog** (`cogs/gemini_image.py`)
- Discord bot cog with slash commands
- User interface for image generation
- Admin tools and system diagnostics
- Help and status commands

## 🚀 Quick Start

### 1. Installation

Install the required dependency:
```bash
pip install google-genai>=0.8.0
```

### 2. Configuration

Set your Gemini API key as an environment variable:
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

### 3. Discord Setup

The system automatically loads with the bot. Commands will be available after restart:

- `/gemini-image` - Generate images
- `/gemini-status` - Check system status
- `/gemini-help` - View help information
- `/gemini-test` - Test connection (Admin only)

## 🎨 Usage Examples

### Basic Image Generation
```
/gemini-image prompt:A beautiful sunset over mountains
```

### Advanced Generation
```
/gemini-image prompt:A futuristic city at night style:artistic size:landscape
```

### Style Options
- **Realistic** - Photorealistic images
- **Artistic** - Creative and artistic style
- **Cartoon** - Fun cartoon-style images  
- **Anime** - Japanese animation style
- **Photographic** - Professional photography
- **Abstract** - Abstract and modern art
- **Vintage** - Retro and nostalgic style

### Size Options
- **Square HD** - 1024x1024 (default)
- **Portrait** - 768x1024
- **Landscape** - 1024x768
- **Wide** - 1024x576

## ⚙️ Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your-gemini-api-key-here

# Optional Discord Configuration
GEMINI_DEFAULT_CHANNEL_ID=123456789  # Default channel for regular users
GEMINI_ADMIN_ROLE_ID=987654321       # Admin role ID
GEMINI_MOD_ROLE_ID=567890123         # Moderator role ID
```

### Rate Limits

| User Type | Per Minute | Per Hour | Per Day |
|-----------|------------|----------|---------|
| Regular   | 10         | 50       | 100     |
| Moderator | 20         | 100      | 300     |
| Admin     | 50         | 200      | 500     |

### Permission System

- **Regular Users**: Can only use in designated channel
- **Moderators**: Can use in any channel with mod permissions
- **Administrators**: Full access to all features and channels

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_gemini_integration.py
```

### Test Coverage
1. **System Availability** - API key configuration and connection
2. **Discord Integration** - Embed generation and permissions
3. **Full Generation** - Complete image generation workflow

## 🛠️ Development

### Adding New Features

1. **Core Features**: Modify `ai/gemini_image_generator.py`
2. **Discord Features**: Modify `ai/gemini_discord_integration.py`
3. **Commands**: Modify `cogs/gemini_image.py`

### Error Handling

The system includes comprehensive error handling:
- Network timeouts and API errors
- Invalid prompts and content filtering
- Rate limit exceeded scenarios
- Permission denied cases
- Missing configuration issues

### Logging

All components use structured logging:
```python
import logging
logger = logging.getLogger("astra.gemini_image")
```

## 📊 Monitoring

### Status Information
- API connection status
- Current rate limit usage
- Generation success rates
- Average generation times
- Error frequencies

### Health Checks
- `/gemini-status` - User-friendly status
- `/gemini-test` - Admin diagnostic tool
- Automatic error recovery
- Connection pooling

## 🔒 Security

### Content Safety
- Built-in Gemini content filtering
- Prompt validation and sanitization
- User input length limits
- Rate limiting prevents abuse

### Privacy
- No image storage or caching
- Minimal logging of user data
- Secure API key handling
- Isolated from other bot systems

## 🤝 Contributing

When contributing to the Gemini system:

1. Maintain the isolated architecture
2. Follow existing error handling patterns
3. Update tests for new features
4. Document configuration changes
5. Respect rate limiting design

## 📝 API Reference

### Core Classes

#### `GeminiImageGenerator`
```python
async def generate_image(
    prompt: str,
    style: str = "realistic",
    size: str = "square_hd"
) -> ImageGenerationResult
```

#### `GeminiImageDiscord`
```python
async def handle_image_command(
    interaction: discord.Interaction,
    prompt: str,
    style: str,
    size: str
) -> None
```

### Data Classes

#### `ImageGenerationRequest`
- `prompt: str` - Image description
- `style: str` - Art style
- `size: str` - Image dimensions
- `user_id: int` - Discord user ID

#### `ImageGenerationResult`
- `success: bool` - Generation success
- `image_data: Optional[bytes]` - Generated image
- `generation_time: float` - Time taken
- `error: Optional[str]` - Error message

## 🆘 Troubleshooting

### Common Issues

#### "GEMINI_API_KEY not set"
- Set the environment variable with your API key
- Restart the bot after setting the variable

#### "Rate limit exceeded"
- Wait for the rate limit to reset
- Check current usage with `/gemini-status`

#### "Permission denied"
- Ensure you're in the correct channel
- Check if you have the required role

#### "Generation failed"
- Try a different prompt
- Check if the prompt violates content policies
- Verify API connectivity with `/gemini-test`

### Getting Help

1. Use `/gemini-help` for usage information
2. Use `/gemini-status` to check system health
3. Contact administrators for persistent issues
4. Check logs for detailed error information

## 📄 License

This system is part of Astra Bot and follows the same license terms.

---

🤖 **Powered by Google Gemini AI** - Use responsibly and enjoy creating amazing images!
