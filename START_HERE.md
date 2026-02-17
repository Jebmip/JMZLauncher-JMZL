# Ely.by Skins Not Working? Start Here

## Quick Fix

### 1. Check Java Version
```bash
java -version
```
**Need Java 17 or newer.** Download from https://adoptium.net/

### 2. Run Diagnostic
```bash
python diagnose_elyby.py
```
This checks everything and tells you what's wrong.

### 3. Test Java Network
```bash
python test_java_network.py
```
If this fails → Java can't connect (firewall/antivirus issue)  
If this succeeds → Authlib-injector issue

### 4. Check the Log
```bash
python view_authlib_log.py
```
Shows errors from authlib-injector.

## Common Solutions

| Problem | Solution |
|---------|----------|
| Java < 17 | Update from https://adoptium.net/ |
| Network test fails | Check firewall, disable antivirus temporarily |
| Authlib-injector file small | Delete `.minecraft/authlib-injector/authlib-injector.jar` and restart launcher |
| Not logged in | Click "🔐 Ely.by Login" in launcher |

## The Issue

Error: `[authlib-injector] [ERROR] Unable to parse metadata: java.io.IOException: Invalid JSON`

This means Java can't fetch metadata from Ely.by. Usually caused by:
- Firewall blocking Java
- Old Java version (SSL/TLS issues)
- Antivirus interference

## Most Likely Fix

1. Update Java to 17+
2. Check Windows Firewall for Java
3. Temporarily disable antivirus and test

## Need More Help?

Read `ELYBY_TROUBLESHOOTING.md` for detailed solutions.

## Files to Check

After launching Minecraft:
- Log: `C:\Users\[Name]\.minecraft\authlib-injector.log`
- JAR: `C:\Users\[Name]\.minecraft\authlib-injector\authlib-injector.jar` (should be ~300-500 KB)

## Quick Commands

```bash
# Run all diagnostics (Windows)
run_diagnostics.bat

# Individual tests
python diagnose_elyby.py
python test_java_network.py
python view_authlib_log.py
```
