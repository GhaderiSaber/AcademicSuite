#!/usr/bin/env bash
# ==============================================================================
# Helper Python script to authenticate Saber's second Telegram account (+989142564775)
# ==============================================================================
python3 - << 'EOF'
import asyncio
import os
import sys
import getpass
import qrcode
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
storage_dir = os.path.join(SCRIPT_DIR, "../.agents/skills/digital-twin-academic-consultant/scripts/userbot_storage")
os.makedirs(storage_dir, exist_ok=True)
session_path = os.path.join(storage_dir, "saber_second_userbot")
qr_image_path = os.path.join(SCRIPT_DIR, "../telegram_login_qr.png")
proxy = ("socks5", "127.0.0.1", 3066)

api_id = 6
api_hash = "eb06d4abfb49dc3eeb1aeb98ae0f581e"

client = TelegramClient(session_path, api_id, api_hash, proxy=proxy)

async def main():
    print("[*] Connecting to Telegram...")
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"\n[+] Second account is ALREADY authenticated!")
        print(f"    Name: {me.first_name} {me.last_name or ''}")
        print(f"    Username: @{me.username}")
        print(f"    Phone: {me.phone}")
        print(f"    User ID: {me.id}")
        await client.disconnect()
        return

    print("[*] Initiating fast QR Code Login...")
    qr_login = await client.qr_login()

    # Save PNG QR image
    img = qrcode.make(qr_login.url)
    img.save(qr_image_path)
    print(f"\n[+] QR Code image saved to: {qr_image_path}")

    # Print ASCII QR
    qr = qrcode.QRCode()
    qr.add_data(qr_login.url)
    print("\n" + "=" * 60)
    print("📱 SCAN THIS QR CODE WITH YOUR SECOND TELEGRAM ACCOUNT:")
    print("   1. Open Telegram on your phone with +989142564775.")
    print("   2. Go to Settings -> Devices -> Link Desktop Device (اتصال دستگاه).")
    print("   3. Point your camera at the screen or open: telegram_login_qr.png")
    print("=" * 60 + "\n")
    qr.print_ascii(invert=True)

    print(f"\nDirect Telegram Deep Link: {qr_login.url}")
    print("\n[*] Waiting up to 120 seconds for you to scan the QR code...")

    try:
        user = await qr_login.wait(120)
        print(f"\n[+] Successfully authenticated!")
        print(f"    Name: {user.first_name} {user.last_name or ''}")
        print(f"    Username: @{user.username}")
        print(f"    Phone: {user.phone}")
        print(f"    User ID: {user.id}")
    except SessionPasswordNeededError:
        print("\n[!] Two-step verification (2FA) cloud password is required for this account.")
        pw = getpass.getpass("Enter your Telegram 2FA cloud password: ")
        user = await client.sign_in(password=pw)
        print(f"\n[+] Successfully authenticated with 2FA!")
        print(f"    Name: {user.first_name} {user.last_name or ''}")
        print(f"    Username: @{user.username}")
        print(f"    Phone: {user.phone}")
        print(f"    User ID: {user.id}")
    except Exception as e:
        print(f"\n[-] Login timed out or error: {e}")
        sys.exit(1)

    await client.disconnect()

asyncio.run(main())
EOF
