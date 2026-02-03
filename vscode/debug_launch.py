#!/usr/bin/env python3
import os
import re
import json

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
VSCODE_DIR = os.path.join(REPO_ROOT, ".vscode")
LAUNCH_JSON_PATH = os.path.join(VSCODE_DIR, "launch.json")

DEBUG_PORT_REGEX = re.compile(r'--listen\s+(?:[0-9.]+:)?([0-9]+)')

# --- Scan folders for Makefiles ---
new_configs = []

for entry in os.scandir(REPO_ROOT):
    if entry.is_dir():
        makefile_path = os.path.join(entry.path, "Makefile")
        if os.path.exists(makefile_path):
            with open(makefile_path, "r") as f:
                content = f.read()

            # Extract all debugpy ports
            ports = DEBUG_PORT_REGEX.findall(content)
            if ports:
                folder_name = entry.name
                for port in ports:
                    config = {
                        "name": folder_name,
                        "type": "debugpy",
                        "request": "attach",
                        "connect": {"host": "localhost", "port": int(port)},
                        "pathMappings": [
                            {
                                "localRoot": f"${{workspaceFolder}}/{folder_name}",
                                "remoteRoot": f"${{workspaceFolder}}/{folder_name}"
                            }
                        ]
                    }
                    new_configs.append(config)

# --- Load existing launch.json if exists ---
if os.path.exists(LAUNCH_JSON_PATH):
    with open(LAUNCH_JSON_PATH, "r") as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = {"version": "0.2.0", "configurations": []}
else:
    existing_data = {"version": "0.2.0", "configurations": []}

existing_configs = existing_data.get("configurations", [])

# --- Merge configs (avoid duplicates by name) ---
merged_configs = {cfg["name"]: cfg for cfg in existing_configs}
for cfg in new_configs:
    merged_configs[cfg["name"]] = cfg  # overwrite or add

final_data = {
    "version": "0.2.0",
    "configurations": list(merged_configs.values())
}

# --- Ensure .vscode folder exists ---
os.makedirs(VSCODE_DIR, exist_ok=True)

# --- Write launch.json ---
with open(LAUNCH_JSON_PATH, "w") as f:
    json.dump(final_data, f, indent=2)

print(f"launch.json updated at {LAUNCH_JSON_PATH}")
for c in final_data["configurations"]:
    print(f"- {c['name']}: port {c['connect']['port']}")
