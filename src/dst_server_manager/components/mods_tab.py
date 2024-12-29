import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
from typing import Dict, Any

class ModsTab(ctk.CTkFrame):
    """Mods tab for server configuration"""
    def __init__(self, parent, server_name: str, manager):
        super().__init__(parent)
        self.server_name = server_name
        self.manager = manager
        
        self._create_add_section()
        self._create_mods_list()
        
        # Load initial mods
        self.refresh_mods()
    
    def _create_add_section(self):
        """Create the add mod section"""
        add_frame = ctk.CTkFrame(self)
        add_frame.pack(fill="x", padx=5, pady=5)
        
        self.mod_id_entry = ctk.CTkEntry(add_frame, placeholder_text="Mod ID")
        self.mod_id_entry.pack(side="left", expand=True, fill="x", padx=5)
        
        self.mod_name_entry = ctk.CTkEntry(add_frame, placeholder_text="Mod Name")
        self.mod_name_entry.pack(side="left", expand=True, fill="x", padx=5)
        
        ctk.CTkButton(add_frame, text="Add Mod",
                     command=self.add_mod).pack(side="right", padx=5)
    
    def _create_mods_list(self):
        """Create the scrollable mods list"""
        self.mods_list = ctk.CTkScrollableFrame(self)
        self.mods_list.pack(fill="both", expand=True, padx=5, pady=5)
    
    def refresh_mods(self):
        """Refresh the mods list"""
        try:
            # Clear existing mods
            for widget in self.mods_list.winfo_children():
                widget.destroy()
            
            # Get mods and their configurations
            mods = self.manager.mod_manager.get_server_mods(self.server_name)
            
            # Create a row for each mod
            for mod_id, mod_config in mods.items():
                self._create_mod_row(mod_id, mod_config)
        except Exception as e:
            print(f"Error refreshing mods: {str(e)}")
    
    def _create_mod_row(self, mod_id: str, mod_config: Dict[str, Any]):
        """Create a row for a mod in the list"""
        mod_frame = ctk.CTkFrame(self.mods_list)
        mod_frame.pack(fill="x", padx=5, pady=2)
        
        # Enable/Disable checkbox
        enabled = ctk.CTkCheckBox(mod_frame, text="", width=60)
        enabled.pack(side="left", padx=5)
        if mod_config.get('enabled', True):
            enabled.select()
        enabled.configure(command=lambda: self.toggle_mod(mod_id, enabled.get()))
        
        # Mod info
        mod_name = self.manager.mod_manager.mod_settings.get('servers', {}).get(self.server_name, {}).get(mod_id, {}).get('name', f"Mod {mod_id}")
        ctk.CTkLabel(mod_frame, text=f"{mod_name} ({mod_id})").pack(side="left", padx=5)
        
        # Remove button
        ctk.CTkButton(mod_frame, text="Remove",
                     command=lambda: self.remove_mod(mod_id),
                     fg_color="darkred", width=80).pack(side="right", padx=5)
        
        # Configure button
        ctk.CTkButton(mod_frame, text="Configure",
                     command=lambda: self.open_mod_folder(mod_id),
                     width=80).pack(side="right", padx=5)
    
    def add_mod(self):
        """Add a mod to the server"""
        mod_id = self.mod_id_entry.get().strip()
        mod_name = self.mod_name_entry.get().strip()
        
        if not mod_id or not mod_name:
            messagebox.showwarning("Warning", "Please enter both Mod ID and Name")
            return
        
        try:
            # Create mod info with custom name
            mod_info = {
                'name': mod_name,
                'version': '1.0'
            }
            
            # Add the mod
            self.manager.mod_manager._fetch_mod_info = lambda x: mod_info
            self.manager.mod_manager.add_mod(self.server_name, mod_id)
            
            # Clear inputs and refresh
            self.mod_id_entry.delete(0, tk.END)
            self.mod_name_entry.delete(0, tk.END)
            self.refresh_mods()
            
            # Show success message
            messagebox.showinfo("Success", f"Mod {mod_name} ({mod_id}) added!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add mod: {str(e)}")
    
    def toggle_mod(self, mod_id: str, enabled: bool):
        """Toggle mod enabled/disabled state"""
        try:
            current_config = self.manager.mod_manager.get_server_mods(self.server_name).get(mod_id, {})
            current_config['enabled'] = enabled
            self.manager.mod_manager.update_mod_config(self.server_name, mod_id, current_config)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update mod state: {str(e)}")
    
    def remove_mod(self, mod_id: str):
        """Remove a mod"""
        try:
            # Confirm removal
            if not messagebox.askyesno("Confirm Remove", f"Are you sure you want to remove mod {mod_id}?"):
                return
            
            # Remove mod
            self.manager.mod_manager.remove_mod(self.server_name, mod_id)
            
            # Clear and refresh UI
            for widget in self.mods_list.winfo_children():
                widget.destroy()
            self.refresh_mods()
            
            messagebox.showinfo("Success", f"Mod {mod_id} removed!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove mod: {str(e)}")
    
    def open_mod_folder(self, mod_id: str):
        """Open the mod folder"""
        try:
            mod_path = os.path.join(self.manager.steamcmd_path, 
                                  "steamapps", 
                                  "workshop",
                                  "content",
                                  "322330",  # DST App ID
                                  mod_id)
            
            if os.path.exists(mod_path):
                os.startfile(mod_path)
            else:
                messagebox.showwarning("Warning", "Mod folder not found. The mod may not be downloaded yet.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open mod folder: {str(e)}")
