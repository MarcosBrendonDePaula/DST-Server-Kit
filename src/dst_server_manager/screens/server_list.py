import customtkinter as ctk
from tkinter import messagebox
from typing import Callable
from ..components.server_card import ServerCard
from ..server_manager import ServerManager

class ServerListScreen(ctk.CTkFrame):
    """Main screen showing all servers as cards"""
    def __init__(self, parent, manager: ServerManager, switch_screen: Callable):
        super().__init__(parent)
        self.manager = manager
        self.switch_screen = switch_screen
        
        self._create_header()
        self._create_cards_container()
        
        # Start refresh timer
        self.after(1000, self.refresh_servers)
    
    def _create_header(self):
        """Create the header section with title and create button"""
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(header, text="DST Servers", 
                    font=("Arial", 24, "bold")).pack(side="left")
        
        ctk.CTkButton(header, text="Create New Server",
                     command=lambda: self.switch_screen("create")).pack(side="right")
    
    def _create_cards_container(self):
        """Create the scrollable container for server cards"""
        self.cards_frame = ctk.CTkScrollableFrame(self)
        self.cards_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def refresh_servers(self):
        """Refresh server cards"""
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        # Create cards for each server
        for server_name in self.manager.list_servers():
            status = self.manager.get_server_status(server_name)
            
            card = ServerCard(
                self.cards_frame,
                server_name,
                status,
                lambda s=server_name: self.switch_screen("config", server_name=s),
                lambda s=server_name: self.start_server(s),
                lambda s=server_name: self.stop_server(s)
            )
            card.pack(fill="x", padx=10, pady=5)
        
        # Schedule next refresh
        self.after(1000, self.refresh_servers)
    
    def start_server(self, server_name: str):
        """Start a server"""
        try:
            self.manager.start_server(server_name)
            messagebox.showinfo("Success", f"Server '{server_name}' started!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
    
    def stop_server(self, server_name: str):
        """Stop a server"""
        try:
            self.manager.stop_server(server_name)
            messagebox.showinfo("Success", f"Server '{server_name}' stopped!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {str(e)}")
