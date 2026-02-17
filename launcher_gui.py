#!/usr/bin/env python3
"""
JMZLauncher GUI
Minecraft launcher with Ely.by authentication and modpack support
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
from pathlib import Path
from minecraft_downloader import MinecraftDownloader
from minecraft_launcher import MinecraftLauncher
from elyby_auth import ElyByAuth

class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JMZLauncher")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)  # Minimum size
        self.root.resizable(True, True)  # Allow resizing
        self.root.configure(bg="#1e1e1e")
        
        self.downloader = MinecraftDownloader()
        self.launcher = MinecraftLauncher(use_elyby=True)
        self.elyby = ElyByAuth()
        
        # Ensure directories exist on startup
        self.launcher.game_dir.mkdir(parents=True, exist_ok=True)
        self.launcher.versions_dir.mkdir(parents=True, exist_ok=True)
        self.launcher.libraries_dir.mkdir(parents=True, exist_ok=True)
        self.launcher.assets_dir.mkdir(parents=True, exist_ok=True)
        
        self.setup_ui()
        self.load_installed_versions()
        
        # Log startup info
        self.log(f"JMZLauncher initialized")
        self.log(f"Game directory: {self.launcher.game_dir}")
        self.log(f"Ely.by authentication: Required")
        self.log("")
        self.log("Need help? Read START_HERE.md or run: python diagnose_elyby.py")
        self.log("")
        
        # Check authlib-injector
        if hasattr(self.launcher, 'authlib_injector'):
            injector_info = self.launcher.authlib_injector.get_info()
            if injector_info['installed']:
                self.log(f"Authlib-injector: Ready ({injector_info['size_mb']} MB)")
            else:
                self.log("Authlib-injector: Downloading...")
        
        # Check if logged into Ely.by and update display
        self.update_account_display()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Header with gradient effect
        header_frame = tk.Frame(self.root, bg="#2d2d2d", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="⛏ JMZLAUNCHER", 
            font=("Segoe UI", 24, "bold"),
            bg="#2d2d2d",
            fg="#5cb85c"
        )
        title_label.pack(pady=20)
        
        # Main content with dark theme
        content_frame = tk.Frame(self.root, bg="#1e1e1e", padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Profile card
        profile_card = tk.Frame(content_frame, bg="#2d2d2d", relief=tk.FLAT, bd=0)
        profile_card.pack(fill=tk.X, pady=(0, 20))
        
        profile_inner = tk.Frame(profile_card, bg="#2d2d2d", padx=20, pady=15)
        profile_inner.pack(fill=tk.BOTH)
        
        # Username section with icon - now read-only display
        username_frame = tk.Frame(profile_inner, bg="#2d2d2d")
        username_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            username_frame, 
            text="👤 Account Status", 
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        ).pack(anchor=tk.W)
        
        # Display label instead of entry
        self.username_display = tk.Label(
            username_frame,
            text="Not logged in - Click 'Ely.by Login' to play",
            font=("Segoe UI", 11),
            bg="#3d3d3d",
            fg="#ff9800",
            relief=tk.FLAT,
            anchor=tk.W,
            padx=10,
            pady=8
        )
        self.username_display.pack(fill=tk.X, pady=(5, 0))
        
        # Version selection with icon
        version_frame = tk.Frame(profile_inner, bg="#2d2d2d")
        version_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            version_frame, 
            text="📦 Version", 
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        ).pack(anchor=tk.W)
        
        self.version_var = tk.StringVar()
        
        # Custom styled combobox
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Custom.TCombobox',
            fieldbackground="#3d3d3d",
            background="#3d3d3d",
            foreground="#ffffff",
            arrowcolor="#ffffff",
            borderwidth=0
        )
        
        self.version_combo = ttk.Combobox(
            version_frame, 
            textvariable=self.version_var,
            state="readonly",
            font=("Segoe UI", 11),
            style='Custom.TCombobox'
        )
        self.version_combo.pack(fill=tk.X, pady=(5, 0), ipady=6)
        
        # JVM Arguments section
        jvm_frame = tk.Frame(profile_inner, bg="#2d2d2d")
        jvm_frame.pack(fill=tk.X)
        
        tk.Label(
            jvm_frame, 
            text="⚙️ JVM Arguments", 
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        ).pack(anchor=tk.W)
        
        self.jvm_args_var = tk.StringVar(value="-Xmx2G -Xms512M")
        jvm_entry = tk.Entry(
            jvm_frame, 
            textvariable=self.jvm_args_var, 
            font=("Segoe UI", 10),
            bg="#3d3d3d",
            fg="#ffffff",
            relief=tk.FLAT,
            insertbackground="#ffffff",
            bd=0
        )
        jvm_entry.pack(fill=tk.X, pady=(5, 0), ipady=6)
        
        # Action buttons
        button_frame = tk.Frame(content_frame, bg="#1e1e1e")
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Play button - large and prominent
        self.play_button = tk.Button(
            button_frame,
            text="▶  PLAY",
            font=("Segoe UI", 14, "bold"),
            bg="#5cb85c",
            fg="white",
            activebackground="#4a9d4a",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            height=2,
            command=self.launch_game
        )
        self.play_button.pack(fill=tk.X, pady=(0, 10))
        
        # Secondary buttons row
        button_row = tk.Frame(button_frame, bg="#1e1e1e")
        button_row.pack(fill=tk.X)
        
        self.download_button = tk.Button(
            button_row,
            text="⬇ Download",
            font=("Segoe UI", 10),
            bg="#0275d8",
            fg="white",
            activebackground="#025aa5",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.open_download_window
        )
        self.download_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3), ipady=8)
        
        self.modpacks_button = tk.Button(
            button_row,
            text="📦 Modpacks",
            font=("Segoe UI", 10),
            bg="#9b59b6",
            fg="white",
            activebackground="#8e44ad",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.open_modpacks_window
        )
        self.modpacks_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 3), ipady=8)
        
        self.refresh_button = tk.Button(
            button_row,
            text="🔄 Refresh",
            font=("Segoe UI", 10),
            bg="#5a6268",
            fg="white",
            activebackground="#4a5258",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.load_installed_versions
        )
        self.refresh_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 0), ipady=8)
        
        # Second row of buttons
        button_row2 = tk.Frame(button_frame, bg="#1e1e1e")
        button_row2.pack(fill=tk.X, pady=(5, 0))
        
        self.elyby_button = tk.Button(
            button_row2,
            text="� Ely.by Login",
            font=("Segoe UI", 10),
            bg="#9b59b6",
            fg="white",
            activebackground="#8e44ad",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.open_elyby_login
        )
        self.elyby_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3), ipady=8)
        
        self.folder_button = tk.Button(
            button_row2,
            text="� Folder",
            font=("Segoe UI", 10),
            bg="#5a6268",
            fg="white",
            activebackground="#4a5258",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.open_minecraft_folder
        )
        self.folder_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 3), ipady=8)
        
        self.delete_button = tk.Button(
            button_row2,
            text="🗑 Delete",
            font=("Segoe UI", 10),
            bg="#d9534f",
            fg="white",
            activebackground="#c9302c",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.delete_version
        )
        self.delete_button.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 0), ipady=8)
        
        # Console section
        console_header = tk.Frame(content_frame, bg="#1e1e1e")
        console_header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            console_header,
            text="📋 Console",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(side=tk.LEFT)
        
        clear_btn = tk.Button(
            console_header,
            text="Clear",
            font=("Segoe UI", 8),
            bg="#3d3d3d",
            fg="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_console
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Console with better styling
        console_frame = tk.Frame(content_frame, bg="#0d0d0d", relief=tk.FLAT)
        console_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console = scrolledtext.ScrolledText(
            console_frame,
            height=12,
            font=("Consolas", 9),
            bg="#0d0d0d",
            fg="#00ff41",
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            insertbackground="#00ff41"
        )
        self.console.pack(fill=tk.BOTH, expand=True)
    
    def clear_console(self):
        """Clear console output"""
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.config(state=tk.DISABLED)
    
    def update_account_display(self):
        """Update the account status display"""
        elyby_auth = self.elyby.get_stored_auth()
        
        if elyby_auth:
            # Validate token
            if self.elyby.validate_token():
                self.username_display.config(
                    text=f"✓ Logged in as: {elyby_auth['username']}",
                    fg="#5cb85c"
                )
                self.log(f"Ely.by account: {elyby_auth['username']}")
                self.play_button.config(state=tk.NORMAL)
            else:
                # Try to refresh
                self.log("Ely.by token expired, refreshing...")
                refreshed = self.elyby.refresh_token()
                if refreshed:
                    self.username_display.config(
                        text=f"✓ Logged in as: {refreshed['username']}",
                        fg="#5cb85c"
                    )
                    self.log(f"Token refreshed for: {refreshed['username']}")
                    self.play_button.config(state=tk.NORMAL)
                else:
                    self.username_display.config(
                        text="⚠ Session expired - Please login again",
                        fg="#ff9800"
                    )
                    self.log("Failed to refresh token, please login again")
                    self.play_button.config(state=tk.DISABLED)
        else:
            self.username_display.config(
                text="Not logged in - Click 'Ely.by Login' to play",
                fg="#ff9800"
            )
            self.log("No Ely.by account - Login required to play")
            self.play_button.config(state=tk.DISABLED)
    
    def open_minecraft_folder(self):
        """Open Minecraft folder in file explorer"""
        minecraft_dir = self.launcher.game_dir
        
        # Ensure folder exists
        minecraft_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(minecraft_dir))
            elif os.name == 'posix':  # macOS/Linux
                import subprocess
                import sys
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(minecraft_dir)])
            self.log(f"Opened folder: {minecraft_dir}")
        except Exception as e:
            self.log(f"Error opening folder: {e}")
            messagebox.showerror("Error", f"Could not open folder:\n{minecraft_dir}\n\nError: {e}")
    
    def open_modpacks_window(self):
        """Open Modrinth modpacks window"""
        from modpacks_gui import ModpacksWindow
        ModpacksWindow(self.root)
    
    def open_elyby_login(self):
        """Open Ely.by login dialog"""
        from elyby_login_gui import ElyByLoginDialog
        
        def on_auth_change(auth_data):
            self.update_account_display()
        
        ElyByLoginDialog(self.root, callback=on_auth_change)
    
    def delete_version(self):
        """Delete selected version"""
        version = self.version_var.get()
        
        if not version:
            messagebox.showwarning("Warning", "Please select a version to delete!")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete Minecraft {version}?\n\nThis will remove all files for this version."
        )
        
        if not confirm:
            return
        
        try:
            import shutil
            version_dir = self.launcher.versions_dir / version
            
            if version_dir.exists():
                shutil.rmtree(version_dir)
                self.log(f"Deleted version {version}")
                messagebox.showinfo("Success", f"Version {version} has been deleted.")
                self.load_installed_versions()
            else:
                messagebox.showerror("Error", f"Version {version} not found!")
        except Exception as e:
            self.log(f"Error deleting version: {e}")
            messagebox.showerror("Error", f"Failed to delete version:\n{e}")
    
    def log(self, message):
        """Log message to console"""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
    
    def load_installed_versions(self):
        """Load installed versions from disk"""
        self.log("Loading installed versions...")
        versions = []
        
        if self.launcher.versions_dir.exists():
            for version_dir in self.launcher.versions_dir.iterdir():
                if version_dir.is_dir():
                    version_json = version_dir / f"{version_dir.name}.json"
                    if version_json.exists():
                        versions.append(version_dir.name)
        
        versions.sort(reverse=True)
        self.version_combo['values'] = versions
        
        if versions:
            self.version_combo.current(0)
            self.log(f"Found {len(versions)} installed version(s)")
        else:
            self.log("No versions installed. Click 'Download Version' to get started.")
    
    def launch_game(self):
        """Launch Minecraft"""
        version = self.version_var.get()
        
        if not version:
            messagebox.showerror("Error", "Please select a version!")
            return
        
        # Get Ely.by auth - now mandatory
        elyby_auth = self.elyby.get_stored_auth()
        
        if not elyby_auth:
            messagebox.showerror(
                "Login Required",
                "You must login with Ely.by to play Minecraft.\n\n"
                "Click the '🔐 Ely.by Login' button to get started."
            )
            return
        
        # Validate token
        if not self.elyby.validate_token():
            self.log("Ely.by token expired, refreshing...")
            elyby_auth = self.elyby.refresh_token()
            if not elyby_auth:
                messagebox.showerror(
                    "Session Expired",
                    "Your Ely.by session has expired.\n\n"
                    "Please login again."
                )
                self.update_account_display()
                return
        
        username = elyby_auth['username']
        
        # Check Ely.by version compatibility
        if not self.elyby.is_version_supported(version):
            response = messagebox.askyesno(
                "Version Warning",
                f"Minecraft {version} may not fully support Ely.by skins.\n\n"
                f"Ely.by works best with Minecraft 1.7.2 and newer.\n\n"
                f"Continue anyway?"
            )
            if not response:
                return
        
        self.log(f"Launching Minecraft {version} as {username}...")
        self.log(f"Using Ely.by account: {username}")
        
        self.play_button.config(state=tk.DISABLED, text="⏳ LAUNCHING...", bg="#4a9d4a")
        
        def launch_thread():
            try:
                success = self.launcher.launch(version, username, elyby_auth)
                if success:
                    self.log("Game closed.")
                else:
                    self.log("Failed to launch game.")
            except Exception as e:
                self.log(f"Error: {e}")
            finally:
                self.play_button.config(state=tk.NORMAL, text="▶  PLAY", bg="#5cb85c")
        
        threading.Thread(target=launch_thread, daemon=True).start()
    
    def open_download_window(self):
        """Open download window"""
        download_window = tk.Toplevel(self.root)
        download_window.title("Download Minecraft")
        download_window.geometry("550x500")
        download_window.resizable(False, False)
        download_window.configure(bg="#1e1e1e")
        
        # Header
        header_frame = tk.Frame(download_window, bg="#2d2d2d", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="⬇ Download Minecraft Version",
            font=("Segoe UI", 16, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        )
        title_label.pack(pady=15)
        
        # Content
        content_frame = tk.Frame(download_window, bg="#1e1e1e", padx=25, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info label
        info_label = tk.Label(
            content_frame,
            text="Select a version to download:",
            font=("Segoe UI", 10),
            bg="#1e1e1e",
            fg="#ffffff"
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Listbox with custom styling
        listbox_frame = tk.Frame(content_frame, bg="#2d2d2d", relief=tk.FLAT)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        scrollbar = tk.Scrollbar(listbox_frame, bg="#2d2d2d")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        version_listbox = tk.Listbox(
            listbox_frame,
            font=("Segoe UI", 10),
            bg="#2d2d2d",
            fg="#ffffff",
            selectbackground="#0275d8",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set,
            activestyle='none'
        )
        version_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.config(command=version_listbox.yview)
        
        # Progress label
        progress_label = tk.Label(
            content_frame,
            text="",
            font=("Segoe UI", 9),
            bg="#1e1e1e",
            fg="#5cb85c"
        )
        progress_label.pack(pady=(0, 15))
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg="#1e1e1e")
        button_frame.pack(fill=tk.X)
        
        download_btn = tk.Button(
            button_frame,
            text="⬇ Download Selected",
            font=("Segoe UI", 11, "bold"),
            bg="#5cb85c",
            fg="white",
            activebackground="#4a9d4a",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        download_btn.pack(fill=tk.X, pady=(0, 8), ipady=10)
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Segoe UI", 10),
            bg="#5a6268",
            fg="white",
            activebackground="#4a5258",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=download_window.destroy
        )
        close_btn.pack(fill=tk.X, ipady=8)
        
        # Load versions
        def load_versions():
            progress_label.config(text="⏳ Loading versions...", fg="#ffffff")
            download_btn.config(state=tk.DISABLED)
            
            def fetch_thread():
                try:
                    import requests
                    response = requests.get(MinecraftDownloader.VERSION_MANIFEST_URL)
                    manifest = response.json()
                    
                    releases = [v for v in manifest['versions'] if v['type'] == 'release']
                    
                    for version in releases[:30]:  # Show first 30 releases
                        version_listbox.insert(tk.END, version['id'])
                    
                    progress_label.config(text=f"✓ Loaded {len(releases[:30])} versions", fg="#5cb85c")
                    download_btn.config(state=tk.NORMAL)
                except Exception as e:
                    progress_label.config(text=f"✗ Error: {e}", fg="#d9534f")
            
            threading.Thread(target=fetch_thread, daemon=True).start()
        
        # Download selected version
        def download_selected():
            selection = version_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a version first!")
                return
            
            version = version_listbox.get(selection[0])
            progress_label.config(text=f"⏳ Downloading {version}...", fg="#ffffff")
            download_btn.config(state=tk.DISABLED)
            close_btn.config(state=tk.DISABLED)
            
            def download_thread():
                try:
                    self.log(f"Starting download of {version}...")
                    success = self.downloader.download_version(version)
                    
                    if success:
                        progress_label.config(text=f"✓ {version} downloaded successfully!", fg="#5cb85c")
                        self.log(f"Successfully downloaded {version}")
                        self.load_installed_versions()
                        messagebox.showinfo("Success", f"Minecraft {version} is ready to play!")
                    else:
                        progress_label.config(text="✗ Download failed!", fg="#d9534f")
                        self.log(f"Failed to download {version}")
                except Exception as e:
                    progress_label.config(text=f"✗ Error: {e}", fg="#d9534f")
                    self.log(f"Error downloading: {e}")
                finally:
                    download_btn.config(state=tk.NORMAL)
                    close_btn.config(state=tk.NORMAL)
            
            threading.Thread(target=download_thread, daemon=True).start()
        
        download_btn.config(command=download_selected)
        load_versions()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = LauncherGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
