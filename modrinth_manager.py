#!/usr/bin/env python3
"""
Modrinth Modpack Manager
Handles downloading and installing modpacks from Modrinth
"""

import json
import os
import requests
import zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

class ModrinthManager:
    """Manage Modrinth modpacks"""
    
    API_BASE = "https://api.modrinth.com/v2"
    USER_AGENT = "JMZLauncher/1.0"
    
    def __init__(self, game_dir=None):
        """Initialize Modrinth manager"""
        if game_dir is None:
            self.game_dir = Path.home() / ".minecraft"
        else:
            self.game_dir = Path(game_dir)
        
        self.modpacks_dir = self.game_dir / "modpacks"
        self.modpacks_dir.mkdir(parents=True, exist_ok=True)
    
    def search_modpacks(self, query, limit=20):
        """Search for modpacks on Modrinth"""
        url = f"{self.API_BASE}/search"
        params = {
            'query': query,
            'limit': limit,
            'facets': '[["project_type:modpack"]]'
        }
        headers = {'User-Agent': self.USER_AGENT}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('hits', [])
        except Exception as e:
            print(f"Error searching modpacks: {e}")
            return []
    
    def get_modpack_versions(self, project_id):
        """Get available versions for a modpack"""
        url = f"{self.API_BASE}/project/{project_id}/version"
        headers = {'User-Agent': self.USER_AGENT}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting modpack versions: {e}")
            return []
    
    def download_modpack(self, version_data, modpack_name):
        """Download and install a modpack"""
        print(f"Downloading modpack: {modpack_name}")
        
        # Find the primary file (usually .mrpack)
        files = version_data.get('files', [])
        primary_file = None
        for file in files:
            if file.get('primary') or file['filename'].endswith('.mrpack'):
                primary_file = file
                break
        
        if not primary_file:
            print("Error: No modpack file found!")
            return False
        
        # Download the .mrpack file
        download_url = primary_file['url']
        mrpack_path = self.modpacks_dir / f"{modpack_name}.mrpack"
        
        print(f"Downloading from {download_url}...")
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(mrpack_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded to {mrpack_path}")
        except Exception as e:
            print(f"Error downloading modpack: {e}")
            return False
        
        # Extract and install the modpack
        return self._install_modpack(mrpack_path, modpack_name)
    
    def _install_modpack(self, mrpack_path, modpack_name):
        """Extract and install a .mrpack file"""
        print(f"Installing modpack: {modpack_name}")
        
        # Create instance directory
        instance_dir = self.game_dir / "instances" / modpack_name
        instance_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(mrpack_path, 'r') as zip_ref:
                # Extract modrinth.index.json
                index_data = json.loads(zip_ref.read('modrinth.index.json'))
                
                # Get game version and mod loader
                game_version = index_data.get('dependencies', {}).get('minecraft')
                fabric_version = index_data.get('dependencies', {}).get('fabric-loader')
                forge_version = index_data.get('dependencies', {}).get('forge')
                quilt_version = index_data.get('dependencies', {}).get('quilt-loader')
                
                print(f"Minecraft version: {game_version}")
                if fabric_version:
                    print(f"Fabric loader: {fabric_version}")
                elif forge_version:
                    print(f"Forge version: {forge_version}")
                elif quilt_version:
                    print(f"Quilt loader: {quilt_version}")
                
                # Extract overrides (configs, resource packs, etc.)
                print("Extracting overrides...")
                for file in zip_ref.namelist():
                    if file.startswith('overrides/'):
                        target_path = instance_dir / file.replace('overrides/', '')
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(target_path, 'wb') as f:
                            f.write(zip_ref.read(file))
                
                # Download mods
                print("Downloading mods...")
                mods_dir = instance_dir / "mods"
                mods_dir.mkdir(exist_ok=True)
                
                files = index_data.get('files', [])
                self._download_mods(files, mods_dir)
                
                # Save instance info
                instance_info = {
                    'name': modpack_name,
                    'gameVersion': game_version,
                    'fabricLoader': fabric_version,
                    'forgeVersion': forge_version,
                    'quiltLoader': quilt_version,
                    'instanceDir': str(instance_dir)
                }
                
                with open(instance_dir / 'instance.json', 'w') as f:
                    json.dump(instance_info, f, indent=2)
                
                print(f"✓ Modpack installed successfully!")
                print(f"Instance directory: {instance_dir}")
                return True
                
        except Exception as e:
            print(f"Error installing modpack: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _download_mods(self, files, mods_dir):
        """Download all mods from modpack"""
        total = len(files)
        print(f"Downloading {total} mods...")
        
        def download_mod(file_info):
            url = file_info['downloads'][0]  # Primary download URL
            filename = file_info['path'].split('/')[-1]
            file_path = mods_dir / filename
            
            if file_path.exists():
                return True  # Skip if exists
            
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
            except Exception as e:
                print(f"  Failed to download {filename}: {e}")
                return False
        
        completed = 0
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(download_mod, file): file for file in files}
            
            for future in as_completed(futures):
                completed += 1
                if completed % 10 == 0 or completed == total:
                    print(f"  Progress: {completed}/{total}")
    
    def list_installed_modpacks(self):
        """List all installed modpacks"""
        instances_dir = self.game_dir / "instances"
        if not instances_dir.exists():
            return []
        
        modpacks = []
        for instance_dir in instances_dir.iterdir():
            if instance_dir.is_dir():
                instance_json = instance_dir / 'instance.json'
                if instance_json.exists():
                    with open(instance_json, 'r') as f:
                        modpacks.append(json.load(f))
        
        return modpacks


def main():
    """Test the Modrinth manager"""
    manager = ModrinthManager()
    
    print("Modrinth Modpack Manager")
    print("=" * 50)
    print()
    
    # Search for modpacks
    query = input("Search for modpacks: ")
    results = manager.search_modpacks(query, limit=10)
    
    if not results:
        print("No modpacks found!")
        return
    
    print(f"\nFound {len(results)} modpacks:")
    for i, pack in enumerate(results, 1):
        print(f"{i}. {pack['title']} by {pack['author']}")
        print(f"   Downloads: {pack['downloads']:,}")
        print(f"   {pack['description'][:100]}...")
        print()
    
    # Select a modpack
    choice = int(input("Select a modpack (number): ")) - 1
    selected = results[choice]
    
    print(f"\nGetting versions for {selected['title']}...")
    versions = manager.get_modpack_versions(selected['project_id'])
    
    if not versions:
        print("No versions found!")
        return
    
    print(f"\nAvailable versions:")
    for i, ver in enumerate(versions[:5], 1):
        print(f"{i}. {ver['name']} - MC {', '.join(ver['game_versions'])}")
    
    ver_choice = int(input("Select version (number): ")) - 1
    selected_version = versions[ver_choice]
    
    # Download and install
    manager.download_modpack(selected_version, selected['slug'])


if __name__ == "__main__":
    main()
