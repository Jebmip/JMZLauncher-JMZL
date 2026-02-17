#!/usr/bin/env python3
"""
Ely.by Authentication and Skin System
Provides skin support for offline Minecraft
"""

import json
import requests
import uuid
from pathlib import Path

class ElyByAuth:
    """Handle Ely.by authentication and skins"""
    
    AUTH_SERVER = "https://authserver.ely.by/auth"
    API_BASE = "https://authserver.ely.by/api"
    SESSION_SERVER = "https://sessionserver.ely.by/session/minecraft"
    
    # Minecraft versions that support Ely.by authentication
    # Versions 1.7.2+ support the new authentication system
    SUPPORTED_VERSIONS = ["1.7", "1.8", "1.9", "1.10", "1.11", "1.12", "1.13", 
                          "1.14", "1.15", "1.16", "1.17", "1.18", "1.19", "1.20", "1.21"]
    
    def __init__(self, game_dir=None):
        """Initialize Ely.by auth"""
        if game_dir is None:
            self.game_dir = Path.home() / ".minecraft"
        else:
            self.game_dir = Path(game_dir)
        
        self.auth_file = self.game_dir / "elyby_auth.json"
    
    def is_version_supported(self, version):
        """Check if Minecraft version supports Ely.by auth"""
        # Extract major.minor version (e.g., "1.20.1" -> "1.20")
        parts = version.split('.')
        if len(parts) >= 2:
            major_minor = f"{parts[0]}.{parts[1]}"
            return major_minor in self.SUPPORTED_VERSIONS
        return False
    
    def login(self, username, password):
        """Login to Ely.by account"""
        print(f"Logging in to Ely.by as {username}...")
        
        payload = {
            "username": username,
            "password": password,
            "clientToken": str(uuid.uuid4()),
            "requestUser": True
        }
        
        try:
            response = requests.post(
                f"{self.AUTH_SERVER}/authenticate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Save auth data
            auth_data = {
                "accessToken": data["accessToken"],
                "clientToken": data["clientToken"],
                "username": data["selectedProfile"]["name"],
                "uuid": data["selectedProfile"]["id"]
            }
            
            with open(self.auth_file, 'w') as f:
                json.dump(auth_data, f, indent=2)
            
            print(f"✓ Logged in as {auth_data['username']}")
            return auth_data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print("✗ Invalid username or password")
            else:
                print(f"✗ Login failed: {e}")
            return None
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
    
    def validate_token(self):
        """Validate stored access token"""
        if not self.auth_file.exists():
            return False
        
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)
            
            payload = {
                "accessToken": auth_data["accessToken"],
                "clientToken": auth_data["clientToken"]
            }
            
            response = requests.post(
                f"{self.AUTH_SERVER}/validate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            return response.status_code == 204
            
        except Exception:
            return False
    
    def refresh_token(self):
        """Refresh access token"""
        if not self.auth_file.exists():
            return None
        
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)
            
            payload = {
                "accessToken": auth_data["accessToken"],
                "clientToken": auth_data["clientToken"],
                "requestUser": True
            }
            
            response = requests.post(
                f"{self.AUTH_SERVER}/refresh",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Update auth data
            auth_data["accessToken"] = data["accessToken"]
            
            with open(self.auth_file, 'w') as f:
                json.dump(auth_data, f, indent=2)
            
            return auth_data
            
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None
    
    def logout(self):
        """Logout and remove stored credentials"""
        if self.auth_file.exists():
            self.auth_file.unlink()
            print("✓ Logged out")
            return True
        return False
    
    def get_stored_auth(self):
        """Get stored authentication data"""
        if not self.auth_file.exists():
            return None
        
        try:
            with open(self.auth_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_profile(self, username):
        """Get profile information including skin"""
        try:
            response = requests.get(
                f"{self.API_BASE}/users/profiles/minecraft/{username}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def get_launch_args(self):
        """Get launch arguments for Ely.by skin system"""
        auth_data = self.get_stored_auth()
        
        if not auth_data:
            # Offline mode with Ely.by skin server
            return {
                "username": "Player",
                "uuid": "00000000-0000-0000-0000-000000000000",
                "accessToken": "null",
                "userType": "legacy",
                "skinDomain": "ely.by",
                "authServer": self.AUTH_SERVER,
                "sessionServer": self.SESSION_SERVER
            }
        
        # Validate or refresh token
        if not self.validate_token():
            auth_data = self.refresh_token()
            if not auth_data:
                # Token refresh failed, use offline
                return self.get_launch_args()
        
        return {
            "username": auth_data["username"],
            "uuid": auth_data["uuid"],
            "accessToken": auth_data["accessToken"],
            "userType": "ely",
            "skinDomain": "ely.by",
            "authServer": self.AUTH_SERVER,
            "sessionServer": self.SESSION_SERVER
        }
    
    def configure_jvm_args(self):
        """Get JVM arguments to enable Ely.by skins"""
        return [
            "-Dminecraft.api.auth.host=https://authserver.ely.by/auth",
            "-Dminecraft.api.account.host=https://authserver.ely.by/api",
            "-Dminecraft.api.session.host=https://sessionserver.ely.by/session",
            "-Dminecraft.api.services.host=https://api.ely.by/api",
            "-Dely.by.enable=true"
        ]


def main():
    """Test Ely.by authentication"""
    auth = ElyByAuth()
    
    print("Ely.by Authentication System")
    print("=" * 50)
    print()
    
    # Check if already logged in
    stored = auth.get_stored_auth()
    if stored:
        print(f"Already logged in as: {stored['username']}")
        print()
        choice = input("1. Use current account\n2. Login with different account\n3. Logout\nChoice: ")
        
        if choice == "1":
            if auth.validate_token():
                print("✓ Token is valid")
            else:
                print("Token expired, refreshing...")
                if auth.refresh_token():
                    print("✓ Token refreshed")
                else:
                    print("✗ Failed to refresh token")
        elif choice == "2":
            auth.logout()
            username = input("Ely.by username/email: ")
            password = input("Password: ")
            auth.login(username, password)
        elif choice == "3":
            auth.logout()
    else:
        print("Not logged in")
        print()
        choice = input("1. Login to Ely.by\n2. Use offline mode (with Ely.by skins)\nChoice: ")
        
        if choice == "1":
            username = input("Ely.by username/email: ")
            password = input("Password: ")
            auth.login(username, password)
    
    print()
    print("Launch arguments:")
    args = auth.get_launch_args()
    for key, value in args.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
