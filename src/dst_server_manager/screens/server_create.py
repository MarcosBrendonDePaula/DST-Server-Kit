import customtkinter as ctk
from tkinter import messagebox
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Callable
from threading import Thread
from queue import Queue
from ..server_manager import ServerManager

class ServerTemplate:
    """Template data for server creation"""
    TEMPLATES = [
        {
            "name": "Survival Server",
            "description": "Classic survival experience",
            "preset": "default",
            "settings": {
                "game_mode": "survival",
                "max_players": 6,
                "pvp": False,
                "pause_when_empty": True
            }
        },
        {
            "name": "Endless Server",
            "description": "Long-term gameplay with abundant resources",
            "preset": "endless",
            "settings": {
                "game_mode": "endless",
                "max_players": 8,
                "pvp": False,
                "pause_when_empty": True
            }
        },
        {
            "name": "PvP Server",
            "description": "Competitive survival with PvP enabled",
            "preset": "wilderness",
            "settings": {
                "game_mode": "survival",
                "max_players": 10,
                "pvp": True,
                "pause_when_empty": False
            }
        }
    ]

class ServerCreateScreen(ctk.CTkFrame):
    """Screen for creating a new server"""
    def __init__(self, parent, manager: ServerManager, switch_screen: Callable):
        super().__init__(parent)
        self.manager = manager
        self.switch_screen = switch_screen
        
        self._create_header()
        self._create_templates_section()
    
    def _create_header(self):
        """Create the header section with back button and title"""
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(header, text="← Back",
                     command=lambda: self.switch_screen("list")).pack(side="left")
        
        ctk.CTkLabel(header, text="Create New Server", 
                    font=("Arial", 24, "bold")).pack(side="left", padx=20)
    
    def _create_templates_section(self):
        """Create the templates section with server template cards"""
        templates_frame = ctk.CTkFrame(self)
        templates_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for template in ServerTemplate.TEMPLATES:
            self._create_template_card(templates_frame, template)
    
    def _create_template_card(self, parent: ctk.CTkFrame, template: Dict[str, Any]):
        """Create a card for a server template"""
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(card, text=template["name"],
                    font=("Arial", 16, "bold")).pack(padx=10, pady=5)
        ctk.CTkLabel(card, text=template["description"]).pack(padx=10)
        
        ctk.CTkButton(card, text="Use Template",
                     command=lambda: self._show_create_dialog(template)).pack(padx=10, pady=10)
    
    def _show_create_dialog(self, template: Dict[str, Any]):
        """Show dialog for entering server details"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create Server")
        dialog.geometry("600x700")
        dialog.attributes('-topmost', True)
        
        # Server name input
        name_frame = ctk.CTkFrame(dialog)
        name_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(name_frame, text="Server Name:").pack(side="left", padx=5)
        name_entry = ctk.CTkEntry(name_frame)
        name_entry.pack(side="right", expand=True, fill="x", padx=5)
        
        # Cluster token input
        token_frame = ctk.CTkFrame(dialog)
        token_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(token_frame, text="Cluster Token:").pack(side="left", padx=5)
        token_entry = ctk.CTkEntry(token_frame)
        token_entry.pack(side="right", expand=True, fill="x", padx=5)
        
        # Progress section
        progress_frame = ctk.CTkFrame(dialog)
        progress_frame.pack(fill="x", padx=20, pady=10)
        progress_label = ctk.CTkLabel(progress_frame, text="")
        progress_label.pack(pady=5)
        progress_bar = ctk.CTkProgressBar(progress_frame)
        progress_bar.pack(fill="x", pady=5)
        progress_bar.set(0)
        
        # Log viewer
        log_frame = ctk.CTkFrame(dialog)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        log_label = ctk.CTkLabel(log_frame, text="Installation Log:")
        log_label.pack(pady=5)
        
        log_text = ctk.CTkTextbox(log_frame, height=300)
        log_text.pack(fill="both", expand=True, pady=5)
        log_text.configure(state="disabled")
        
        def add_log(message: str):
            log_text.configure(state="normal")
            log_text.insert("end", message + "\n")
            log_text.see("end")
            log_text.configure(state="disabled")
            dialog.update()
        
        def update_progress(step: str, progress: float):
            progress_label.configure(text=step)
            progress_bar.set(progress)
            add_log(step)
            dialog.update()
        
        def create_server():
            server_name = name_entry.get().strip()
            cluster_token = token_entry.get().strip()
            
            if not server_name:
                messagebox.showwarning("Warning", "Please enter a server name")
                return
            
            if not server_name.replace('_', '').isalnum():
                messagebox.showwarning("Warning", "Server name can only contain letters, numbers, and underscores")
                return
            
            # Disable inputs
            name_entry.configure(state="disabled")
            token_entry.configure(state="disabled")
            create_button.configure(state="disabled")
            
            def progress_callback(message: str, progress: float):
                if progress_callback.cancelled:
                    return
                progress_label.configure(text=message)
                progress_bar.set(progress)
                add_log(message)
                dialog.update()
            
            progress_callback.cancelled = False
            
            try:
                # Create server with progress tracking
                settings = template["settings"].copy()
                settings.update({
                    "name": server_name,
                    "description": template["description"],
                    "world_preset": template["preset"]
                })
                
                # Create server
                self.manager.create_server(server_name, settings, progress_callback)
                
                # Save cluster token if provided
                if cluster_token:
                    progress_callback("Saving cluster token...", 0.95)
                    token_path = Path(self.manager.base_path) / server_name / "cluster_token.txt"
                    with open(token_path, 'w') as f:
                        f.write(cluster_token)
                
                progress_callback("Server created successfully!", 1.0)
                messagebox.showinfo("Success", f"Server '{server_name}' created!")
                dialog.destroy()
                self.switch_screen("list")
                
            except Exception as e:
                progress_callback.cancelled = True
                messagebox.showerror("Error", f"Failed to create server: {str(e)}")
                dialog.destroy()
        
        # Create button
        create_button = ctk.CTkButton(dialog, text="Create Server",
                                    command=create_server)
        create_button.pack(pady=20)
