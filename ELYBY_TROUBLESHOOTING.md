# Ely.by Skin System Troubleshooting Guide

## Current Issue
Skins not showing in-game despite successful Ely.by login.

## Error in Logs
```
[authlib-injector] [ERROR] Unable to parse metadata: java.io.IOException: Invalid JSON
Raw metadata:???
```

## What This Means
The authlib-injector is unable to fetch or parse the metadata from Ely.by's API endpoint. The "???" suggests corrupted or incomplete data.

## Possible Causes

### 1. Network/Firewall Issues
- Java might be blocked from making HTTPS requests
- Corporate firewall blocking the connection
- Antivirus interfering with network requests

### 2. Java Version Issues
- Older Java versions might have SSL/TLS compatibility issues
- Try using Java 17 or newer

### 3. Encoding Issues
- Windows path encoding problems
- URL encoding issues in the javaagent parameter

### 4. Authlib-Injector Version
- Corrupted download
- Incompatible version

## Solutions to Try

### Solution 1: Run Diagnostic
```bash
python diagnose_elyby.py
```
This will check all components and show you exactly what's wrong.

### Solution 2: Re-download Authlib-Injector
1. Delete the file: `C:\Users\[YourName]\.minecraft\authlib-injector\authlib-injector.jar`
2. Launch the launcher again (it will auto-download)

### Solution 3: Check Java Version
```bash
java -version
```
Make sure you're using Java 17 or newer. Older versions may have SSL issues.

### Solution 4: Manual Test
Run this to test if Java can access the Ely.by API:
```bash
python test_authlib_command.py
```

### Solution 5: Check Firewall/Antivirus
- Temporarily disable antivirus
- Check Windows Firewall settings for Java
- Make sure Java can make HTTPS connections

### Solution 6: Try Different Minecraft Version
- Ely.by works best with Minecraft 1.16+
- Try launching 1.20 or 1.21 instead of older versions

### Solution 7: Check the Log File
After launching Minecraft, check:
```
C:\Users\[YourName]\.minecraft\authlib-injector.log
```

Look for specific error messages that might give more clues.

## Expected Behavior

When working correctly, you should see:
```
[authlib-injector] [INFO] Logging file: C:\Users\...\authlib-injector.log
[authlib-injector] [INFO] Version: 1.2.7
[authlib-injector] [INFO] Authentication server: https://authserver.ely.by/api/authlib-injector
[authlib-injector] [INFO] Metadata loaded successfully
```

## Alternative: Use Without Authlib-Injector

If authlib-injector continues to fail, you can still play with your Ely.by account, but skins might not work. The authentication will still function for multiplayer servers that support Ely.by.

## Getting Help

If none of these solutions work:
1. Run `python diagnose_elyby.py` and save the output
2. Check `authlib-injector.log` for detailed errors
3. Note your Java version and Minecraft version
4. Check if you can access https://authserver.ely.by/api/authlib-injector in your browser

## Known Working Configuration

- Windows 10/11
- Java 17 or newer
- Minecraft 1.16+
- Ely.by account with uploaded skin
- No restrictive firewall/antivirus
