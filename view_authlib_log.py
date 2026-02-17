#!/usr/bin/env python3
"""
View authlib-injector log file
"""

from pathlib import Path
import sys

log_file = Path.home() / ".minecraft" / "authlib-injector.log"

print("=" * 70)
print("AUTHLIB-INJECTOR LOG VIEWER")
print("=" * 70)
print()
print(f"Log file: {log_file}")
print()

if not log_file.exists():
    print("✗ Log file not found!")
    print()
    print("This is normal if you haven't launched Minecraft yet.")
    print("The log file is created when Minecraft starts with authlib-injector.")
    print()
    print("To create the log:")
    print("1. Make sure you're logged into Ely.by")
    print("2. Launch Minecraft from the launcher")
    print("3. Run this script again")
    print()
    sys.exit(0)

print("✓ Log file found")
print()

try:
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.split('\n')
    print(f"Total lines: {len(lines)}")
    print()
    
    # Check for errors
    errors = [line for line in lines if '[ERROR]' in line or '[FATAL]' in line]
    warnings = [line for line in lines if '[WARN]' in line]
    
    if errors:
        print(f"⚠ Found {len(errors)} ERROR(S):")
        print("-" * 70)
        for error in errors:
            print(f"  {error}")
        print()
    
    if warnings:
        print(f"⚠ Found {len(warnings)} WARNING(S):")
        print("-" * 70)
        for warning in warnings[:5]:  # Show first 5
            print(f"  {warning}")
        if len(warnings) > 5:
            print(f"  ... and {len(warnings) - 5} more warnings")
        print()
    
    if not errors and not warnings:
        print("✓ No errors or warnings found!")
        print()
    
    # Show full log
    print("=" * 70)
    print("FULL LOG CONTENT:")
    print("=" * 70)
    print()
    print(content)
    print()
    print("=" * 70)
    print("END OF LOG")
    print("=" * 70)
    print()
    
    # Analysis
    if '[ERROR]' in content and 'Invalid JSON' in content:
        print("ANALYSIS:")
        print("-" * 70)
        print("✗ Found 'Invalid JSON' error")
        print()
        print("This means authlib-injector cannot fetch or parse the metadata")
        print("from Ely.by's API endpoint.")
        print()
        print("Possible causes:")
        print("1. Firewall blocking Java's network access")
        print("2. Java version too old (SSL/TLS issues)")
        print("3. Network timeout or connectivity issues")
        print("4. Antivirus interfering with Java")
        print()
        print("Solutions:")
        print("1. Update Java to version 17 or newer")
        print("2. Check Windows Firewall settings for Java")
        print("3. Temporarily disable antivirus and try again")
        print("4. Run: python test_java_network.py")
        print()
        print("For more help, see: ELYBY_TROUBLESHOOTING.md")
        print()
    elif '[INFO]' in content and 'Metadata loaded' in content:
        print("ANALYSIS:")
        print("-" * 70)
        print("✓ Metadata loaded successfully!")
        print()
        print("Authlib-injector is working correctly.")
        print("If skins still don't show, the issue might be:")
        print("1. Minecraft version compatibility")
        print("2. Skin not uploaded to Ely.by account")
        print("3. In-game skin settings")
        print()
        print("Check:")
        print("1. Make sure your Ely.by account has a skin uploaded")
        print("2. Try Minecraft 1.16 or newer")
        print("3. Check in-game skin settings")
        print()
    
except Exception as e:
    print(f"✗ Error reading log file: {e}")
    print()

print("To run diagnostics: python diagnose_elyby.py")
print("For troubleshooting: see ELYBY_TROUBLESHOOTING.md")
print()
