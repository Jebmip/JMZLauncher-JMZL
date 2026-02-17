# JMZLauncher

A modern Minecraft launcher with Ely.by authentication and modpack support.

## Features

- Download any Minecraft version from official Mojang servers
- Launch Minecraft with Ely.by authentication (mandatory)
- Modern dark-themed GUI
- Modrinth modpack support (Fabric/Quilt)
- Secure downloads with SHA1 verification
- Version management (download, delete, refresh)
- Ely.by skin system integration

## Requirements

- Python 3.7+
- Java Runtime Environment (JRE) 17 or higher (recommended for Ely.by support)
- Internet connection for downloading
- Ely.by account (required to play) - Register at https://ely.by

## Installation

1. Install required Python packages:
```bash
pip install -r requirements.txt
```

2. Make sure Java 17+ is installed and in your PATH:
```bash
java -version
```

3. Create an Ely.by account at https://ely.by (required to play)

## Usage

### GUI Mode (Recommended)

Run the launcher:
```bash
python launcher_gui.py
```

Or use the batch file:
```bash
launch.bat
```

The GUI allows you to:
- Login with your Ely.by account (required)
- Select installed Minecraft versions
- Download new versions with one click
- Browse and install Modrinth modpacks
- Launch the game with your Ely.by skin
- View console output and logs
- Manage installed versions

### First Time Setup

1. Launch the GUI
2. Click "🔐 Ely.by Login"
3. Enter your Ely.by credentials
4. Click "⬇ Download" to get a Minecraft version
5. Select the version and click "▶ PLAY"

### Command Line Mode (Advanced)

You can still use command-line mode for automation:

```bash
# Download a version
python minecraft_downloader.py download 1.20.1

# Launch (requires Ely.by login first)
python minecraft_launcher.py 1.20.1
```

## File Structure

```
C:\Users\YourUsername\.minecraft\
├── versions/
│   └── 1.20.1/
│       ├── 1.20.1.json
│       └── 1.20.1.jar
├── libraries/
│   └── ... (downloaded libraries)
└── assets/
    ├── indexes/
    └── objects/
```

Files are stored in your user home directory at `.minecraft`

## Notes

- Ely.by authentication is mandatory - you must login to play
- Your Ely.by skin will appear in-game (if properly configured)
- Game files are stored in `C:\Users\YourUsername\.minecraft`
- Authlib-injector is downloaded automatically on first launch
- Click the "📁 Folder" button in the launcher to open the game directory
- Use Minecraft 1.16+ for best Ely.by compatibility
- Modpacks feature is experimental (Fabric/Quilt only, no Forge yet)

## Security Features

- SHA1 hash verification for all downloads
- Input validation for usernames and version names
- Main class whitelist to prevent arbitrary code execution
- Classpath validation to prevent directory traversal
- All downloads from official Mojang servers

## Project Status

See `PROJECT_STATUS.md` for current development status and known issues.

## Troubleshooting

### Ely.by Skins Not Showing

If you're logged in but skins don't appear in-game:

1. **Run diagnostics:**
   ```bash
   python diagnose_elyby.py
   ```

2. **Test Java network connectivity:**
   ```bash
   python test_java_network.py
   ```

3. **Check your Java version:**
   ```bash
   java -version
   ```
   Use Java 17 or newer for best compatibility.

4. **Read the troubleshooting guide:**
   See `ELYBY_TROUBLESHOOTING.md` for detailed solutions.

For a quick start, see `START_HERE.md`

### Other Issues

**Java not found:**
- Make sure Java 17+ is installed and in your system PATH
- Try running `java -version` to verify

**Download fails:**
- Check your internet connection
- Try downloading again (existing files are skipped)

**Game won't launch:**
- Make sure you're logged into Ely.by
- Verify the version was fully downloaded
- Check that you have enough RAM (2GB minimum)
- Try Minecraft 1.20+ for best compatibility

**Can't login to Ely.by:**
- Check your credentials at https://ely.by
- Make sure you have internet connection
- Check if Ely.by service is online
