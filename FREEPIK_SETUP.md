# Freepik AI Image Generation Setup 🎨

## Overview
Successfully implemented Freepik AI image generation with channel restrictions and user permission system for the Astra Discord Bot.

## Railway Environment Variable

### Variable Name: `FREEPIK_API_KEY`
- **Description**: API key for Freepik AI image generation service
- **Required**: Yes (for image generation functionality)
- **Where to set**: Railway Dashboard → Your Project → Variables tab
- **Value**: Your Freepik API key from Freepik AI service

## Features Implemented

### 🔐 Permission System
- **Regular Users**: Can only use `/image` command in channel ID `1402666535696470169`
- **Moderators**: Can use `/image` command in any channel (users with `manage_messages` or `manage_guild` permissions)
- **Administrators**: Can use `/image` command in any channel (users with `administrator` permission)

### ⏱️ Rate Limiting
- **Regular Users**: 5 images per hour
- **Moderators**: 20 images per hour  
- **Administrators**: 50 images per hour
- Rate limits reset every hour automatically

### 🎯 AI Provider Priority
1. **Freepik AI** (Primary) - Uses your `FREEPIK_API_KEY`
2. **OpenAI DALL-E** (Fallback) - If Freepik fails and OpenAI is available

### 📊 Database Logging
- All image generation attempts are logged to database
- Tracks user ID, channel ID, prompt, provider, success/failure
- Enables usage analytics and moderation

## Command Usage

### `/image <prompt>`
- **Description**: Generate an image using AI
- **Parameter**: `prompt` - Description of the image to generate
- **Examples**:
  - `/image a futuristic space station orbiting a red planet`
  - `/image a cyberpunk cat with neon eyes in a dark alley`
  - `/image a medieval castle on a floating island`

### Permission Messages
- **Regular users in wrong channel**: Shows redirect message to correct channel
- **Rate limit exceeded**: Shows when limit resets with Discord timestamp
- **Success**: Displays generated image with provider info and user access level

## Technical Implementation

### Core Components
1. **`FreepikImageGenerator`** - Handles Freepik API communication
2. **Permission checking** - Channel and role-based access control
3. **Rate limiting** - Redis/memory-based usage tracking
4. **Database logging** - SQLite storage for analytics
5. **Enhanced Discord command** - User-friendly interface with rich embeds

### Database Schema
```sql
CREATE TABLE image_generations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    provider TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Configuration
```python
image_config = {
    "default_channel_id": 1402666535696470169,
    "mod_anywhere": True,
    "admin_anywhere": True,
    "rate_limit": {
        "regular_users": 5,
        "mods": 20,
        "admins": 50,
    }
}
```

## Testing Results ✅

### Permission System Tests
- ✅ Regular users blocked in wrong channels
- ✅ Regular users allowed in designated channel (1402666535696470169)
- ✅ Mods can use anywhere
- ✅ Admins can use anywhere

### Rate Limiting Tests  
- ✅ Different limits for different user roles
- ✅ Proper tracking and reset functionality
- ✅ User-friendly error messages

### Integration Tests
- ✅ FreepikImageGenerator class working
- ✅ ConsolidatedAIEngine integration complete
- ✅ Discord command enhanced with rich embeds
- ✅ Error handling and fallback systems

## Setup Instructions

### 1. Get Freepik API Key
- Sign up at Freepik AI service
- Obtain your API key from the dashboard

### 2. Set Railway Environment Variable
- Go to Railway Dashboard
- Navigate to your Astra Bot project
- Go to Variables tab
- Add new variable:
  - **Name**: `FREEPIK_API_KEY`
  - **Value**: Your actual API key

### 3. Deploy Changes
- The bot will automatically detect the API key on restart
- Image generation will be available immediately

### 4. Test the Feature
- Use `/image test prompt` in the designated channel as a regular user
- Try as a mod/admin in any channel to verify permissions
- Check rate limiting by generating multiple images

## Channel Configuration

### Default Channel ID: `1402666535696470169`
This is the designated channel where regular users can generate images. To change this:

1. Update the `default_channel_id` in the `image_config` dictionary
2. Or set via environment variable `IMAGE_DEFAULT_CHANNEL_ID`

## Usage Analytics

The system logs all image generation attempts including:
- User information and permissions
- Success/failure rates
- Popular prompts and usage patterns  
- Rate limit violations
- Channel usage statistics

## Security Features

### Content Safety
- Prompts are logged for moderation review
- Rate limiting prevents abuse
- Channel restrictions control access
- Role-based permissions ensure proper usage

### Error Handling
- Graceful fallback to OpenAI DALL-E if Freepik fails
- User-friendly error messages
- Comprehensive logging for debugging
- No API key exposure in error messages

## Maintenance

### Monitoring
- Check database logs for usage patterns
- Monitor rate limit violations
- Review generated image prompts for policy compliance
- Track API usage costs

### Updates
- API key rotation supported through Railway variables
- Channel restrictions easily adjustable
- Rate limits configurable per user role
- Provider priorities can be modified

---

**Ready for Production** ✅  
The Freepik AI image generation system is fully implemented and ready for deployment with your `FREEPIK_API_KEY` environment variable on Railway.
