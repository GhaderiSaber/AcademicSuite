#!/usr/bin/env bash
# ==============================================================================
# Digital Saber Academic Suite — Environment Bootstrapper (bootstrap_env.sh)
# ==============================================================================
# Prepares the isolated Python virtual environment (.venv) and installs the
# core scientific and document generation dependencies (pandas, numpy, scipy, docx).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${WORKSPACE_ROOT}"

echo "================================================================================"
echo "🏛️  Digital Saber Academic Suite — Local Environment Setup"
echo "================================================================================"

# 1. Check for uv (fastest) or python3
if command -v uv >/dev/null 2>&1; then
    echo "⚡ Found 'uv' package manager. Creating virtual environment..."
    uv venv .venv --python python3
    echo "📦 Installing requirements via uv pip..."
    uv pip install -r requirements.txt --python .venv/bin/python
elif command -v python3 >/dev/null 2>&1; then
    echo "🐍 Using system python3: $(python3 --version)"
    if python3 -m venv --help >/dev/null 2>&1; then
        echo "Creating virtual environment at .venv..."
        python3 -m venv .venv || {
            echo "⚠️  Standard venv creation failed (ensurepip may be missing)."
            echo "    On Ubuntu/Debian: sudo apt update && sudo apt install -y python3-venv python3-pip"
            exit 1
        }
        echo "📦 Installing requirements via pip..."
        .venv/bin/pip install --upgrade pip
        .venv/bin/pip install -r requirements.txt
    else
        echo "❌ python3-venv module is not installed."
        echo "   Please install it via: sudo apt install -y python3-venv python3-pip"
        exit 1
    fi
else
    echo "❌ Neither 'uv' nor 'python3' was found on your PATH."
    exit 1
fi

echo "--------------------------------------------------------------------------------"
echo "✅ Environment successfully bootstrapped in ${WORKSPACE_ROOT}/.venv"
echo "   To activate: source .venv/bin/activate"
echo "   To run tests: .venv/bin/python run_tests.py"
echo "================================================================================"
