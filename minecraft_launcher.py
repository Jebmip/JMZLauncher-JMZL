#!/usr/bin/env python3
"""
Simple Minecraft Launcher
Launches Minecraft Java Edition from the terminal
"""

import os
import json
import subprocess
import sys
import re
from pathlib import Path

class MinecraftLauncher:
    def __init__(self, game_dir=None, use_elyby=True):
        """Initialize the launcher with game directory"""
        if game_dir is None:
            self.game_dir = Path.home() / ".minecraft"
        else:
            self.game_dir = Path(game_dir)
        
        self.game_dir.mkdir(parents=True, exist_ok=True)
        self.versions_dir = self.game_dir / "versions"
        self.libraries_dir = self.game_dir / "libraries"
        self.assets_dir = self.game_dir / "assets"
        self.use_elyby = use_elyby
        
        # Initialize authlib-injector for Ely.by
        if use_elyby:
            from authlib_injector import AuthlibInjector
            self.authlib_injector = AuthlibInjector(game_dir)
            self.authlib_injector.ensure_injector()
        else:
            self.authlib_injector = None
        
    def launch(self, version, username="Player", elyby_auth=None):
        """Launch Minecraft with specified version and username"""
        print(f"Launching Minecraft {version} as {username}...")
        
        # Validate version name (prevent directory traversal)
        if not self._is_safe_version_name(version):
            print(f"Error: Invalid version name '{version}'")
            return False
        
        # Validate username (prevent command injection)
        if not self._is_safe_username(username):
            print(f"Error: Invalid username '{username}'")
            print("Username must be 3-16 characters, alphanumeric and underscores only")
            return False
        
        version_dir = self.versions_dir / version
        version_json = version_dir / f"{version}.json"
        version_jar = version_dir / f"{version}.jar"
        
        if not version_json.exists() or not version_jar.exists():
            print(f"Error: Version {version} not found!")
            print(f"Please download it first.")
            return False
        
        # Load version manifest
        try:
            with open(version_json, 'r') as f:
                version_data = json.load(f)
        except json.JSONDecodeError:
            print("Error: Corrupted version manifest!")
            return False
        
        # Validate main class (security check)
        main_class = version_data.get('mainClass')
        if not main_class or not self._is_safe_main_class(main_class):
            print(f"Error: Invalid or missing main class")
            return False
        
        # Extract natives
        print("Extracting native libraries...")
        natives_dir = self._extract_natives(version_data, version)
        
        # Build classpath
        print("Building classpath...")
        classpath = self._build_classpath(version_data, version_jar)
        
        if not classpath:
            print("Error: Failed to build classpath!")
            return False
        
        # Build game arguments (with Ely.by auth if provided)
        game_args = self._build_game_args(version_data, username, version, elyby_auth)
        
        # Build JVM arguments (with validation)
        jvm_args = self._build_jvm_args(version_data, natives_dir)
        
        # Construct launch command (all parameters are now validated)
        cmd = ['java'] + jvm_args + ['-cp', classpath, main_class] + game_args
        
        print("Starting Minecraft...")
        print(f"Working directory: {self.game_dir}")
        if elyby_auth:
            print(f"Using Ely.by account: {elyby_auth['username']}")
        
        # Log authlib-injector info for debugging
        if self.use_elyby and self.authlib_injector:
            authlib_args = [arg for arg in jvm_args if 'javaagent' in arg]
            if authlib_args:
                print(f"[authlib-injector] {authlib_args[0]}")
                print(f"[authlib-injector] Log file: {self.game_dir / 'authlib-injector.log'}")
        
        try:
            subprocess.run(cmd, cwd=self.game_dir)
            return True
        except Exception as e:
            print(f"Error launching Minecraft: {e}")
            return False
    
    def _is_safe_version_name(self, version):
        """Validate version name to prevent directory traversal"""
        # Allow alphanumeric, dots, hyphens, underscores
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', version):
            return False
        # Prevent directory traversal
        if '..' in version or '/' in version or '\\' in version:
            return False
        return True
    
    def _is_safe_username(self, username):
        """Validate username to prevent command injection"""
        import re
        # Minecraft usernames: 3-16 characters, alphanumeric and underscores
        if not re.match(r'^[a-zA-Z0-9_]{3,16}$', username):
            return False
        return True
    
    def _is_safe_main_class(self, main_class):
        """Validate main class name"""
        import re
        # Java class names: package.ClassName format
        if not re.match(r'^[a-zA-Z0-9._]+$', main_class):
            return False
        # Must be a Minecraft main class
        allowed_main_classes = [
            'net.minecraft.client.main.Main',
            'net.minecraft.client.Minecraft',
            'net.minecraft.launchwrapper.Launch'
        ]
        return main_class in allowed_main_classes
    
    def _build_classpath(self, version_data, version_jar):
        """Build the Java classpath from libraries"""
        classpath_parts = []
        
        # Add libraries (only from our libraries directory)
        for lib in version_data.get('libraries', []):
            if not self._should_use_library(lib):
                continue
            
            lib_path = self._get_library_path(lib)
            if lib_path and lib_path.exists():
                # Security: Verify path is within our libraries directory
                try:
                    lib_path.resolve().relative_to(self.libraries_dir.resolve())
                    classpath_parts.append(str(lib_path))
                except ValueError:
                    print(f"Warning: Library outside safe directory, skipping: {lib_path}")
            elif lib_path:
                print(f"Warning: Library not found: {lib_path}")
        
        # Add main jar (verify it's in our versions directory)
        try:
            version_jar.resolve().relative_to(self.versions_dir.resolve())
            classpath_parts.append(str(version_jar))
        except ValueError:
            print(f"Error: Version JAR outside safe directory!")
            return None
        
        print(f"Classpath contains {len(classpath_parts)} entries")
        
        # Use ; for Windows, : for Unix
        separator = ';' if os.name == 'nt' else ':'
        return separator.join(classpath_parts)
    
    def _should_use_library(self, lib):
        """Check if library should be used based on rules"""
        rules = lib.get('rules', [])
        if not rules:
            return True
        
        # Simple rule evaluation
        for rule in rules:
            action = rule.get('action')
            os_rule = rule.get('os', {})
            
            if os_rule:
                os_name = os_rule.get('name')
                if os_name == 'windows' and os.name != 'nt':
                    return action == 'disallow'
                elif os_name in ['linux', 'osx'] and os.name == 'nt':
                    return action == 'disallow'
        
        return True
    
    def _get_library_path(self, lib):
        """Get the file path for a library"""
        downloads = lib.get('downloads', {})
        artifact = downloads.get('artifact', {})
        path = artifact.get('path')
        
        if path:
            return self.libraries_dir / path
        return None
    
    def _build_game_args(self, version_data, username, version, elyby_auth=None):
        """Build game launch arguments"""
        args = []
        
        # Handle different argument formats
        if 'minecraftArguments' in version_data:
            # Old format (pre-1.13)
            arg_string = version_data['minecraftArguments']
            args = arg_string.split()
        elif 'arguments' in version_data:
            # New format (1.13+)
            game_args = version_data['arguments'].get('game', [])
            for arg in game_args:
                if isinstance(arg, str):
                    args.append(arg)
                elif isinstance(arg, dict):
                    # Conditional arguments - skip for now
                    pass
        
        # Use Ely.by credentials if available
        if elyby_auth:
            auth_username = elyby_auth['username']
            auth_uuid = elyby_auth['uuid']
            auth_token = elyby_auth['accessToken']
            user_type = 'ely'
        else:
            auth_username = username
            auth_uuid = '00000000-0000-0000-0000-000000000000'
            auth_token = 'null'
            user_type = 'legacy'
        
        # Replace argument variables
        replacements = {
            '${auth_player_name}': auth_username,
            '${version_name}': version,
            '${game_directory}': str(self.game_dir),
            '${assets_root}': str(self.assets_dir),
            '${assets_index_name}': version_data.get('assets', version),
            '${auth_uuid}': auth_uuid,
            '${auth_access_token}': auth_token,
            '${user_type}': user_type,
            '${version_type}': version_data.get('type', 'release'),
        }
        
        return [replacements.get(arg, arg) for arg in args]
    
    def _build_jvm_args(self, version_data, natives_dir):
        """Build JVM launch arguments"""
        args = ['-Xmx2G', '-Xms512M']  # Basic memory settings
        
        # Add authlib-injector for Ely.by (MUST be first)
        if self.use_elyby and self.authlib_injector:
            injector_args = self.authlib_injector.get_jvm_args()
            args = injector_args + args  # Put javaagent FIRST
        
        # Add natives directory
        args.append(f'-Djava.library.path={natives_dir}')
        
        return args
    
    def _extract_natives(self, version_data, version):
        """Extract native libraries for the current OS"""
        import zipfile
        
        natives_dir = self.versions_dir / version / f"{version}-natives"
        natives_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine OS name for natives
        os_name = None
        if os.name == 'nt':
            os_name = 'windows'
        elif sys.platform == 'darwin':
            os_name = 'osx'
        else:
            os_name = 'linux'
        
        # Extract natives from libraries
        for lib in version_data.get('libraries', []):
            if not self._should_use_library(lib):
                continue
            
            downloads = lib.get('downloads', {})
            classifiers = downloads.get('classifiers', {})
            
            # Look for natives for current OS
            native_key = None
            natives = lib.get('natives', {})
            if os_name in natives:
                native_key = natives[os_name].replace('${arch}', '64')
            
            if native_key and native_key in classifiers:
                native_artifact = classifiers[native_key]
                native_path = self.libraries_dir / native_artifact['path']
                
                if native_path.exists():
                    try:
                        with zipfile.ZipFile(native_path, 'r') as zip_ref:
                            # Extract only .dll, .so, .dylib files
                            for file in zip_ref.namelist():
                                if file.endswith(('.dll', '.so', '.dylib')) and not file.startswith('META-INF'):
                                    zip_ref.extract(file, natives_dir)
                    except Exception as e:
                        print(f"Warning: Failed to extract {native_path}: {e}")
        
        return natives_dir


def main():
    """Main entry point"""
    launcher = MinecraftLauncher()
    
    if len(sys.argv) < 2:
        print("Usage: python minecraft_launcher.py <version> [username]")
        print("Example: python minecraft_launcher.py 1.20.1 Steve")
        sys.exit(1)
    
    version = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "Player"
    
    # Check for Ely.by auth
    from elyby_auth import ElyByAuth
    elyby = ElyByAuth()
    elyby_auth = elyby.get_stored_auth()
    
    if elyby_auth:
        print(f"Using Ely.by account: {elyby_auth['username']}")
    
    launcher.launch(version, username, elyby_auth)


if __name__ == "__main__":
    main()
