#!/usr/bin/env python3
"""
Create a backup of the launcher files
"""

import shutil
import os
from pathlib import Path
from datetime import datetime

# Get current directory
current_dir = Path.cwd()

# Create backup folder name with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_folder = current_dir / f"launcher_backup_{timestamp}"

print("=" * 60)
print("JMZ MINECRAFT LAUNCHER - BACKUP UTILITY")
print("=" * 60)
print()

# Files to backup
files_to_backup = [
    "launcher_gui.py",
    "minecraft_downloader.py",
    "minecraft_launcher.py",
    "elyby_auth.py",
    "elyby_login_gui.py",
    "authlib_injector.py",
    "modrinth_manager.py",
    "modpacks_gui.py",
    "mod_loader_installer.py",
    "launch.bat",
    "requirements.txt",
    "README.md",
    "QUICKSTART.md",
    "SECURITY.md",
    "PROJECT_STATUS.md"
]

print(f"Creating backup folder: {backup_folder.name}")
backup_folder.mkdir(exist_ok=True)

print()
print("Backing up files:")
backed_up = 0
for file in files_to_backup:
    source = current_dir / file
    if source.exists():
        destination = backup_folder / file
        shutil.copy2(source, destination)
        print(f"  ✓ {file}")
        backed_up += 1
    else:
        print(f"  ✗ {file} (not found)")

print()
print("=" * 60)
print(f"Backup complete! {backed_up}/{len(files_to_backup)} files backed up")
print(f"Location: {backup_folder}")
print("=" * 60)
print()

input("Press Enter to exit...")
