#!/usr/bin/env bash
# ==============================================================================
# manage_service.sh — Telethon Userbot Background Service Manager (macOS launchd)
# ==============================================================================
# This script manages Saber Ghaderi's Digital Twin Telethon Userbot as a native
# background daemon using macOS launchd (LaunchAgent).
#
# Features:
#   - Starts automatically on system boot / user login
#   - Runs silently in the background 24/7
#   - Auto-restarts on network disconnection or crash (KeepAlive)
#   - Real-time unbuffered logging to userbot_storage/telethon.log
#   - Zero manual runs needed when switching clients
# ==============================================================================

set -e

PLIST_LABEL="com.saber.telethon-userbot"
# Resolve real directory even if called via symlink
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
    DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/userbot_storage"
PLIST_FILE="${HOME}/Library/LaunchAgents/${PLIST_LABEL}.plist"
PYTHON_BIN="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
USERBOT_SCRIPT="${SCRIPT_DIR}/telethon_userbot.py"

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

generate_plist() {
    cat <<EOF > "${PLIST_FILE}"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_BIN}</string>
        <string>-u</string>
        <string>${USERBOT_SCRIPT}</string>
        <string>--listen</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/telethon.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/telethon.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Library/Frameworks/Python.framework/Versions/3.13/bin:/Users/saber/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
    </dict>
</dict>
</plist>
EOF
}

stop_orphans() {
    # Kill any manually running instances of telethon_userbot to prevent SQLite lock on session
    local orphan_pids
    orphan_pids=$(pgrep -f "telethon_userbot.py" || true)
    if [ -n "$orphan_pids" ]; then
        echo "[*] Stopping existing telethon_userbot processes (PID: $orphan_pids)..."
        kill -9 $orphan_pids 2>/dev/null || true
        sleep 1
    fi
}

case "$1" in
    install)
        echo "[*] Installing macOS LaunchAgent for Telethon Userbot..."
        stop_orphans
        generate_plist
        echo "[+] Created: ${PLIST_FILE}"
        launchctl unload "${PLIST_FILE}" 2>/dev/null || true
        launchctl load -w "${PLIST_FILE}"
        echo "[+] Service '${PLIST_LABEL}' loaded and active!"
        echo "[+] Telethon is now set to run automatically 24/7 on macOS login."
        ;;

    start)
        if [ ! -f "${PLIST_FILE}" ]; then
            echo "[-] LaunchAgent plist not found. Running install first..."
            "$0" install
            exit 0
        fi
        stop_orphans
        launchctl load -w "${PLIST_FILE}"
        echo "[+] Telethon service started."
        ;;

    stop)
        echo "[*] Stopping Telethon service..."
        if [ -f "${PLIST_FILE}" ]; then
            launchctl unload "${PLIST_FILE}" 2>/dev/null || true
        fi
        stop_orphans
        echo "[+] Telethon service stopped."
        ;;

    restart)
        echo "[*] Restarting Telethon service..."
        "$0" stop
        sleep 1
        "$0" start
        ;;

    status)
        echo "=========================================================="
        echo "Telethon Background Service Status"
        echo "=========================================================="
        echo "Service Label: ${PLIST_LABEL}"
        echo "Plist Location: ${PLIST_FILE}"
        echo "Log File:       ${LOG_DIR}/telethon.log"
        echo "----------------------------------------------------------"
        
        # Check launchctl list
        if launchctl list | grep -q "${PLIST_LABEL}"; then
            echo "[✓] launchd state: REGISTERED"
            launchctl list | grep "${PLIST_LABEL}"
        else
            echo "[-] launchd state: NOT REGISTERED"
        fi

        # Check actual process
        pids=$(pgrep -f "telethon_userbot.py.*--listen" || true)
        if [ -n "$pids" ]; then
            echo "[✓] Process status: RUNNING (PID: $pids)"
        else
            echo "[-] Process status: NOT RUNNING"
        fi

        echo "----------------------------------------------------------"
        echo "Recent log entries (last 10 lines):"
        if [ -f "${LOG_DIR}/telethon.log" ]; then
            tail -n 10 "${LOG_DIR}/telethon.log"
        else
            echo "(Log file not created yet)"
        fi
        echo "=========================================================="
        ;;

    logs)
        if [ -f "${LOG_DIR}/telethon.log" ]; then
            echo "[*] Streaming live logs (Ctrl+C to exit)..."
            tail -f "${LOG_DIR}/telethon.log"
        else
            echo "[-] Log file not found at: ${LOG_DIR}/telethon.log"
        fi
        ;;

    uninstall)
        echo "[*] Removing Telethon LaunchAgent..."
        "$0" stop
        if [ -f "${PLIST_FILE}" ]; then
            rm -f "${PLIST_FILE}"
            echo "[+] Removed: ${PLIST_FILE}"
        fi
        echo "[+] LaunchAgent completely uninstalled."
        ;;

    *)
        echo "Usage: $0 {install|start|stop|restart|status|logs|uninstall}"
        echo ""
        echo "Commands:"
        echo "  install    : Create macOS LaunchAgent and start background daemon (runs on login)"
        echo "  start      : Start the background daemon via launchctl"
        echo "  stop       : Stop the background daemon"
        echo "  restart    : Restart the daemon"
        echo "  status     : Show process and service status with recent logs"
        echo "  logs       : Follow live output logs (tail -f)"
        echo "  uninstall  : Stop and remove the LaunchAgent plist"
        exit 1
        ;;
esac
