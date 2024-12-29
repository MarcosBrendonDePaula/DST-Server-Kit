import customtkinter as ctk
from typing import Dict, Any, Callable

class ServerCard(ctk.CTkFrame):
    """A card widget displaying server information"""
    def __init__(self, parent, server_name: str, server_info: Dict[str, Any], 
                 on_configure: Callable, on_start: Callable, on_stop: Callable):
        super().__init__(parent)
        
        self.server_name = server_name
        self.server_info = server_info
        
        self._create_title_section()
        self._create_details_section()
        self._create_action_buttons(on_configure, on_start, on_stop)
    
    def _create_title_section(self):
        """Create the title section with server name and status"""
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(title_frame, text=self.server_info['name'], 
                    font=("Arial", 16, "bold")).pack(side="left")
        
        status_color = "green" if self.server_info['running'] else "gray"
        status_text = "Running" if self.server_info['running'] else "Stopped"
        ctk.CTkLabel(title_frame, text=status_text, 
                    text_color=status_color).pack(side="right")
    
    def _create_details_section(self):
        """Create the details section with server information"""
        details_frame = ctk.CTkFrame(self)
        details_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(details_frame, text=self.server_info['description']).pack(anchor="w")
        ctk.CTkLabel(details_frame, 
                    text=f"Game Mode: {self.server_info['game_mode']} | Players: {self.server_info['max_players']}").pack(anchor="w")
        
        if self.server_info['running'] and self.server_info['uptime'] is not None:
            hours = int(self.server_info['uptime'] // 3600)
            minutes = int((self.server_info['uptime'] % 3600) // 60)
            ctk.CTkLabel(details_frame, 
                        text=f"Uptime: {hours}h {minutes}m").pack(anchor="w")
    
    def _create_action_buttons(self, on_configure: Callable, on_start: Callable, on_stop: Callable):
        """Create action buttons for server control"""
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="Configure",
                     command=lambda: on_configure(self.server_name)).pack(side="left", padx=5)
        
        if self.server_info['running']:
            ctk.CTkButton(button_frame, text="Stop Server",
                         command=lambda: on_stop(self.server_name),
                         fg_color="darkred").pack(side="right", padx=5)
        else:
            ctk.CTkButton(button_frame, text="Start Server",
                         command=lambda: on_start(self.server_name)).pack(side="right", padx=5)
