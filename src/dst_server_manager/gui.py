import customtkinter as ctk
from typing import Optional, Dict, Any
from dst_server_manager.server_manager import ServerManager
from dst_server_manager.screens.server_list import ServerListScreen
from dst_server_manager.screens.server_create import ServerCreateScreen
from dst_server_manager.screens.server_config import ServerConfigScreen

class ServerManagerGUI:
    def __init__(self):
        self.manager = ServerManager()
        
        # Setup main window
        self.root = ctk.CTk()
        self.root.title("DST Server Manager")
        self.root.geometry("1000x800")
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Current screen
        self.current_screen = None
        
        # Show initial screen
        self.switch_screen("list")
    
    def switch_screen(self, screen_name: str, **kwargs):
        """Switch to a different screen"""
        # Remove current screen if exists
        if self.current_screen:
            self.current_screen.destroy()
        
        # Create new screen
        if screen_name == "list":
            self.current_screen = ServerListScreen(
                self.root,
                self.manager,
                self.switch_screen
            )
        elif screen_name == "create":
            self.current_screen = ServerCreateScreen(
                self.root,
                self.manager,
                self.switch_screen
            )
        elif screen_name == "config":
            if "server_name" not in kwargs:
                raise ValueError("server_name required for config screen")
            self.current_screen = ServerConfigScreen(
                self.root,
                self.manager,
                self.switch_screen,
                kwargs["server_name"]
            )
        else:
            raise ValueError(f"Unknown screen: {screen_name}")
        
        # Show new screen
        self.current_screen.grid(row=0, column=0, sticky="nsew")
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    """Entry point for the GUI application"""
    app = ServerManagerGUI()
    app.run()

if __name__ == "__main__":
    main()
