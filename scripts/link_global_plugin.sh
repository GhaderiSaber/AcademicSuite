#!/usr/bin/env bash
# scripts/link_global_plugin.sh — Symlinks AcademicSuite into global Antigravity plugins directory
# Enables instant cross-project propagation of skills, rules, hooks, and agent capabilities.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLUGIN_SRC="${REPO_ROOT}/.agents/plugins/academic-suite"
GLOBAL_PLUGINS_DIR="${HOME}/.gemini/config/plugins"
GLOBAL_TARGET="${GLOBAL_PLUGINS_DIR}/academic-suite"

echo "[link_global_plugin] Ensuring global plugins directory exists: ${GLOBAL_PLUGINS_DIR}"
mkdir -p "${GLOBAL_PLUGINS_DIR}"

echo "[link_global_plugin] Linking ${PLUGIN_SRC} -> ${GLOBAL_TARGET}"
ln -sfn "${PLUGIN_SRC}" "${GLOBAL_TARGET}"

if [ -L "${GLOBAL_TARGET}" ] && [ -e "${GLOBAL_TARGET}" ]; then
    echo "[link_global_plugin] Successfully linked AcademicSuite plugin to ${GLOBAL_TARGET}."
    echo "[link_global_plugin] Any updates in AcademicSuite will now automatically propagate to all active workspaces."
else
    echo "[link_global_plugin] ERROR: Failed to establish valid symlink at ${GLOBAL_TARGET}" >&2
    exit 1
fi
