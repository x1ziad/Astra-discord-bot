# 🔑 Bot Owner Setup Guide

## Critical Configuration: Owner ID

To use owner-only commands and avoid "ACCESS DENIED" errors, you **MUST** set your Discord user ID as the bot owner.

### Quick Fix

Add this line to your `.env` file:

```bash
OWNER_ID=1115739214148026469
```

### How to Find Your Discord User ID

1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click on your username in any chat
3. Select "Copy User ID"
4. Paste the ID into your `.env` file

### Important Files Updated

- ✅ `.env` - Added OWNER_ID variable
- ✅ `.env.template` - Updated template with OWNER_ID placeholder
- ✅ `config/config.json` - Added owner_id field to bot configuration

### Owner-Only Commands

These commands require owner permissions:
- `/nexus ai_tokens` - AI token usage monitoring
- `/nexus test_reporting` - Test Discord data reporting
- `/admin shutdown` - Bot shutdown/restart
- `/admin sync` - Sync slash commands

### Verification

After adding OWNER_ID to your `.env` file, restart the bot and try an owner-only command. You should no longer see "ACCESS DENIED" errors.

### Security Note

The `.env` file is in `.gitignore` for security reasons. Never commit real API keys or user IDs to version control.