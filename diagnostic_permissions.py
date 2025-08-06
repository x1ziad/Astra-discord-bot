#!/usr/bin/env python3
"""
Discord Bot Permission Diagnostic Utility
Helps diagnose and fix Discord permission issues for Astra Bot.
"""

import discord
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PermissionDiagnostic:
    def __init__(self, token):
        self.token = token
        self.client = discord.Client(intents=discord.Intents.all())
        self.required_permissions = [
            "send_messages",
            "embed_links",
            "attach_files",
            "read_message_history",
            "add_reactions",
            "use_external_emojis",
            "manage_messages",
        ]

    async def run_diagnostic(self):
        """Run comprehensive permission diagnostic"""
        await self.client.login(self.token)

        print("🛡️  Discord Bot Permission Diagnostic")
        print("=" * 50)
        print(f"Bot: {self.client.user.name}#{self.client.user.discriminator}")
        print(f"ID: {self.client.user.id}")
        print(f"Guilds: {len(self.client.guilds)}")
        print("=" * 50)

        for guild in self.client.guilds:
            await self.check_guild_permissions(guild)

        await self.client.close()

    async def check_guild_permissions(self, guild):
        """Check permissions for a specific guild"""
        print(f"\n🏰 Server: {guild.name} (ID: {guild.id})")
        print(f"👥 Members: {guild.member_count}")

        # Get bot member
        bot_member = guild.get_member(self.client.user.id)
        if not bot_member:
            print("❌ Bot is not a member of this server!")
            return

        # Check server-wide permissions
        server_perms = bot_member.guild_permissions
        print(f"\n📋 Server-Wide Permissions:")

        all_server_good = True
        for perm in self.required_permissions:
            has_perm = getattr(server_perms, perm, False)
            status = "✅" if has_perm else "❌"
            print(f"  {status} {perm}")
            if not has_perm:
                all_server_good = False

        if all_server_good:
            print("  🎉 All server permissions OK!")
        else:
            print("  ⚠️  Some server permissions missing!")

        # Check text channels
        text_channels = [
            c for c in guild.channels if isinstance(c, discord.TextChannel)
        ]
        problem_channels = []

        print(f"\n📝 Checking {len(text_channels)} text channels...")

        for channel in text_channels[:5]:  # Limit to first 5 channels
            channel_perms = bot_member.permissions_in(channel)
            channel_issues = []

            for perm in self.required_permissions:
                if not getattr(channel_perms, perm, False):
                    channel_issues.append(perm)

            if channel_issues:
                problem_channels.append((channel.name, channel_issues))

        if problem_channels:
            print(f"  ⚠️  Found permission issues in {len(problem_channels)} channels:")
            for channel_name, issues in problem_channels[:3]:  # Show first 3
                print(f"    #{channel_name}: {', '.join(issues)}")
        else:
            print("  ✅ All checked channels have proper permissions!")

        # Image generation specific check
        print(f"\n🎨 Image Generation Requirements:")
        img_perms = ["send_messages", "embed_links", "attach_files"]
        img_ready = all(getattr(server_perms, perm, False) for perm in img_perms)
        print(
            f"  {'✅' if img_ready else '❌'} Image generation permissions: {'Ready' if img_ready else 'Missing permissions'}"
        )

    def generate_invite_link(self, client_id=None):
        """Generate bot invite link with proper permissions"""
        if not client_id:
            client_id = input("Enter your bot's Client ID: ").strip()

        # Permission integer for all required permissions
        permissions = 2147746816  # Calculated permission integer

        invite_url = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions={permissions}&scope=bot%20applications.commands"

        print(f"\n🔗 Bot Invite Link (with proper permissions):")
        print(f"{invite_url}")
        print(f"\n📋 This link includes all required permissions:")
        for perm in self.required_permissions:
            print(f"  ✅ {perm}")

        return invite_url


async def main():
    """Main diagnostic function"""
    print("🤖 Astra Bot Permission Diagnostic Tool")
    print("=" * 40)

    # Get bot token
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        token = input("Enter your Discord bot token: ").strip()

    if not token:
        print("❌ No token provided. Exiting.")
        return

    try:
        diagnostic = PermissionDiagnostic(token)

        print("\nChoose an option:")
        print("1. Run full permission diagnostic")
        print("2. Generate invite link with proper permissions")
        print("3. Both")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice in ["1", "3"]:
            print("\n🔍 Running permission diagnostic...")
            await diagnostic.run_diagnostic()

        if choice in ["2", "3"]:
            print("\n🔗 Generating invite link...")
            diagnostic.generate_invite_link()

    except discord.errors.LoginFailure:
        print("❌ Invalid bot token! Please check your token.")
    except Exception as e:
        print(f"❌ Error during diagnostic: {e}")


def quick_permissions_check():
    """Quick permission reference without bot connection"""
    print("📋 Quick Permission Reference for Astra Bot")
    print("=" * 50)

    permissions = [
        ("send_messages", "Send Messages", "Essential - Bot communication"),
        ("embed_links", "Embed Links", "Essential - Rich AI responses"),
        ("attach_files", "Attach Files", "Essential - Image generation"),
        (
            "read_message_history",
            "Read Message History",
            "Recommended - Better context",
        ),
        ("add_reactions", "Add Reactions", "Recommended - Interactive responses"),
        ("use_external_emojis", "Use External Emojis", "Optional - Enhanced reactions"),
        ("manage_messages", "Manage Messages", "Optional - Message cleanup"),
    ]

    print("\n🛡️  Required Permissions:")
    for perm_code, perm_name, description in permissions:
        importance = (
            "🔴"
            if "Essential" in description
            else "🟡" if "Recommended" in description else "🟢"
        )
        print(f"{importance} {perm_name}")
        print(f"   Code: {perm_code}")
        print(f"   Use: {description}")
        print()

    print("🔗 Permission Integer for Invite Link: 2147746816")
    print("📝 This covers all essential and recommended permissions.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_permissions_check()
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n👋 Diagnostic cancelled by user.")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
