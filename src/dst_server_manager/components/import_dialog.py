import customtkinter as ctk
from tkinter import messagebox
from typing import List, Dict, Any, Callable, Optional
from .save_card import SaveCard
import logging

logger = logging.getLogger('ImportDialog')

class ImportDialog:
    """Dialog for importing saves from other servers"""
    def __init__(self, parent, servers: List[Dict[str, Any]], current_server: str, import_callback: Callable[[str, str], None], manager=None, on_complete: Optional[Callable] = None):
        # Create dialog window
        self.window = ctk.CTkToplevel(parent)
        self.window.withdraw()  # Hide initially
        
        # Store parameters
        self.parent = parent
        self.servers = servers
        self.current_server = current_server
        self.import_callback = import_callback
        self.manager = manager
        self.on_complete = on_complete
        self.selected_server = None
        self.cards = []
        
        # Configure window
        self.window.title("Import Save")
        self.window.geometry("800x600")
        self.window.resizable(False, False)
        
        # Configure appearance
        self.window.configure(fg_color=("gray95", "gray10"))
        
        # Create main container
        self.container = ctk.CTkFrame(self.window, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create widgets
        self._create_widgets()
        
        # Position window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.window.geometry(f"+{x}+{y}")
        
        # Make dialog modal
        self.window.transient(parent)
        self.window.deiconify()  # Show window
        self.window.grab_set()
        self.window.focus_force()
        
        # Bind escape key to close
        self.window.bind('<Escape>', lambda e: self.destroy())
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Header with close button
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header, text="Import World Save", 
                    font=("Arial", 24, "bold")).pack(side="left")
        
        ctk.CTkButton(header, text="×", width=30, height=30,
                     command=self.destroy).pack(side="right")
        
        # Cards container
        cards_frame = ctk.CTkScrollableFrame(self.container)
        cards_frame.pack(fill="both", expand=True)
        
        # Create cards
        for server in self.servers:
            server_name = str(server.get("name", "")).strip()
            current_name = str(self.current_server).strip()
            
            if server_name == current_name:  # Skip current server
                continue
            
            card = SaveCard(cards_frame, server, self._on_select)
            card.pack(padx=10, pady=5)
            self.cards.append(card)
        
        # Progress bar (hidden initially)
        self.progress_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(10, 0))
        self.progress_frame.pack_forget()
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Importing...")
        self.progress_label.pack(fill="x", pady=(0, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        
        # Import button
        button_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        self.import_button = ctk.CTkButton(
            button_frame, 
            text="Import Selected Save",
            command=self._on_import,
            font=("Arial", 14)
        )
        self.import_button.pack(pady=10, padx=20, fill="x")
    
    def _on_select(self, server_name: str):
        """Handle server selection"""
        self.selected_server = str(server_name)
        for card in self.cards:
            try:
                is_selected = str(card.server_name).strip() == str(server_name).strip()
                card.set_selected(is_selected)
            except Exception as e:
                logger.error(f"Error selecting card: {e}")
    
    def _on_import(self):
        """Handle import button click"""
        if not self.selected_server:
            messagebox.showwarning("Warning", "Please select a server")
            return
        
        try:
            # Find selected server data
            selected_name = str(self.selected_server).strip()
            selected_server = None
            
            # Look for server by name
            for server in self.servers:
                if str(server.get("name", "")).strip() == selected_name:
                    selected_server = server
                    break
            
            if not selected_server:
                raise ValueError(f"Server '{selected_name}' not found")
            
            # Show progress bar
            self.import_button.configure(state="disabled")
            self.progress_frame.pack(fill="x", pady=(10, 0))
            self.progress_bar.set(0)
            self.progress_label.configure(text="Importing save files...")
            self.window.update_idletasks()
            
            # Import save files
            source_server = selected_server["name"]
            self.import_callback(source_server, self.current_server)
            
            # Update progress
            self.progress_bar.set(0.5)
            self.progress_label.configure(text="Importing mods...")
            self.window.update_idletasks()
            
            # Import mods if available
            if self.manager and "mods" in selected_server:
                total_mods = len(selected_server["mods"])
                for i, mod_entry in enumerate(selected_server["mods"]):
                    try:
                        # Handle both old and new mod formats
                        if isinstance(mod_entry, dict):
                            mod_id = str(mod_entry.get('id', ''))
                            config = mod_entry.get('config', {})
                        else:
                            mod_id = str(mod_entry)
                            config = {}
                        
                        if mod_id:
                            # Fetch mod info to get proper name
                            mod_info = self.manager.mod_manager._fetch_mod_info(mod_id)
                            self.manager.mod_manager.add_mod(
                                self.current_server, 
                                mod_id,
                                config
                            )
                            # Update progress
                            progress = 0.5 + ((i + 1) / total_mods * 0.5)
                            self.progress_bar.set(progress)
                            self.progress_label.configure(text=f"Importing mod: {mod_info.get('name', f'Mod {mod_id}')}")
                            self.window.update_idletasks()
                    except Exception as e:
                        logger.error(f"Failed to import mod {mod_id}: {e}")
            
            # Complete
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="Import complete!")
            self.window.update_idletasks()
            
            messagebox.showinfo("Success", "Save and mods imported successfully!")
            
            # Call completion callback if provided
            if self.on_complete:
                self.on_complete()
            
            self.destroy()
            
        except Exception as e:
            self.progress_frame.pack_forget()
            self.import_button.configure(state="normal")
            messagebox.showerror("Error", f"Failed to import save: {str(e)}")
    
    def destroy(self):
        """Clean up and destroy dialog"""
        if hasattr(self, 'window'):
            self.window.grab_release()
            self.window.destroy()
