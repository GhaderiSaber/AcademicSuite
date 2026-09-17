#!/usr/bin/env bash
# ==============================================================================
# telethon_service.sh — Telethon Userbot Background Service Manager
# Supports Linux (systemd --user) and macOS (launchd)
# ==============================================================================
# Features:
#   - Starts automatically on system boot / user login
#   - Runs silently in the background 24/7
#   - Auto-restarts on network disconnection or crash
#   - Real-time unbuffered logging to userbot_storage/telethon.log
# ==============================================================================

set -e

SERVICE_LABEL="telethon-userbot"
PLIST_LABEL="com.saber.telethon-userbot"

# Resolve script directory and AcademicSuite root
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
    DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

# Find AcademicSuite root directory
if [ -d "${SCRIPT_DIR}/../.agents" ]; then
    ROOT_DIR="$(cd -P "${SCRIPT_DIR}/.." && pwd)"
elif [ -d "${SCRIPT_DIR}/../../../../.agents" ]; then
    ROOT_DIR="$(cd -P "${SCRIPT_DIR}/../../../.." && pwd)"
else
    ROOT_DIR="$(cd -P "${SCRIPT_DIR}/.." && pwd)"
fi

USERBOT_DIR="${ROOT_DIR}/.agents/skills/digital-twin-academic-consultant/scripts"
USERBOT_SCRIPT="${USERBOT_DIR}/telethon_userbot.py"
LOG_DIR="${USERBOT_DIR}/userbot_storage"

# Resolve Python binary (prefer virtualenv)
if [ -f "${ROOT_DIR}/.venv/bin/python" ]; then
    PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
elif [ -f "${USERBOT_DIR}/.venv/bin/python" ]; then
    PYTHON_BIN="${USERBOT_DIR}/.venv/bin/python"
else
    PYTHON_BIN="$(which python3)"
fi

OS_TYPE="$(uname -s)"
SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"
SYSTEMD_SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_LABEL}.service"
PLIST_FILE="${HOME}/Library/LaunchAgents/${PLIST_LABEL}.plist"

mkdir -p "${LOG_DIR}"

stop_orphans() {
    local orphan_pids
    orphan_pids=$(pgrep -f "telethon_userbot.py.*--listen" || true)
    if [ -n "$orphan_pids" ]; then
        echo "[*] Stopping existing telethon_userbot processes (PID: $orphan_pids)..."
        kill -9 $orphan_pids 2>/dev/null || true
        sleep 1
    fi
}

install_linux() {
    echo "[*] Installing systemd user service for Linux..."
    mkdir -p "${SYSTEMD_USER_DIR}"
    cat <<EOF > "${SYSTEMD_SERVICE_FILE}"
[Unit]
Description=Digital Saber Telethon Userbot Background Service
After=network.target

[Service]
Type=simple
WorkingDirectory=${USERBOT_DIR}
ExecStart=${PYTHON_BIN} -u ${USERBOT_SCRIPT} --listen
Restart=always
RestartSec=10
StandardOutput=append:${LOG_DIR}/telethon.log
StandardError=append:${LOG_DIR}/telethon.error.log
Environment="PYTHONUNBUFFERED=1"
Environment="PATH=$(dirname ${PYTHON_BIN}):/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable --now "${SERVICE_LABEL}.service"
    echo "[+] Created: ${SYSTEMD_SERVICE_FILE}"
    echo "[+] Systemd user service '${SERVICE_LABEL}.service' enabled and started!"
}

install_macos() {
    echo "[*] Installing macOS LaunchAgent for Telethon Userbot..."
    mkdir -p "${HOME}/Library/LaunchAgents"
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
    <string>${USERBOT_DIR}</string>
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
        <string>$(dirname ${PYTHON_BIN}):/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
    </dict>
</dict>
</plist>
EOF
    launchctl unload "${PLIST_FILE}" 2>/dev/null || true
    launchctl load -w "${PLIST_FILE}"
    echo "[+] Created: ${PLIST_FILE}"
    echo "[+] Service '${PLIST_LABEL}' loaded and active!"
}

case "$1" in
    install)
        stop_orphans
        if [ "$OS_TYPE" = "Darwin" ]; then
            install_macos
        else
            install_linux
        fi
        echo "[+] Telethon is now set to run automatically 24/7 on system login."
        ;;

    start)
        stop_orphans
        if [ "$OS_TYPE" = "Darwin" ]; then
            if [ ! -f "${PLIST_FILE}" ]; then
                "$0" install
                exit 0
            fi
            launchctl load -w "${PLIST_FILE}"
        else
            if [ ! -f "${SYSTEMD_SERVICE_FILE}" ]; then
                "$0" install
                exit 0
            fi
            systemctl --user start "${SERVICE_LABEL}.service"
        fi
        echo "[+] Telethon service started."
        ;;

    stop)
        echo "[*] Stopping Telethon service..."
        if [ "$OS_TYPE" = "Darwin" ]; then
            if [ -f "${PLIST_FILE}" ]; then
                launchctl unload "${PLIST_FILE}" 2>/dev/null || true
            fi
        else
            systemctl --user stop "${SERVICE_LABEL}.service" 2>/dev/null || true
        fi
        stop_orphans
        echo "[+] Telethon service stopped."
        ;;

    restart)
        echo "[*] Restarting Telethon service..."
        bash "$0" stop
        sleep 1
        bash "$0" start
        ;;

    run)
        echo "[*] Running Telethon userbot directly in foreground (Ctrl+C to exit)..."
        stop_orphans
        exec "${PYTHON_BIN}" -u "${USERBOT_SCRIPT}" --listen
        ;;

    status)
        echo "=========================================================="
        echo "Telethon Background Service Status"
        echo "=========================================================="
        echo "OS Detected:    ${OS_TYPE}"
        echo "Python:         ${PYTHON_BIN}"
        echo "Script:         ${USERBOT_SCRIPT}"
        echo "Log File:       ${LOG_DIR}/telethon.log"
        echo "----------------------------------------------------------"
        
        if [ "$OS_TYPE" = "Darwin" ]; then
            if launchctl list | grep -q "${PLIST_LABEL}"; then
                echo "[✓] launchd state: REGISTERED"
            else
                echo "[-] launchd state: NOT REGISTERED"
            fi
        else
            if systemctl --user is-active --quiet "${SERVICE_LABEL}.service" 2>/dev/null; then
                echo "[✓] systemd state: ACTIVE (Running)"
            else
                echo "[-] systemd state: INACTIVE"
            fi
        fi

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
        if [ "$OS_TYPE" != "Darwin" ] && systemctl --user is-active --quiet "${SERVICE_LABEL}.service" 2>/dev/null; then
            echo "[*] Streaming live logs via journalctl + log file (Ctrl+C to exit)..."
            journalctl --user -u "${SERVICE_LABEL}.service" -f -n 50
        elif [ -f "${LOG_DIR}/telethon.log" ]; then
            echo "[*] Streaming live logs (Ctrl+C to exit)..."
            tail -f "${LOG_DIR}/telethon.log"
        else
            echo "[-] Log file not found at: ${LOG_DIR}/telethon.log"
        fi
        ;;

    triage)
        shift
        "${PYTHON_BIN}" "${ROOT_DIR}/scripts/triage_projects.py" "$@"
        ;;

    uninstall)
        echo "[*] Removing Telethon service..."
        bash "$0" stop
        if [ "$OS_TYPE" = "Darwin" ]; then
            rm -f "${PLIST_FILE}"
        else
            systemctl --user disable "${SERVICE_LABEL}.service" 2>/dev/null || true
            rm -f "${SYSTEMD_SERVICE_FILE}"
            systemctl --user daemon-reload
        fi
        echo "[+] Service completely uninstalled."
        ;;

    *)
        echo "Usage: $0 {install|start|stop|restart|run|status|logs|triage|uninstall}"
        echo ""
        echo "Commands:"
        echo "  install    : Create service and start background daemon (runs 24/7 on login)"
        echo "  start      : Start background daemon"
        echo "  stop       : Stop background daemon"
        echo "  restart    : Restart daemon"
        echo "  run        : Run directly in foreground (for testing/debugging)"
        echo "  status     : Show process and service status with recent logs"
        echo "  logs       : Follow live output logs"
        echo "  triage     : Scan and organize inactive client projects (use --execute to apply)"
        echo "  uninstall  : Stop and remove the service"
        exit 1
        ;;
esac
