#!/usr/bin/env python3
"""
Comprehensive Ely.by Skin System Diagnostic
"""

import requests
import json
from pathlib import Path
from authlib_injector import AuthlibInjector
from elyby_auth import ElyByAuth

print("=" * 70)
print("ELY.BY SKIN SYSTEM DIAGNOSTIC")
print("=" * 70)
print()

# 1. Check authlib-injector
print("1. AUTHLIB-INJECTOR CHECK")
print("-" * 70)
injector = AuthlibInjector()
info = injector.get_info()

if info['installed']:
    print(f"✓ Installed: {info['path']}")
    print(f"  Size: {info['size_mb']} MB")
    
    # Check if file is valid
    if info['size_mb'] < 0.1:
        print("  ⚠ WARNING: File seems too small, might be corrupted")
        print("  Recommendation: Delete and re-download")
else:
    print("✗ Not installed")
    print("  Recommendation: Will auto-download on first launch")

print()

# 2. Check Ely.by API endpoint
print("2. ELY.BY API ENDPOINT CHECK")
print("-" * 70)
try:
    response = requests.get(
        "https://authserver.ely.by/api/authlib-injector",
        timeout=10,
        headers={"User-Agent": "authlib-injector"}
    )
    print(f"✓ Status: {response.status_code}")
    print(f"  Content-Type: {response.headers.get('Content-Type')}")
    print(f"  Content-Length: {len(response.content)} bytes")
    
    # Parse JSON
    data = response.json()
    print(f"  Server: {data.get('meta', {}).get('serverName')}")
    print(f"  Skin Domains: {', '.join(data.get('skinDomains', []))}")
    print(f"  ✓ Valid JSON metadata")
    
except Exception as e:
    print(f"✗ Error: {e}")
    print("  Recommendation: Check internet connection")

print()

# 3. Check Ely.by authentication
print("3. ELY.BY AUTHENTICATION CHECK")
print("-" * 70)
elyby = ElyByAuth()
auth_data = elyby.get_stored_auth()

if auth_data:
    print(f"✓ Logged in as: {auth_data['username']}")
    print(f"  UUID: {auth_data['uuid']}")
    
    # Validate token
    if elyby.validate_token():
        print(f"  ✓ Token is valid")
    else:
        print(f"  ⚠ Token expired")
        print(f"  Recommendation: Token will auto-refresh on launch")
else:
    print("✗ Not logged in")
    print("  Recommendation: Click 'Ely.by Login' button in launcher")

print()

# 4. Check JVM arguments
print("4. JVM ARGUMENTS CHECK")
print("-" * 70)
if info['installed']:
    args = injector.get_jvm_args()
    for arg in args:
        print(f"  {arg}")
    
    # Check for path issues
    if '\\' in args[0] and '/' not in args[0]:
        print("  ⚠ WARNING: Backslashes in path might cause issues")
        print("  Recommendation: Path should use forward slashes")
else:
    print("  (Authlib-injector not installed)")

print()

# 5. Check log file
print("5. AUTHLIB-INJECTOR LOG CHECK")
print("-" * 70)
log_file = Path.home() / ".minecraft" / "authlib-injector.log"

if log_file.exists():
    print(f"✓ Log file exists: {log_file}")
    print()
    print("Last 20 lines:")
    print("-" * 70)
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line in lines[-20:]:
                print(f"  {line.rstrip()}")
    except Exception as e:
        print(f"  Error reading log: {e}")
else:
    print("✗ Log file not found")
    print("  This is normal if you haven't launched Minecraft yet")

print()
print("=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print()
print("RECOMMENDATIONS:")
print("1. Make sure you're logged into Ely.by")
print("2. Launch Minecraft and check if skins appear")
print("3. If skins don't work, check authlib-injector.log for errors")
print("4. Try Minecraft 1.16+ for best compatibility")
print()
