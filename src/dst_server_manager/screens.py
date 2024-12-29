import customtkinter as ctk
from typing import Optional, Dict, Any
from .screens import ServerListScreen, ServerCreateScreen, ServerConfigScreen
from .server_manager import ServerManager

class ScreenManager(ctk.CTkFrame):
    """Main screen manager that handles switching between different screens"""
    def __init__(self, parent, manager: ServerManager):
        super().__init__(parent)
        self.manager = manager
        self.current_screen = None
        
        # Show initial screen
        self.switch_screen("list")
    
    def switch_screen(self, screen_name: str, **kwargs):
        """Switch to a different screen"""
        # Remove current screen if exists
        if self.current_screen:
            self.current_screen.destroy()
        
        # Create and show new screen
        if screen_name == "list":
            self.current_screen = ServerListScreen(
                self,
                self.manager,
                self.switch_screen
            )
        elif screen_name == "create":
            self.current_screen = ServerCreateScreen(
                self,
                self.manager,
                self.switch_screen
            )
        elif screen_name == "config":
            if "server_name" not in kwargs:
                raise ValueError("server_name is required for config screen")
            self.current_screen = ServerConfigScreen(
                self,
                self.manager,
                self.switch_screen,
                kwargs["server_name"]
            )
        else:
            raise ValueError(f"Unknown screen: {screen_name}")
        
        self.current_screen.pack(fill="both", expand=True)
