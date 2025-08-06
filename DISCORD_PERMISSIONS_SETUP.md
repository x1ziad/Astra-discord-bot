# Discord Bot Permissions Setup Guide

## 🛡️ Essential Permissions for Astra Bot

This guide helps server administrators configure the necessary Discord permissions for Astra Bot to function properly, especially for AI features and image generation.

## 📋 Required Permissions

### Core Permissions (Essential)
- ✅ **Send Messages** - Basic bot communication
- ✅ **Embed Links** - Rich message formatting for AI responses
- ✅ **Attach Files** - Image generation and file uploads
- ✅ **Read Message History** - Better conversation context
- ✅ **Add Reactions** - Interactive command responses

### Enhanced Features (Recommended)
- ✅ **Use External Emojis** - Enhanced reaction system
- ✅ **Manage Messages** - Message cleanup when needed
- ✅ **Use Slash Commands** - Modern Discord command interface

## 🚀 Quick Setup Methods

### Method 1: Bot Invite Link (Easiest)
When inviting the bot, use this permissions integer: `2147746816`

**Invite Link Template:**
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=2147746816&scope=bot%20applications.commands
```

### Method 2: Server-Wide Role Setup

1. **Go to Server Settings**
   - Right-click your server name
   - Select "Server Settings"

2. **Navigate to Roles**
   - Click "Roles" in the left sidebar
   - Find your bot's role (usually named after the bot)

3. **Enable Required Permissions**
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Use External Emojis
   - ✅ Manage Messages
   - ✅ Use Slash Commands

4. **Save Changes**
   - Click "Save Changes" at the bottom

### Method 3: Channel-Specific Setup

For specific channels where you want enhanced control:

1. **Right-click the channel**
2. **Select "Edit Channel"**
3. **Go to "Permissions" tab**
4. **Add the bot role** (+ symbol)
5. **Set permissions** for that specific channel
6. **Save changes**

## 🔍 Permission Verification

### Using Bot Commands
```
/permissions
```
This command will check all required permissions in the current channel and provide troubleshooting guidance.

### Using Bot Test
```
/ai_test
```
This will test if the AI features are working properly with current permissions.

### Manual Verification Checklist
- [ ] Bot can send messages in target channels
- [ ] Bot can create rich embeds (colorful message boxes)
- [ ] Bot can attach/upload files (test with `/imagine` command)
- [ ] Bot can add reactions to messages
- [ ] Bot can read previous messages for context

## 🎨 Image Generation Requirements

For the `/imagine` command to work properly:

### Essential Permissions
- ✅ **Attach Files** - Upload generated images
- ✅ **Embed Links** - Display image information
- ✅ **Send Messages** - Respond to commands

### API Requirements
- Valid Freepik API key configured
- Sufficient API credits/usage limits

## 🛠️ Troubleshooting Common Issues

### "Bot doesn't respond to commands"
**Solution:** Check if bot has "Send Messages" permission
```
/permissions
```

### "Images aren't generating"
**Possible Causes:**
1. Missing "Attach Files" permission
2. Freepik API not configured
3. API rate limits exceeded

**Solutions:**
1. Enable "Attach Files" permission
2. Check environment variables (`FREEPIK_API_KEY`)
3. Wait for rate limit reset or upgrade API plan

### "Bot messages look plain/broken"
**Solution:** Enable "Embed Links" permission for rich formatting

### "Bot can't react to messages"
**Solution:** Enable "Add Reactions" and "Use External Emojis" permissions

## 🏗️ Administrator Commands

### Permission Diagnostic
```
/permissions
```
Comprehensive permission check with troubleshooting guidance.

### AI System Test
```
/ai_test
```
Test AI response generation capabilities.

### Enhanced Features Test
```
/test_enhanced_features
```
Full system diagnostic (Admin only).

## 🔐 Security Best Practices

### Principle of Least Privilege
- Only enable permissions the bot actually needs
- Use channel-specific permissions for sensitive channels
- Regularly audit bot permissions

### Recommended Role Setup
1. Create a dedicated role for the bot
2. Position it appropriately in role hierarchy
3. Don't give unnecessary admin permissions
4. Monitor bot activity logs

## 🚨 Emergency Troubleshooting

### Bot Completely Unresponsive
1. Check if bot is online (green status)
2. Verify "Send Messages" permission
3. Test in different channels
4. Restart bot if you have access

### Image Generation Failing
1. Run `/permissions` command
2. Check "Attach Files" permission
3. Verify Freepik API status
4. Test with simple prompt first

### Permissions Keep Resetting
1. Check Discord's audit log
2. Verify role hierarchy
3. Ensure bot role isn't being overridden
4. Contact server owner if needed

## 📞 Support Information

### Quick Help Commands
- `/help` - General bot help
- `/permissions` - Permission diagnostic
- `/ai_test` - Feature testing

### Error Messages to Look For
- "Missing Access" - Permission issue
- "Cannot send messages" - Send Messages disabled
- "Cannot attach files" - Attach Files disabled
- "Embed links disabled" - Embed Links disabled

## 🎯 Optimal Configuration

### For Full AI Features
```
Permissions Integer: 2147746816
Includes: Send Messages, Embed Links, Attach Files, 
         Read Message History, Add Reactions, 
         Use External Emojis, Manage Messages
```

### For Basic AI Only
```
Permissions Integer: 18432
Includes: Send Messages, Embed Links, Read Message History
```

### For Image Generation Focus
```
Permissions Integer: 32768 + 16384 + 2048 = 51200
Includes: Send Messages, Embed Links, Attach Files
```

---

**Note:** After changing permissions, it may take a few moments for Discord to update. Test the bot functionality after making changes to ensure everything works properly.

**Pro Tip:** Use the `/permissions` command regularly to monitor permission status, especially after server updates or role changes.
