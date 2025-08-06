# Railway Environment Variables Setup for Astra Bot

## 🚨 CRITICAL: Fix for Image Generation API Issue

The issue you're experiencing is that the **FREEPIK_API_KEY** environment variable is not set in your Railway deployment. This causes the 401 Unauthorized error.

## Required Environment Variables

### 1. Discord Bot Token
```bash
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
```

### 2. AI Conversation API (Choose ONE)
```bash
# Option A: OpenRouter (Recommended)
OPENROUTER_API_KEY=sk-or-v1-YOUR_OPENROUTER_KEY_HERE
AI_API_KEY=sk-or-v1-YOUR_OPENROUTER_KEY_HERE
AI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=openrouter/auto

# Option B: OpenAI Direct
OPENAI_API_KEY=sk-YOUR_OPENAI_KEY_HERE
AI_API_KEY=sk-YOUR_OPENAI_KEY_HERE
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-3.5-turbo
```

### 3. 🎨 IMAGE GENERATION API (This is what's missing!)
```bash
# Freepik API for image generation (REQUIRED for images)
FREEPIK_API_KEY=YOUR_FREEPIK_API_KEY_HERE
```

**Get your Freepik API key at: https://www.freepik.com/api**
**Verify your key at: https://www.freepik.com/developers/dashboard/api-key**

### 4. Optional APIs
```bash
# NASA API for space content
NASA_API_KEY=YOUR_NASA_API_KEY_HERE

# Any other optional APIs
```

## 🔧 How to Set Environment Variables in Railway

1. **Go to your Railway project dashboard**
2. **Click on your bot service**
3. **Go to the "Variables" tab**
4. **Add each environment variable:**
   - Variable Name: `FREEPIK_API_KEY`
   - Value: `your_actual_freepik_api_key_here`
5. **Click "Add"**
6. **Redeploy your service**

## 🧪 Test Your Configuration

Run this command in your Railway service to verify:

```python
import os
print("Environment Variables Status:")
print(f"DISCORD_TOKEN: {'✅' if os.getenv('DISCORD_TOKEN') else '❌'}")
print(f"AI_API_KEY: {'✅' if os.getenv('AI_API_KEY') else '❌'}")
print(f"FREEPIK_API_KEY: {'✅' if os.getenv('FREEPIK_API_KEY') else '❌'}")
```

## 🐞 Debug the Issue

The logs show:
```
Freepik API error 401: {"message":"Unauthorized: No API key provided..."}
```

This confirms that `FREEPIK_API_KEY` is missing from Railway environment variables.

## ✅ Solution Steps

1. **Get Freepik API Key:** https://www.freepik.com/api
2. **Add to Railway:** Variables tab → `FREEPIK_API_KEY` = `your_key`
3. **Redeploy:** Railway will restart with new environment variables
4. **Test:** Use `astra generate a blue star` in Discord

## 📝 API Separation Explanation

- **AI Conversations:** Uses OpenRouter/OpenAI API (working fine)
- **Image Generation:** Uses separate Freepik API (this was missing)
- **These are completely different services requiring separate API keys**

## 🚀 Expected Result After Fix

Once you add the FREEPIK_API_KEY:
- Image generation commands will work: `astra generate <prompt>`
- No more 401 Unauthorized errors
- Detailed logging will show successful API calls
- Users will get beautiful AI-generated images

## 🔍 Verify the Fix

After setting the environment variable, check logs for:
```
✅ Freepik Image Client initialized with API key
🎨 Starting Freepik image generation for user...
✅ Image generated successfully
```

Instead of:
```
❌ Freepik API error 401: Unauthorized
```
