# 🔐 Discord ID Verification & Update Guide

## ⚠️ **IMPORTANT NOTICE**

The Discord ID currently configured in your bot (`397847366090063872`) is **NOT your real Discord ID**. This is a placeholder that needs to be replaced with your actual Discord user ID.

## 🔍 **Step-by-Step: Find Your Real Discord ID**

### **Method 1: Developer Mode (Easiest)**

1. **Open Discord** (desktop app or web browser)
2. **Click the gear icon ⚙️** (User Settings) 
3. **Click "Advanced"** in the left sidebar
4. **Toggle ON "Developer Mode"**
5. **Close settings and right-click on your profile picture/username** anywhere
6. **Click "Copy User ID"**
7. **Your Discord ID is now copied!** (It will be 17-19 digits)

### **Method 2: Message Mention**

1. In any Discord text channel, type: `\@yourusername`
2. Send the message
3. You'll see something like: `<@123456789012345678>`
4. The number between `<@` and `>` is your Discord ID

### **Method 3: Profile URL**

1. Right-click your profile picture and select "Copy User ID" (if Developer Mode is on)
2. Or visit your profile and look at the URL: `https://discord.com/users/YOUR_ID_HERE`

## 🛠️ **How to Update Your Bot Configuration**

### **Option 1: Use the Update Script (Recommended)**

I've created a script to make this easy:

```bash
# Navigate to your bot directory
cd /Users/ziadmekawy/Developer/Discord-Stellaris/AstraBot

# Run the update script
./update_discord_id.sh
```

The script will:
- ✅ Backup your current config
- ✅ Validate your Discord ID format
- ✅ Update the configuration file
- ✅ Confirm the change

### **Option 2: Manual Edit**

Edit `config/config.json` and replace:
```json
"owner_id": "397847366090063872"
```

With your real Discord ID:
```json
"owner_id": "YOUR_REAL_DISCORD_ID_HERE"
```

### **Option 3: Use Bot Command (After Deployment)**

Once your bot is running, use:
```
/admin config set key:owner_id value:YOUR_REAL_DISCORD_ID
```

## ✅ **Verification Steps**

After updating your Discord ID:

1. **Deploy your bot** with the new configuration
2. **Test the owner verification** by trying:
   ```
   /admin shutdown confirm:CONFIRM
   ```
3. **The command should work** if your ID is correct
4. **The command should be denied** for other users

## 🚨 **Security Notes**

- **Keep your Discord ID private** - it's sensitive information
- **Only you should have access** to owner-only commands
- **Test the security** by having a friend try the shutdown command
- **They should get an "ACCESS DENIED" message**

## 📋 **Example Discord IDs**

Valid Discord IDs look like:
- `123456789012345678` (18 digits)
- `987654321098765432` (18 digits)
- `456789123456789123` (18 digits)

Invalid formats:
- `user#1234` (username format)
- `@username` (mention format)
- `123456789` (too short)

## 🔄 **After Update**

Once you've updated your Discord ID:

1. **Commit and push** the changes:
   ```bash
   git add config/config.json
   git commit -m "Update owner Discord ID to real user ID"
   git push origin main
   ```

2. **Deploy your bot** to your hosting platform

3. **Test the owner commands** to ensure they work

## ❓ **Need Help?**

If you're having trouble finding your Discord ID:

1. **Ask a friend** to help you with Developer Mode
2. **Use Discord's desktop app** (easier than mobile)
3. **Check Discord's official documentation** for ID location
4. **Your ID should be 17-19 digits long**

---

**Remember**: The current ID `397847366090063872` is just a placeholder and won't give you owner access to your bot. Make sure to replace it with your actual Discord user ID!
