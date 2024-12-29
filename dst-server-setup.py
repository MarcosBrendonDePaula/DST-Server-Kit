import os
import shutil
import subprocess
import sys
import requests
import json
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog

class DSTServerSetup:
    def __init__(self):
        self.steamcmd_path = "C:\\steamcmd"
        self.documents_path = os.path.expanduser("~\\Documents")
        self.klei_path = os.path.join(self.documents_path, "Klei")
        self.dst_path = os.path.join(self.klei_path, "DoNotStarveTogether")
        self.server_name = "MyDediServer"
        
    def create_directories(self):
        """Create necessary directories for the server"""
        directories = [
            self.steamcmd_path,
            self.klei_path,
            self.dst_path,
            os.path.join(self.dst_path, self.server_name),
            os.path.join(self.dst_path, self.server_name, "Master"),
            os.path.join(self.dst_path, self.server_name, "Caves")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
            
    def download_steamcmd(self):
        """Download and extract SteamCMD"""
        steamcmd_url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
        zip_path = os.path.join(self.steamcmd_path, "steamcmd.zip")
        
        print("Downloading SteamCMD...")
        response = requests.get(steamcmd_url)
        with open(zip_path, 'wb') as f:
            f.write(response.content)
            
        shutil.unpack_archive(zip_path, self.steamcmd_path)
        os.remove(zip_path)
        print("SteamCMD downloaded and extracted")
        
    def create_server_config(self):
        """Create server configuration files"""
        # cluster.ini
        cluster_config = """[GAMEPLAY]
game_mode = survival
max_players = 6
pvp = false
pause_when_empty = true

[NETWORK]
cluster_name = My DST Server
cluster_description = A Don't Starve Together Dedicated Server
cluster_password = 
cluster_intention = cooperative

[MISC]
console_enabled = true

[SHARD]
shard_enabled = true
bind_ip = 127.0.0.1
master_ip = 127.0.0.1
master_port = 10889
cluster_key = defaultkey
"""
        
        # server.ini for Master
        master_config = """[NETWORK]
server_port = 10999

[SHARD]
is_master = true
name = Master
id = 1

[STEAM]
master_server_port = 27018
authentication_port = 8768
"""
        
        # server.ini for Caves
        caves_config = """[NETWORK]
server_port = 10998

[SHARD]
is_master = false
name = Caves
id = 2

[STEAM]
master_server_port = 27019
authentication_port = 8769
"""
        
        # Create the configuration files
        configs = {
            os.path.join(self.dst_path, self.server_name, "cluster.ini"): cluster_config,
            os.path.join(self.dst_path, self.server_name, "Master", "server.ini"): master_config,
            os.path.join(self.dst_path, self.server_name, "Caves", "server.ini"): caves_config
        }
        
        for path, content in configs.items():
            with open(path, 'w') as f:
                f.write(content)
            print(f"Created config file: {path}")
            
    def create_startup_script(self):
        """Create batch file to start the server"""
        batch_content = """@echo off
cd /D "C:\\steamcmd"
steamcmd.exe +login anonymous +app_update 343050 validate +quit
cd /D "C:\\steamcmd\\steamapps\\common\\Don't Starve Together Dedicated Server\\bin64"
start dontstarve_dedicated_server_nullrenderer_x64 -console -cluster MyDediServer -shard Master
start dontstarve_dedicated_server_nullrenderer_x64 -console -cluster MyDediServer -shard Caves
"""
        
        batch_path = os.path.join(self.klei_path, "StartDSTServers.bat")
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        print(f"Created startup script: {batch_path}")
        
    def setup_server(self):
        """Run the complete server setup process"""
        try:
            print("Starting Don't Starve Together server setup...")
            
            self.create_directories()
            self.download_steamcmd()
            self.create_server_config()
            self.create_startup_script()
            
            print("\nServer setup completed successfully!")
            print("\nIMPORTANT: Before starting the server:")
            print("1. Get your cluster_token.txt from Klei Account website")
            print("2. Place it in: " + os.path.join(self.dst_path, self.server_name))
            print("3. Run StartDSTServers.bat to start your server")
            
        except Exception as e:
            print(f"Error during setup: {str(e)}")
            raise

class ServerSetupGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DST Server Setup")
        self.root.geometry("400x300")
        
        # Create and pack widgets
        tk.Label(self.root, text="Don't Starve Together\nServer Setup", font=('Arial', 16)).pack(pady=20)
        
        tk.Button(self.root, text="Start Setup", command=self.run_setup).pack(pady=10)
        tk.Button(self.root, text="Select Installation Directory", command=self.select_directory).pack(pady=10)
        
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=20)
        
    def run_setup(self):
        try:
            server = DSTServerSetup()
            server.setup_server()
            messagebox.showinfo("Success", "Server setup completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Setup failed: {str(e)}")
            
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.status_label.config(text=f"Selected: {directory}")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        app = ServerSetupGUI()
        app.run()
    else:
        server = DSTServerSetup()
        server.setup_server()
