import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
from pathlib import Path
from typing import Dict, Any, Callable

class SettingsTab(ctk.CTkFrame):
    """Settings tab for server configuration"""
    def __init__(self, parent, server_name: str, manager, on_save: Callable = None):
        super().__init__(parent)
        self.server_name = server_name
        self.manager = manager
        self.on_save = on_save
        self.settings_widgets = {}
        
        self._create_basic_settings()
        self._create_game_settings()
        self._create_cluster_token()
        self._create_control_buttons()
        self._create_action_buttons()
        
        # Load initial configuration
        self.load_config()
        
        # Start periodic status updates
        self.after(1000, self.update_control_buttons)
    
    def _create_basic_settings(self):
        """Create basic server settings section"""
        basic_settings = [
            ("name", "Server Name"),
            ("description", "Description"),
            ("max_players", "Max Players"),
            ("password", "Password (optional)"),
        ]
        
        for key, label in basic_settings:
            frame = ctk.CTkFrame(self)
            frame.pack(padx=5, pady=5, fill="x")
            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame)
            entry.pack(side="right", padx=5, expand=True, fill="x")
            self.settings_widgets[key] = entry
    
    def _create_game_settings(self):
        """Create game mode and world preset settings"""
        # Game mode selection
        frame = ctk.CTkFrame(self)
        frame.pack(padx=5, pady=5, fill="x")
        ctk.CTkLabel(frame, text="Game Mode").pack(side="left", padx=5)
        self.settings_widgets["game_mode"] = ctk.CTkComboBox(
            frame, values=["survival", "endless", "wilderness"])
        self.settings_widgets["game_mode"].pack(side="right", padx=5)
        
        # World preset selection
        frame = ctk.CTkFrame(self)
        frame.pack(padx=5, pady=5, fill="x")
        ctk.CTkLabel(frame, text="World Preset").pack(side="left", padx=5)
        self.settings_widgets["world_preset"] = ctk.CTkComboBox(
            frame, values=["default", "endless", "wilderness"])
        self.settings_widgets["world_preset"].pack(side="right", padx=5)
        
        # Checkboxes
        checkbox_frame = ctk.CTkFrame(self)
        checkbox_frame.pack(padx=5, pady=5, fill="x")
        
        self.settings_widgets["pvp"] = ctk.CTkCheckBox(
            checkbox_frame, text="PvP")
        self.settings_widgets["pvp"].pack(side="left", padx=20)
        
        self.settings_widgets["pause_when_empty"] = ctk.CTkCheckBox(
            checkbox_frame, text="Pause When Empty")
        self.settings_widgets["pause_when_empty"].pack(side="left", padx=20)
    
    def _create_cluster_token(self):
        """Create cluster token input section"""
        token_frame = ctk.CTkFrame(self)
        token_frame.pack(padx=5, pady=5, fill="x")
        
        ctk.CTkLabel(token_frame, text="Cluster Token").pack(side="left", padx=5)
        self.cluster_token_entry = ctk.CTkEntry(token_frame)
        self.cluster_token_entry.pack(side="right", padx=5, expand=True, fill="x")
        
        # Load cluster token if exists
        token_path = Path(self.manager.base_path) / self.server_name / "cluster_token.txt"
        if token_path.exists():
            with open(token_path, 'r') as f:
                self.cluster_token_entry.insert(0, f.read().strip())
    
    def _create_control_buttons(self):
        """Create server control buttons"""
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(padx=5, pady=10, fill="x")
        
        self.start_button = ctk.CTkButton(control_frame, text="Start Server",
                                        command=self.start_server)
        self.start_button.pack(side="left", padx=5, expand=True)
        
        self.stop_button = ctk.CTkButton(control_frame, text="Stop Server",
                                       command=self.stop_server,
                                       fg_color="darkred")
        self.stop_button.pack(side="right", padx=5, expand=True)
    
    def _create_action_buttons(self):
        """Create action buttons"""
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(padx=5, pady=10, fill="x")
        
        ctk.CTkButton(button_frame, text="Save Changes",
                     command=self.save_config).pack(side="left", padx=5, expand=True)
        
        ctk.CTkButton(button_frame, text="Import Save",
                     command=self._on_import_click).pack(side="right", padx=5)
        
        ctk.CTkButton(button_frame, text="Open World Folder",
                     command=self.open_world_folder).pack(side="right", padx=5)
    
    def _on_import_click(self):
        """Handle import button click"""
        if hasattr(self, 'show_import_dialog'):
            self.show_import_dialog()
    
    def load_config(self):
        """Load server configuration into the UI"""
        try:
            config = self.manager.config_manager.get_server_config(self.server_name)
            
            # Update settings widgets
            for key, widget in self.settings_widgets.items():
                if key in config:
                    if isinstance(widget, ctk.CTkCheckBox):
                        widget.select() if config[key] else widget.deselect()
                    elif isinstance(widget, ctk.CTkComboBox):
                        widget.set(str(config[key]))
                    elif isinstance(widget, ctk.CTkEntry):
                        widget.delete(0, tk.END)
                        widget.insert(0, str(config[key]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load server config: {str(e)}")
    
    def save_config(self):
        """Save current configuration"""
        try:
            # Save settings
            settings = {}
            for key, widget in self.settings_widgets.items():
                if isinstance(widget, ctk.CTkCheckBox):
                    settings[key] = widget.get()
                elif isinstance(widget, ctk.CTkComboBox):
                    settings[key] = widget.get()
                elif isinstance(widget, ctk.CTkEntry):
                    value = widget.get()
                    if key == "max_players":
                        try:
                            value = int(value)
                        except ValueError:
                            value = 6  # Default value if invalid
                    # Don't update server name if it's empty
                    if key == "name" and not value:
                        continue
                    settings[key] = value
            
            # Update server configuration
            try:
                self.manager.update_server_config(self.server_name, settings)
            except Exception as e:
                logger.error(f"Failed to update server config: {str(e)}")
                raise
            
            # Save cluster token
            token = self.cluster_token_entry.get().strip()
            if token:
                token_path = Path(self.manager.base_path) / self.server_name / "cluster_token.txt"
                with open(token_path, 'w') as f:
                    f.write(token)
            
            messagebox.showinfo("Success", "Server configuration saved!")
            
            if self.on_save:
                self.on_save()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
    
    def update_control_buttons(self):
        """Update control button states based on server status"""
        try:
            status = self.manager.get_server_status(self.server_name)
            if status['running']:
                self.start_button.configure(state="disabled")
                self.stop_button.configure(state="normal")
            else:
                self.start_button.configure(state="normal")
                self.stop_button.configure(state="disabled")
        except Exception:
            # If there's an error getting status, disable both buttons
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="disabled")
        
        # Schedule next update
        self.after(1000, self.update_control_buttons)
    
    def start_server(self):
        """Start the server"""
        try:
            self.manager.start_server(self.server_name)
            messagebox.showinfo("Success", f"Server '{self.server_name}' started!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
    
    def stop_server(self):
        """Stop the server"""
        try:
            self.manager.stop_server(self.server_name)
            messagebox.showinfo("Success", f"Server '{self.server_name}' stopped!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {str(e)}")
    
    def open_world_folder(self):
        """Open the world folder"""
        try:
            server_path = os.path.join(self.manager.base_path, self.server_name)
            if os.path.exists(server_path):
                os.startfile(server_path)
            else:
                messagebox.showwarning("Warning", "Server folder not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
