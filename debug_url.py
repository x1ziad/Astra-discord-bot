"""
Debug Bot Invitation URL
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.bot_invite import generate_bot_invite_url, get_full_permissions


def debug_url():
    print("🔍 Bot Invitation URL Debug")
    print("-" * 40)

    client_id = "123456789012345678"
    permissions = get_full_permissions()

    url = generate_bot_invite_url(client_id, permissions)
    print(f"Generated URL: {url}")
    print()

    # Check components
    print("URL Components:")
    if f"client_id={client_id}" in url:
        print("✅ Client ID found")
    else:
        print("❌ Client ID missing")

    if f"permissions={permissions}" in url:
        print("✅ Permissions found")
    else:
        print("❌ Permissions missing")

    if "scope=bot%20applications.commands" in url:
        print("✅ Correct scopes found (encoded)")
    elif "scope=bot applications.commands" in url:
        print("✅ Correct scopes found (unencoded)")
    else:
        print("❌ Correct scopes missing")
        print(f"URL contains: {url}")

    print("-" * 40)


if __name__ == "__main__":
    debug_url()
