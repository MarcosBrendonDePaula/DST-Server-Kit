import customtkinter as ctk
from datetime import datetime
from typing import Dict, Any, Optional

class SaveCard(ctk.CTkFrame):
    """A card widget displaying save information"""
    def __init__(self, parent, server_data: Dict[str, Any], on_select: callable):
        super().__init__(parent)
        
        # Store server data
        self.server_data = server_data
        self.server_name = str(server_data.get("name", ""))
        
        # Create card text
        card_text = self._format_save_info(server_data)
        
        # Create button that fills the frame
        self.button = ctk.CTkButton(
            self,
            text="\n".join(card_text),
            command=lambda: on_select(self.server_name),
            width=700,
            height=150,
            anchor="w",
            font=("Arial", 12),
            fg_color=("gray70", "gray30"),
            hover_color=("gray75", "gray25")
        )
        self.button.pack(fill="both", expand=True)
    
    def _format_save_info(self, server_data: Dict[str, Any]) -> list[str]:
        """Format save information into text lines"""
        text_lines = [server_data["name"]]
        
        # Add last save time
        if server_data["last_save"]:
            save_time = datetime.fromtimestamp(server_data["last_save"])
            time_str = save_time.strftime("%Y-%m-%d %H:%M")
            text_lines.append(f"Last Save: {time_str}")
        
        # Add overworld info
        if server_data["master"]:
            text_lines.append("\nOverworld:")
            if "day" in server_data["master"]:
                text_lines.append(f"Day {server_data['master']['day']}")
            if "season" in server_data["master"]:
                text_lines.append(f"Season: {server_data['master']['season']}")
            if "playtime" in server_data["master"]:
                hours = int(server_data["master"]["playtime"] // 60)
                minutes = int(server_data["master"]["playtime"] % 60)
                text_lines.append(f"Playtime: {hours}h {minutes}m")
        
        # Add caves info
        if server_data["caves"]:
            text_lines.append("\nCaves:")
            if "playtime" in server_data["caves"]:
                hours = int(server_data["caves"]["playtime"] // 60)
                minutes = int(server_data["caves"]["playtime"] % 60)
                text_lines.append(f"Playtime: {hours}h {minutes}m")
        
        # Add mod info
        if "mods" in server_data and server_data["mods"]:
            text_lines.append(f"\nMods: {len(server_data['mods'])} installed")
        
        return text_lines
    
    def set_selected(self, selected: bool):
        """Update card appearance based on selection state"""
        color = ("gray75", "gray25") if selected else ("gray70", "gray30")
        self.button.configure(fg_color=color)
