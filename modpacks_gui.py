#!/usr/bin/env python3
"""
Modrinth Modpacks GUI
Browse, download, and install modpacks from Modrinth
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from modrinth_manager import ModrinthManager
from mod_loader_installer import ModLoaderInstaller

class ModpacksWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Modrinth Modpacks")
        self.window.geometry("800x600")
        self.window.minsize(700, 500)  # Minimum size
        self.window.resizable(True, True)  # Allow resizing
        self.window.configure(bg="#1e1e1e")
        
        self.modrinth = ModrinthManager()
        self.mod_loader = ModLoaderInstaller()
        
        self.selected_modpack = None
        self.selected_version = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the modpacks UI"""
        # Header
        header_frame = tk.Frame(self.window, bg="#2d2d2d", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="📦 Modrinth Modpacks",
            font=("Segoe UI", 16, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        )
        title_label.pack(pady=15)
        
        # Main content
        content_frame = tk.Frame(self.window, bg="#1e1e1e", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search section
        search_frame = tk.Frame(content_frame, bg="#1e1e1e")
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            search_frame,
            text="🔍 Search Modpacks:",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            bg="#3d3d3d",
            fg="#ffffff",
            relief=tk.FLAT,
            insertbackground="#ffffff"
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.search_modpacks())
        
        search_btn = tk.Button(
            search_frame,
            text="Search",
            font=("Segoe UI", 10),
            bg="#0275d8",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.search_modpacks
        )
        search_btn.pack(side=tk.LEFT, ipady=6, ipadx=15)
        
        # Results section
        results_label = tk.Label(
            content_frame,
            text="Search Results:",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        )
        results_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Listbox for modpacks
        listbox_frame = tk.Frame(content_frame, bg="#2d2d2d")
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.modpacks_listbox = tk.Listbox(
            listbox_frame,
            font=("Segoe UI", 9),
            bg="#2d2d2d",
            fg="#ffffff",
            selectbackground="#0275d8",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set,
            activestyle='none'
        )
        self.modpacks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.modpacks_listbox.bind('<<ListboxSelect>>', self.on_modpack_select)
        scrollbar.config(command=self.modpacks_listbox.yview)
        
        # Modpack info and version selection
        info_frame = tk.Frame(content_frame, bg="#2d2d2d", relief=tk.FLAT)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        info_inner = tk.Frame(info_frame, bg="#2d2d2d", padx=15, pady=15)
        info_inner.pack(fill=tk.BOTH)
        
        # Modpack info
        self.info_label = tk.Label(
            info_inner,
            text="Select a modpack to see details",
            font=("Segoe UI", 9),
            bg="#2d2d2d",
            fg="#ffffff",
            justify=tk.LEFT,
            wraplength=700
        )
        self.info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Version selection
        version_frame = tk.Frame(info_inner, bg="#2d2d2d")
        version_frame.pack(fill=tk.X)
        
        tk.Label(
            version_frame,
            text="Version:",
            font=("Segoe UI", 10, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.version_var = tk.StringVar()
        self.version_combo = ttk.Combobox(
            version_frame,
            textvariable=self.version_var,
            state="readonly",
            font=("Segoe UI", 9),
            width=40
        )
        self.version_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.version_combo.bind('<<ComboboxSelected>>', self.on_version_select)
        
        # Install button
        self.install_btn = tk.Button(
            content_frame,
            text="⬇ Install Modpack",
            font=("Segoe UI", 11, "bold"),
            bg="#5cb85c",
            fg="white",
            activebackground="#4a9d4a",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
            command=self.install_modpack
        )
        self.install_btn.pack(fill=tk.X, ipady=10)
        
        # Status label
        self.status_label = tk.Label(
            content_frame,
            text="",
            font=("Segoe UI", 9),
            bg="#1e1e1e",
            fg="#5cb85c"
        )
        self.status_label.pack(pady=(10, 0))
    
    def search_modpacks(self):
        """Search for modpacks"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term!")
            return
        
        self.status_label.config(text="⏳ Searching...", fg="#ffffff")
        self.modpacks_listbox.delete(0, tk.END)
        self.install_btn.config(state=tk.DISABLED)
        
        def search_thread():
            try:
                results = self.modrinth.search_modpacks(query, limit=50)
                
                if not results:
                    self.status_label.config(text="No modpacks found", fg="#d9534f")
                    return
                
                self.modpack_results = results
                
                for pack in results:
                    display_text = f"{pack['title']} - {pack['downloads']:,} downloads"
                    self.modpacks_listbox.insert(tk.END, display_text)
                
                self.status_label.config(text=f"✓ Found {len(results)} modpacks", fg="#5cb85c")
                
            except Exception as e:
                self.status_label.config(text=f"Error: {e}", fg="#d9534f")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def on_modpack_select(self, event):
        """Handle modpack selection"""
        selection = self.modpacks_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        self.selected_modpack = self.modpack_results[index]
        
        # Update info
        pack = self.selected_modpack
        info_text = f"{pack['title']} by {pack['author']}\n"
        info_text += f"Downloads: {pack['downloads']:,} | "
        info_text += f"Follows: {pack.get('follows', 0):,}\n"
        info_text += f"{pack['description']}"
        self.info_label.config(text=info_text)
        
        # Load versions
        self.status_label.config(text="⏳ Loading versions...", fg="#ffffff")
        self.version_combo['values'] = []
        self.install_btn.config(state=tk.DISABLED)
        
        def load_versions_thread():
            try:
                versions = self.modrinth.get_modpack_versions(pack['project_id'])
                
                if not versions:
                    self.status_label.config(text="No versions found", fg="#d9534f")
                    return
                
                self.modpack_versions = versions
                
                version_names = []
                for ver in versions:
                    mc_versions = ', '.join(ver['game_versions'][:3])
                    version_names.append(f"{ver['name']} - MC {mc_versions}")
                
                self.version_combo['values'] = version_names
                if version_names:
                    self.version_combo.current(0)
                    self.on_version_select(None)
                
                self.status_label.config(text=f"✓ Loaded {len(versions)} versions", fg="#5cb85c")
                
            except Exception as e:
                self.status_label.config(text=f"Error: {e}", fg="#d9534f")
        
        threading.Thread(target=load_versions_thread, daemon=True).start()
    
    def on_version_select(self, event):
        """Handle version selection"""
        if not self.version_combo.get():
            return
        
        index = self.version_combo.current()
        self.selected_version = self.modpack_versions[index]
        self.install_btn.config(state=tk.NORMAL)
    
    def install_modpack(self):
        """Install the selected modpack"""
        if not self.selected_modpack or not self.selected_version:
            messagebox.showerror("Error", "Please select a modpack and version!")
            return
        
        pack_name = self.selected_modpack['slug']
        version_name = self.selected_version['name']
        
        confirm = messagebox.askyesno(
            "Confirm Installation",
            f"Install {self.selected_modpack['title']}\n"
            f"Version: {version_name}\n\n"
            f"This will download the modpack and all mods."
        )
        
        if not confirm:
            return
        
        self.status_label.config(text=f"⏳ Installing {pack_name}...", fg="#ffffff")
        self.install_btn.config(state=tk.DISABLED)
        
        def install_thread():
            try:
                success = self.modrinth.download_modpack(self.selected_version, pack_name)
                
                if success:
                    self.status_label.config(
                        text=f"✓ {self.selected_modpack['title']} installed successfully!",
                        fg="#5cb85c"
                    )
                    messagebox.showinfo(
                        "Success",
                        f"{self.selected_modpack['title']} has been installed!\n\n"
                        f"You can now launch it from the main launcher."
                    )
                else:
                    self.status_label.config(text="✗ Installation failed", fg="#d9534f")
                    messagebox.showerror("Error", "Failed to install modpack. Check console for details.")
                
            except Exception as e:
                self.status_label.config(text=f"✗ Error: {e}", fg="#d9534f")
                messagebox.showerror("Error", f"Installation error:\n{e}")
            finally:
                self.install_btn.config(state=tk.NORMAL)
        
        threading.Thread(target=install_thread, daemon=True).start()


def main():
    """Test the modpacks window"""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    ModpacksWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
