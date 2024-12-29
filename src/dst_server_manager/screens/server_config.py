import customtkinter as ctk
from tkinter import messagebox
from typing import Callable
from ..components.settings_tab import SettingsTab
from ..components.mods_tab import ModsTab
from ..components.save_card import SaveCard
from ..server_manager import ServerManager

class ServerConfigScreen(ctk.CTkFrame):
    """Screen for configuring a server"""
    def __init__(self, parent, manager: ServerManager, switch_screen: Callable, server_name: str):
        super().__init__(parent)
        self.manager = manager
        self.switch_screen = switch_screen
        self.server_name = server_name
        
        self._create_header()
        self._create_notebook()
    
    def _create_header(self):
        """Create the header section"""
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(header, text="← Back",
                     command=lambda: self.switch_screen("list")).pack(side="left")
        
        ctk.CTkLabel(header, text=f"Configure Server: {self.server_name}", 
                    font=("Arial", 24, "bold")).pack(side="left", padx=20)
    
    def _create_notebook(self):
        """Create notebook with tabs"""
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add tabs
        self.notebook.add("Settings")
        self.notebook.add("Mods")
        
        # Settings tab
        self.settings_tab = SettingsTab(
            self.notebook.tab("Settings"),
            self.server_name,
            self.manager,
            on_save=None  # Add callback if needed
        )
        self.settings_tab.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Override import dialog handler
        self.settings_tab.show_import_dialog = self.show_import_dialog
        
        # Mods tab
        self.mods_tab = ModsTab(
            self.notebook.tab("Mods"),
            self.server_name,
            self.manager
        )
        self.mods_tab.pack(fill="both", expand=True, padx=10, pady=10)
    
    def show_import_dialog(self):
        """Show dialog to import save from another server"""
        try:
            # Get list of servers with saves
            servers = self.manager.world_manager.list_servers_with_saves()
            if not servers:
                messagebox.showinfo("Import Save", "No servers with saves found")
                return
            
            def import_callback(source: str, target: str):
                try:
                    self.manager.world_manager.import_save(source, target)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to import save: {str(e)}")
            
            # Get root window
            root = self.winfo_toplevel()
            
            # Create dialog
            from ..components.import_dialog import ImportDialog
            dialog = ImportDialog(
                root, 
                servers, 
                self.server_name, 
                import_callback, 
                manager=self.manager,
                on_complete=lambda: self.mods_tab.refresh_mods()  # Refresh mods after import
            )
            
            # Wait for dialog window
            root.wait_window(dialog.window)
            
        except Exception as e:
            print(f"Dialog error: {str(e)}")  # Debug print
            messagebox.showerror("Error", f"Failed to show import dialog: {str(e)}")
