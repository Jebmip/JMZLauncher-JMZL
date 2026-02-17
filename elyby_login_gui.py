#!/usr/bin/env python3
"""
Ely.by Login Dialog
GUI for logging into Ely.by accounts
"""

import tkinter as tk
from tkinter import messagebox
import threading
from elyby_auth import ElyByAuth

class ElyByLoginDialog:
    def __init__(self, parent, callback=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Ely.by Login")
        self.window.geometry("400x350")
        self.window.configure(bg="#1e1e1e")
        self.window.resizable(False, False)
        
        self.elyby = ElyByAuth()
        self.callback = callback
        
        # Make dialog modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
        # Check if already logged in
        stored = self.elyby.get_stored_auth()
        if stored:
            self.show_logged_in_state(stored)
    
    def setup_ui(self):
        """Setup the login UI"""
        # Header
        header_frame = tk.Frame(self.window, bg="#2d2d2d", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🔐 Ely.by Account",
            font=("Segoe UI", 16, "bold"),
            bg="#2d2d2d",
            fg="#ffffff"
        )
        title_label.pack(pady=15)
        
        # Content
        content_frame = tk.Frame(self.window, bg="#1e1e1e", padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Info text
        info_label = tk.Label(
            content_frame,
            text="Login to use your Ely.by skin in-game.\nDon't have an account? Visit ely.by",
            font=("Segoe UI", 9),
            bg="#1e1e1e",
            fg="#aaaaaa",
            justify=tk.CENTER
        )
        info_label.pack(pady=(0, 20))
        
        # Login form
        self.form_frame = tk.Frame(content_frame, bg="#1e1e1e")
        self.form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username
        tk.Label(
            self.form_frame,
            text="Username or Email:",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.username_var = tk.StringVar()
        self.username_entry = tk.Entry(
            self.form_frame,
            textvariable=self.username_var,
            font=("Segoe UI", 10),
            bg="#3d3d3d",
            fg="#ffffff",
            relief=tk.FLAT,
            insertbackground="#ffffff"
        )
        self.username_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))
        
        # Password
        tk.Label(
            self.form_frame,
            text="Password:",
            font=("Segoe UI", 10, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            self.form_frame,
            textvariable=self.password_var,
            font=("Segoe UI", 10),
            bg="#3d3d3d",
            fg="#ffffff",
            relief=tk.FLAT,
            insertbackground="#ffffff",
            show="●"
        )
        self.password_entry.pack(fill=tk.X, ipady=8, pady=(0, 20))
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Status label
        self.status_label = tk.Label(
            self.form_frame,
            text="",
            font=("Segoe UI", 9),
            bg="#1e1e1e",
            fg="#5cb85c"
        )
        self.status_label.pack(pady=(0, 15))
        
        # Buttons
        button_frame = tk.Frame(self.form_frame, bg="#1e1e1e")
        button_frame.pack(fill=tk.X)
        
        self.login_button = tk.Button(
            button_frame,
            text="Login",
            font=("Segoe UI", 11, "bold"),
            bg="#5cb85c",
            fg="white",
            activebackground="#4a9d4a",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.login
        )
        self.login_button.pack(fill=tk.X, ipady=10, pady=(0, 8))
        
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg="#5a6268",
            fg="white",
            activebackground="#4a5258",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.window.destroy
        )
        cancel_button.pack(fill=tk.X, ipady=8)
    
    def show_logged_in_state(self, auth_data):
        """Show logged in state"""
        # Clear form
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        
        # Show logged in info
        tk.Label(
            self.form_frame,
            text=f"✓ Logged in as:",
            font=("Segoe UI", 10),
            bg="#1e1e1e",
            fg="#5cb85c"
        ).pack(pady=(0, 10))
        
        tk.Label(
            self.form_frame,
            text=auth_data['username'],
            font=("Segoe UI", 14, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        ).pack(pady=(0, 5))
        
        tk.Label(
            self.form_frame,
            text=f"UUID: {auth_data['uuid']}",
            font=("Segoe UI", 8),
            bg="#1e1e1e",
            fg="#aaaaaa"
        ).pack(pady=(0, 30))
        
        # Buttons
        button_frame = tk.Frame(self.form_frame, bg="#1e1e1e")
        button_frame.pack(fill=tk.X)
        
        logout_button = tk.Button(
            button_frame,
            text="Logout",
            font=("Segoe UI", 11, "bold"),
            bg="#d9534f",
            fg="white",
            activebackground="#c9302c",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.logout
        )
        logout_button.pack(fill=tk.X, ipady=10, pady=(0, 8))
        
        close_button = tk.Button(
            button_frame,
            text="Close",
            font=("Segoe UI", 10),
            bg="#5a6268",
            fg="white",
            activebackground="#4a5258",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.window.destroy
        )
        close_button.pack(fill=tk.X, ipady=8)
    
    def login(self):
        """Handle login"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password!")
            return
        
        self.status_label.config(text="⏳ Logging in...", fg="#ffffff")
        self.login_button.config(state=tk.DISABLED)
        
        def login_thread():
            try:
                auth_data = self.elyby.login(username, password)
                
                if auth_data:
                    self.status_label.config(text="✓ Login successful!", fg="#5cb85c")
                    messagebox.showinfo(
                        "Success",
                        f"Logged in as {auth_data['username']}!\n\n"
                        f"Your skin will now appear in-game."
                    )
                    
                    if self.callback:
                        self.callback(auth_data)
                    
                    self.show_logged_in_state(auth_data)
                else:
                    self.status_label.config(text="✗ Login failed", fg="#d9534f")
                    messagebox.showerror(
                        "Login Failed",
                        "Invalid username or password.\n\n"
                        "Make sure you're using your Ely.by credentials."
                    )
                    self.login_button.config(state=tk.NORMAL)
                    
            except Exception as e:
                self.status_label.config(text=f"✗ Error: {e}", fg="#d9534f")
                messagebox.showerror("Error", f"Login error:\n{e}")
                self.login_button.config(state=tk.NORMAL)
        
        threading.Thread(target=login_thread, daemon=True).start()
    
    def logout(self):
        """Handle logout"""
        confirm = messagebox.askyesno(
            "Confirm Logout",
            "Are you sure you want to logout?\n\n"
            "You'll need to login again to use your skin."
        )
        
        if confirm:
            self.elyby.logout()
            
            if self.callback:
                self.callback(None)
            
            messagebox.showinfo("Logged Out", "You have been logged out from Ely.by.")
            self.window.destroy()


def main():
    """Test the login dialog"""
    root = tk.Tk()
    root.withdraw()
    
    def on_login(auth_data):
        if auth_data:
            print(f"Logged in as: {auth_data['username']}")
        else:
            print("Logged out")
    
    ElyByLoginDialog(root, callback=on_login)
    root.mainloop()


if __name__ == "__main__":
    main()
