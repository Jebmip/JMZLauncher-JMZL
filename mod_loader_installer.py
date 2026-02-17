#!/usr/bin/env python3
"""
Mod Loader Installer
Installs Fabric, Forge, Quilt, and NeoForge loaders
"""

import json
import requests
from pathlib import Path

class ModLoaderInstaller:
    """Install mod loaders for Minecraft"""
    
    FABRIC_META = "https://meta.fabricmc.net/v2"
    QUILT_META = "https://meta.quiltmc.org/v3"
    
    def __init__(self, game_dir=None):
        """Initialize mod loader installer"""
        if game_dir is None:
            self.game_dir = Path.home() / ".minecraft"
        else:
            self.game_dir = Path(game_dir)
        
        self.versions_dir = self.game_dir / "versions"
        self.libraries_dir = self.game_dir / "libraries"
    
    def install_fabric(self, minecraft_version, loader_version=None):
        """Install Fabric loader"""
        print(f"Installing Fabric for Minecraft {minecraft_version}...")
        
        # Get latest loader version if not specified
        if not loader_version:
            loader_version = self._get_latest_fabric_loader()
            if not loader_version:
                print("Error: Could not get Fabric loader version")
                return False
        
        print(f"Using Fabric loader {loader_version}")
        
        # Get Fabric profile
        profile_url = f"{self.FABRIC_META}/versions/loader/{minecraft_version}/{loader_version}/profile/json"
        
        try:
            response = requests.get(profile_url, timeout=10)
            response.raise_for_status()
            profile_data = response.json()
            
            # Create version directory
            version_id = f"fabric-loader-{loader_version}-{minecraft_version}"
            version_dir = self.versions_dir / version_id
            version_dir.mkdir(parents=True, exist_ok=True)
            
            # Save profile JSON
            profile_path = version_dir / f"{version_id}.json"
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            print(f"✓ Fabric installed: {version_id}")
            return version_id
            
        except Exception as e:
            print(f"Error installing Fabric: {e}")
            return False
    
    def install_quilt(self, minecraft_version, loader_version=None):
        """Install Quilt loader"""
        print(f"Installing Quilt for Minecraft {minecraft_version}...")
        
        # Get latest loader version if not specified
        if not loader_version:
            loader_version = self._get_latest_quilt_loader()
            if not loader_version:
                print("Error: Could not get Quilt loader version")
                return False
        
        print(f"Using Quilt loader {loader_version}")
        
        # Get Quilt profile
        profile_url = f"{self.QUILT_META}/versions/loader/{minecraft_version}/{loader_version}/profile/json"
        
        try:
            response = requests.get(profile_url, timeout=10)
            response.raise_for_status()
            profile_data = response.json()
            
            # Create version directory
            version_id = f"quilt-loader-{loader_version}-{minecraft_version}"
            version_dir = self.versions_dir / version_id
            version_dir.mkdir(parents=True, exist_ok=True)
            
            # Save profile JSON
            profile_path = version_dir / f"{version_id}.json"
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            print(f"✓ Quilt installed: {version_id}")
            return version_id
            
        except Exception as e:
            print(f"Error installing Quilt: {e}")
            return False
    
    def _get_latest_fabric_loader(self):
        """Get the latest Fabric loader version"""
        try:
            response = requests.get(f"{self.FABRIC_META}/versions/loader", timeout=10)
            response.raise_for_status()
            loaders = response.json()
            if loaders:
                return loaders[0]['version']
        except Exception as e:
            print(f"Error getting Fabric loader: {e}")
        return None
    
    def _get_latest_quilt_loader(self):
        """Get the latest Quilt loader version"""
        try:
            response = requests.get(f"{self.QUILT_META}/versions/loader", timeout=10)
            response.raise_for_status()
            loaders = response.json()
            if loaders:
                return loaders[0]['version']
        except Exception as e:
            print(f"Error getting Quilt loader: {e}")
        return None
    
    def get_fabric_versions(self, minecraft_version):
        """Get available Fabric loader versions for a Minecraft version"""
        try:
            response = requests.get(
                f"{self.FABRIC_META}/versions/loader/{minecraft_version}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting Fabric versions: {e}")
            return []
    
    def get_quilt_versions(self, minecraft_version):
        """Get available Quilt loader versions for a Minecraft version"""
        try:
            response = requests.get(
                f"{self.QUILT_META}/versions/loader/{minecraft_version}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting Quilt versions: {e}")
            return []


def main():
    """Test mod loader installer"""
    installer = ModLoaderInstaller()
    
    print("Mod Loader Installer")
    print("=" * 50)
    print()
    
    mc_version = input("Enter Minecraft version (e.g., 1.20.1): ")
    
    print("\nSelect mod loader:")
    print("1. Fabric")
    print("2. Quilt")
    
    choice = input("Choice: ")
    
    if choice == "1":
        version_id = installer.install_fabric(mc_version)
        if version_id:
            print(f"\n✓ Fabric installed successfully!")
            print(f"Version ID: {version_id}")
    elif choice == "2":
        version_id = installer.install_quilt(mc_version)
        if version_id:
            print(f"\n✓ Quilt installed successfully!")
            print(f"Version ID: {version_id}")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
