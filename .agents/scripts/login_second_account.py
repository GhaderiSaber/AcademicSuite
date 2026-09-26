#!/usr/bin/env python3
"""
login_second_account.py — Authenticate Saber's Second Telegram Account via QR Code
-----------------------------------------------------------------------------------
Telegram requires QR login to bypass reCAPTCHA.
This script:
1. Connects to Telegram via the active SOCKS5 proxy.
2. Generates a QR login code and displays it as ASCII art + saves /tmp/telegram_qr.png.
3. Waits for you to scan via:
   Telegram -> Settings -> Devices -> Link Desktop Device (اتصال دستگاه).
4. Saves 'saber_second_userbot.session'.
5. Updates 'telethon_config.json' with second_account.
6. Restarts 'telethon-userbot.service' to listen to both accounts 24/7!
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Correctly resolve workspace root from .agents/scripts
if os.path.basename(SCRIPT_DIR) == "scripts" and os.path.basename(os.path.dirname(SCRIPT_DIR)) == ".agents":
    ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
else:
    ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "bin", "python")

# Auto re-exec with virtualenv python if invoked via system python
if os.path.isfile(VENV_PYTHON) and os.path.realpath(sys.executable) != os.path.realpath(VENV_PYTHON):
    os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)

# Fallback: Dynamic discovery of local virtualenv site-packages
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

SKILL_DIR = os.path.join(ROOT_DIR, ".agents/skills/digital-twin-academic-consultant/scripts")
CONFIG_PATH = os.path.join(SKILL_DIR, "telethon_config.json")
SESSION_PATH = os.path.join(SKILL_DIR, "saber_second_userbot")

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import qrcode

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--password", "-p", default=None, help="2FA cloud password if enabled")
    args = parser.parse_args()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    proxy = (cfg["proxy"]["proxy_type"], cfg["proxy"]["addr"], cfg["proxy"]["port"])
    client = TelegramClient(SESSION_PATH, cfg["api_id"], cfg["api_hash"], proxy=proxy)

    await client.connect()
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"[✓] Already authorized as: {me.first_name} (@{me.username}) ID: {me.id}")
        await client.disconnect()
        return

    print("=" * 65)
    print("📱 TELEGRAM QR CODE LOGIN (Bypasses SMS & reCAPTCHA)")
    print("   1. Open Telegram on your phone (Account: +989142564775).")
    print("   2. Go to: Settings -> Devices -> Link Desktop Device")
    print("             (تنظیمات -> دستگاه‌ها -> اتصال دستگاه)")
    print("   3. Scan the QR code below or open the generated image:")
    print("=" * 65 + "\n")

    img_path = str(Path.home() / "Desktop" / "telegram_qr.png")
    qr_login = await client.qr_login()

    user = None
    for attempt in range(1, 7):
        # Save image for easy viewing
        qr_img = qrcode.make(qr_login.url)
        qr_img.save(img_path)
        print(f"\n[+] QR Code image updated on Desktop: {img_path}")
        print(f"[+] Raw Login URL: {qr_login.url}\n")

        # Print ASCII QR
        qr = qrcode.QRCode()
        qr.add_data(qr_login.url)
        qr.print_ascii(invert=True)

        print(f"\n[*] Waiting for QR scan from Telegram mobile app (Attempt {attempt}/6, ~60s)...")
        try:
            user = await qr_login.wait(timeout=60)
            break
        except SessionPasswordNeededError:
            print("\n[*] Two-step verification (2FA) cloud password is required.")
            if args.password:
                user = await client.sign_in(password=args.password)
            else:
                import getpass
                pw = getpass.getpass("Enter 2FA password: ")
                user = await client.sign_in(password=pw)
            break
        except asyncio.TimeoutError:
            if attempt < 6:
                print(f"\n[*] QR code expired. Refreshing QR code automatically (Attempt {attempt+1}/6)...")
                await qr_login.recreate()
            else:
                print("\n[-] QR code expired after 6 attempts. Please run the script again.")
                await client.disconnect()
                sys.exit(1)

    print("\n" + "=" * 65)
    print(f"[✓] SUCCESS! Authenticated as: {user.first_name} {user.last_name or ''} (@{user.username}) [ID: {user.id}]")
    print(f"[✓] Session saved: {SESSION_PATH}.session")
    
    # Update telethon_config.json
    cfg["second_account"] = {
        "phone_number": "+989142564775",
        "session_name": "saber_second_userbot",
        "admin_id": user.id
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"[✓] Updated {CONFIG_PATH} with second_account (ID: {user.id})")

    # Clean up desktop image
    if os.path.exists(img_path):
        try:
            os.remove(img_path)
        except Exception:
            pass

    await client.disconnect()

    # Restart background daemon
    print("[*] Restarting telethon-userbot.service...")
    manage_sh = os.path.join(SKILL_DIR, "manage_service.sh")
    os.system(f"bash '{manage_sh}' restart")
    print("[✓] Dual-account 24/7 background listener is now ACTIVE!")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(main())
