#!/usr/bin/env python3
"""
Minecraft Version Downloader
Downloads Minecraft versions, libraries, and assets
"""

import json
import os
import hashlib
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

class MinecraftDownloader:
    VERSION_MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
    
    def __init__(self, game_dir=None):
        """Initialize downloader with game directory"""
        if game_dir is None:
            self.game_dir = Path.home() / ".minecraft"
        else:
            self.game_dir = Path(game_dir)
        
        self.versions_dir = self.game_dir / "versions"
        self.libraries_dir = self.game_dir / "libraries"
        self.assets_dir = self.game_dir / "assets"
        
        # Create directories
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.libraries_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
    
    def list_versions(self):
        """List available Minecraft versions"""
        print("Fetching version list...")
        response = requests.get(self.VERSION_MANIFEST_URL)
        manifest = response.json()
        
        print("\nAvailable versions:")
        print("-" * 50)
        
        releases = [v for v in manifest['versions'] if v['type'] == 'release']
        print(f"\nReleases (showing first 10):")
        for version in releases[:10]:
            print(f"  {version['id']}")
        
        return manifest['versions']
    
    def download_version(self, version_id):
        """Download a specific Minecraft version"""
        print(f"\nDownloading Minecraft {version_id}...")
        
        # Get version manifest
        response = requests.get(self.VERSION_MANIFEST_URL)
        manifest = response.json()
        
        # Find version
        version_info = None
        for v in manifest['versions']:
            if v['id'] == version_id:
                version_info = v
                break
        
        if not version_info:
            print(f"Error: Version {version_id} not found!")
            return False
        
        # Download version JSON
        print(f"Downloading version manifest...")
        version_url = version_info['url']
        response = requests.get(version_url)
        version_data = response.json()
        
        # Save version JSON
        version_dir = self.versions_dir / version_id
        version_dir.mkdir(parents=True, exist_ok=True)
        
        version_json_path = version_dir / f"{version_id}.json"
        with open(version_json_path, 'w') as f:
            json.dump(version_data, f, indent=2)
        
        # Download client JAR
        print(f"Downloading client JAR...")
        client_info = version_data['downloads']['client']
        client_url = client_info['url']
        client_sha1 = client_info['sha1']
        client_jar_path = version_dir / f"{version_id}.jar"
        
        if not self._download_file(client_url, client_jar_path, client_sha1):
            print("Error: Failed to download or verify client JAR!")
            return False
        
        # Download libraries
        print(f"Downloading libraries...")
        self._download_libraries(version_data)
        
        # Download assets
        print(f"Downloading assets...")
        self._download_assets(version_data)
        
        print(f"\n✓ Successfully downloaded Minecraft {version_id}!")
        return True
    
    def _download_libraries(self, version_data):
        """Download all required libraries with hash verification"""
        libraries = version_data.get('libraries', [])
        
        downloads = []
        for lib in libraries:
            artifact = lib.get('downloads', {}).get('artifact')
            if artifact:
                url = artifact['url']
                path = self.libraries_dir / artifact['path']
                sha1 = artifact.get('sha1')
                if sha1:
                    downloads.append((url, path, sha1))
                else:
                    downloads.append((url, path))
        
        print(f"  Downloading {len(downloads)} libraries...")
        self._download_files_parallel(downloads)
    
    def _download_assets(self, version_data):
        """Download game assets with hash verification"""
        asset_index = version_data.get('assetIndex')
        if not asset_index:
            return
        
        # Download asset index
        asset_index_url = asset_index['url']
        asset_index_sha1 = asset_index.get('sha1')
        asset_index_path = self.assets_dir / "indexes" / f"{asset_index['id']}.json"
        asset_index_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self._download_file(asset_index_url, asset_index_path, asset_index_sha1):
            print("Warning: Failed to download or verify asset index")
            return
        
        # Load asset index
        with open(asset_index_path, 'r') as f:
            asset_data = json.load(f)
        
        # Download assets
        objects = asset_data.get('objects', {})
        downloads = []
        
        for asset_name, asset_info in objects.items():
            hash_code = asset_info['hash']
            hash_prefix = hash_code[:2]
            url = f"https://resources.download.minecraft.net/{hash_prefix}/{hash_code}"
            path = self.assets_dir / "objects" / hash_prefix / hash_code
            downloads.append((url, path, hash_code))  # Hash is the filename
        
        print(f"  Downloading {len(downloads)} assets...")
        self._download_files_parallel(downloads, max_workers=20)
    
    def _download_file(self, url, path, expected_sha1=None):
        """Download a single file with SHA1 verification"""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Skip if file exists and hash matches
        if path.exists() and expected_sha1:
            if self._verify_sha1(path, expected_sha1):
                return True  # File already exists and is valid
            else:
                print(f"  Hash mismatch for {path.name}, re-downloading...")
                path.unlink()  # Delete corrupted file
        elif path.exists():
            return True  # Skip if already exists (no hash to verify)
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Download to temporary file first
            temp_path = path.with_suffix(path.suffix + '.tmp')
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify hash if provided
            if expected_sha1:
                if not self._verify_sha1(temp_path, expected_sha1):
                    temp_path.unlink()
                    print(f"  ✗ Hash verification failed for {path.name}")
                    return False
            
            # Move temp file to final location
            temp_path.replace(path)
            return True
            
        except Exception as e:
            print(f"  ✗ Error downloading {path.name}: {e}")
            if temp_path.exists():
                temp_path.unlink()
            return False
    
    def _verify_sha1(self, file_path, expected_sha1):
        """Verify SHA1 hash of a file"""
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest().lower() == expected_sha1.lower()
    
    def _download_files_parallel(self, downloads, max_workers=10):
        """Download multiple files in parallel with hash verification"""
        completed = 0
        failed = 0
        total = len(downloads)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for item in downloads:
                if len(item) == 3:
                    url, path, sha1 = item
                    futures[executor.submit(self._download_file, url, path, sha1)] = (url, path)
                else:
                    url, path = item
                    futures[executor.submit(self._download_file, url, path)] = (url, path)
            
            for future in as_completed(futures):
                completed += 1
                if not future.result():
                    failed += 1
                if completed % 50 == 0 or completed == total:
                    status = f"Progress: {completed}/{total}"
                    if failed > 0:
                        status += f" ({failed} failed)"
                    print(f"    {status}")


def main():
    """Main entry point"""
    import sys
    
    downloader = MinecraftDownloader()
    
    if len(sys.argv) < 2:
        print("Minecraft Downloader")
        print("\nUsage:")
        print("  python minecraft_downloader.py list")
        print("  python minecraft_downloader.py download <version>")
        print("\nExample:")
        print("  python minecraft_downloader.py download 1.20.1")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        downloader.list_versions()
    elif command == "download" and len(sys.argv) > 2:
        version = sys.argv[2]
        downloader.download_version(version)
    else:
        print("Invalid command!")
        sys.exit(1)


if __name__ == "__main__":
    main()
