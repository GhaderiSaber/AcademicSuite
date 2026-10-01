#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/scripts/install_plugin.py — Cross-Platform Installer for AcademicSuite Antigravity Plugin

Installs the AcademicSuite plugin globally across any system (Linux, macOS, Windows):
1. Locates the global Antigravity config directory (~/.gemini/config/).
2. Attempts to establish a symbolic link to .agents/plugins/academic-suite/.
3. If symlinking is restricted (e.g., Windows without Developer Mode), falls back to
   registering the plugin path in ~/.gemini/config/plugins.json.
4. Ensures all future or existing projects automatically inherit AcademicSuite rules,
   skills, agents, and hooks.
"""

import os
import sys
import json
import platform

def install_plugin():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    plugin_src = os.path.join(repo_root, ".agents", "plugins", "academic-suite")

    if not os.path.isdir(plugin_src):
        print(f"[ERROR] Plugin directory not found at: {plugin_src}", file=sys.stderr)
        sys.exit(1)

    home_dir = os.path.expanduser("~")
    gemini_config_dir = os.path.join(home_dir, ".gemini", "config")
    plugins_dir = os.path.join(gemini_config_dir, "plugins")
    target_link = os.path.join(plugins_dir, "academic-suite")
    plugins_json_path = os.path.join(gemini_config_dir, "plugins.json")

    print(f"=== AcademicSuite Antigravity 2.18 Plugin Installer ===")
    print(f"OS: {platform.system()} ({platform.release()})")
    print(f"Source: {plugin_src}")
    print(f"Global Target: {target_link}")

    os.makedirs(plugins_dir, exist_ok=True)

    # Strategy 1: Symbolic Link (Linux / macOS / Windows with Developer Mode)
    linked = False
    try:
        if os.path.islink(target_link):
            os.remove(target_link)
        elif os.path.exists(target_link):
            import shutil
            shutil.rmtree(target_link)

        os.symlink(plugin_src, target_link, target_is_directory=True)
        linked = True
        print(f"[SUCCESS] Established symlink: {target_link} -> {plugin_src}")
    except OSError as e:
        print(f"[INFO] Direct symlink creation failed ({e}). Falling back to plugins.json registration.")

    # Strategy 2: plugins.json Fallback (guaranteed cross-platform support)
    if not linked:
        config_data = {"entries": []}
        if os.path.isfile(plugins_json_path):
            try:
                with open(plugins_json_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                config_data = {"entries": []}

        entries = config_data.get("entries", [])
        existing_paths = [e.get("path") for e in entries if isinstance(e, dict)]
        if plugin_src not in existing_paths:
            entries.append({"path": plugin_src})
            config_data["entries"] = entries
            with open(plugins_json_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
            print(f"[SUCCESS] Registered plugin in {plugins_json_path}")
        else:
            print(f"[INFO] Plugin already registered in {plugins_json_path}")

    print("\nAcademicSuite is now globally active in Antigravity on this machine!")
    print("Every workspace will now automatically discover AcademicSuite skills, agents, rules, and hooks.")

if __name__ == "__main__":
    install_plugin()
