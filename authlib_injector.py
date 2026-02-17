#!/usr/bin/env python3
"""
Authlib-Injector Manager
Downloads and manages authlib-injector for Ely.by authentication
"""

import requests
import json
from pathlib import Path

class AuthlibInjector:
    """Manage authlib-injector for custom authentication"""
    
    INJECTOR_URL = "https://authlib-injector.yushi.moe/artifact/latest.json"
    ELYBY_API = "https://authserver.ely.by/api/authlib-injector"
    
    def __init__(self, game_dir=None):
        """Initialize authlib-injector manager"""
        if game_dir is None:
            self.game_dir = Path.home() / ".minecraft"
        else:
            self.game_dir = Path(game_dir)
        
        self.injector_dir = self.game_dir / "authlib-injector"
        self.injector_dir.mkdir(parents=True, exist_ok=True)
        self.injector_jar = self.injector_dir / "authlib-injector.jar"
    
    def download_injector(self):
        """Download the latest authlib-injector"""
        print("Downloading authlib-injector...")
        
        try:
            # Get latest version info
            response = requests.get(self.INJECTOR_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            download_url = data['download_url']
            version = data['version']
            
            print(f"Downloading version {version}...")
            
            # Download the JAR with proper headers
            response = requests.get(
                download_url, 
                timeout=30,
                headers={"User-Agent": "JMZLauncher/1.0"}
            )
            response.raise_for_status()
            
            # Verify we got a JAR file
            if len(response.content) < 1000:
                raise Exception("Downloaded file too small, might be corrupted")
            
            with open(self.injector_jar, 'wb') as f:
                f.write(response.content)
            
            size_mb = len(response.content) / (1024 * 1024)
            print(f"✓ Downloaded authlib-injector {version} ({size_mb:.2f} MB)")
            return True
            
        except Exception as e:
            print(f"Error downloading authlib-injector: {e}")
            return False
    
    def ensure_injector(self):
        """Ensure authlib-injector is downloaded"""
        if not self.injector_jar.exists():
            print("authlib-injector not found, downloading...")
            return self.download_injector()
        return True
    
    def get_jvm_args(self):
        """Get JVM arguments for authlib-injector with Ely.by"""
        if not self.ensure_injector():
            print("Warning: Could not get authlib-injector")
            return []
        
        # Return javaagent argument pointing to Ely.by
        # The URL should point to the metadata endpoint
        # Use proper escaping for Windows paths
        injector_path = str(self.injector_jar).replace('\\', '/')
        return [
            f"-javaagent:{injector_path}=https://authserver.ely.by/api/authlib-injector"
        ]
    
    def get_info(self):
        """Get authlib-injector info"""
        if self.injector_jar.exists():
            size_mb = self.injector_jar.stat().st_size / (1024 * 1024)
            return {
                'installed': True,
                'path': str(self.injector_jar),
                'size_mb': round(size_mb, 2)
            }
        return {'installed': False}


def main():
    """Test authlib-injector"""
    injector = AuthlibInjector()
    
    print("Authlib-Injector Manager")
    print("=" * 50)
    print()
    
    info = injector.get_info()
    if info['installed']:
        print(f"✓ Authlib-injector installed")
        print(f"  Path: {info['path']}")
        print(f"  Size: {info['size_mb']} MB")
    else:
        print("✗ Authlib-injector not installed")
        print()
        choice = input("Download now? (y/n): ")
        if choice.lower() == 'y':
            injector.download_injector()
    
    print()
    print("JVM Arguments:")
    args = injector.get_jvm_args()
    for arg in args:
        print(f"  {arg}")


if __name__ == "__main__":
    main()
