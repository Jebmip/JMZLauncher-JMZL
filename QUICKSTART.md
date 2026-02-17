# Quick Start Guide

## Step 1: Install Python
Make sure you have Python 3.7 or higher installed.

Check by opening Command Prompt (cmd) and typing:
```
python --version
```

If you don't have Python, download it from: https://www.python.org/downloads/

## Step 2: Install Java
You need Java 17 or newer for Ely.by support.

Check your Java version:
```
java -version
```

If you don't have Java 17+, download from: https://adoptium.net/

## Step 3: Install Dependencies
Open Command Prompt in this folder and run:
```
pip install -r requirements.txt
```

## Step 4: Create Ely.by Account
1. Go to https://ely.by
2. Register for a free account
3. Upload a skin (optional, but recommended)

## Step 5: Run the Launcher

### Option A: Double-click (Easiest)
Just double-click `launch.bat`

### Option B: Command Line
Open Command Prompt in this folder and run:
```
python launcher_gui.py
```

## Step 6: Login to Ely.by
1. Click "🔐 Ely.by Login" button
2. Enter your Ely.by username/email and password
3. Click "Login"
4. You should see "✓ Logged in as: [YourUsername]"

## Step 7: Download Minecraft
1. Click "⬇ Download" button
2. Wait for the version list to load
3. Select a version (1.20 or 1.21 recommended)
4. Click "Download Selected"
5. Wait for it to finish (this takes a few minutes)

## Step 8: Play!
1. Select the version you downloaded
2. Click "▶ PLAY"
3. Minecraft will launch with your Ely.by account!

## Troubleshooting

### Skins Not Showing?
**Read this first:** `START_HERE.md`

Quick fix:
```bash
python diagnose_elyby.py
```

### Common Issues

**"python is not recognized"**
- Python is not installed or not in PATH
- Reinstall Python and check "Add Python to PATH" during installation

**"No module named 'requests'"**
- Run: `pip install -r requirements.txt`

**"Java not found" when launching**
- Install Java 17+ from: https://adoptium.net/
- Make sure Java is in your system PATH

**Can't login to Ely.by**
- Check your credentials at https://ely.by
- Make sure you have internet connection
- Check if Ely.by service is online

**Game won't launch**
- Make sure you're logged into Ely.by
- Make sure you fully downloaded the version
- Check that Java 17+ is installed
- Try Minecraft 1.20 or 1.21

**Where are my files?**
- Files are stored in: `C:\Users\YourUsername\.minecraft`
- Click the "📁 Folder" button in the launcher to open it
- Or press Win+R and type: `%USERPROFILE%\.minecraft`

## Need More Help?

- **Skins not working?** Read `START_HERE.md`
- **Quick diagnostic:** Run `python diagnose_elyby.py`
- **Detailed help:** Read `ELYBY_TROUBLESHOOTING.md`
- **Project status:** Read `PROJECT_STATUS.md`
