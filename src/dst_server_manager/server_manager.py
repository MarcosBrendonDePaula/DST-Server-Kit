import os
import re
import shutil
import subprocess
import threading
import queue
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import requests
from .config_manager import ConfigManager
from .world_manager import WorldManager
from .mod_manager import ModManager

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dst_server_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ServerManager')

class ServerManager:
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or os.path.expanduser("~\\Documents\\Klei\\DoNotStarveTogether")
        self.steamcmd_path = "C:\\steamcmd"
        
        # Initialize managers
        self.config_manager = ConfigManager(self.base_path)
        self.world_manager = WorldManager(self.base_path)
        self.mod_manager = ModManager(self.base_path)
        
        # Track running servers and their ports
        self.running_servers: Dict[str, Dict[str, Any]] = {}
        self.used_ports = set()
        
        # Default port ranges
        self.server_port_range = range(10999, 11099)
        self.auth_port_range = range(8766, 8866)
        self.master_port_range = range(27016, 27116)
        
        # Ensure base directories exist
        self._create_base_directories()

    def _create_base_directories(self) -> None:
        """Create necessary base directories"""
        directories = [
            self.steamcmd_path,
            self.base_path
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def install_steamcmd(self, progress_callback: Optional[Callable] = None) -> None:
        """Download and install SteamCMD"""
        if not os.path.exists(os.path.join(self.steamcmd_path, "steamcmd.exe")):
            if progress_callback:
                progress_callback("Downloading SteamCMD...", 0.1)
            
            # Download SteamCMD
            steamcmd_url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
            zip_path = os.path.join(self.steamcmd_path, "steamcmd.zip")
            
            response = requests.get(steamcmd_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    f.write(data)
                    if progress_callback and total_size:
                        progress = 0.1 + (downloaded / total_size) * 0.4
                        progress_callback("Downloading SteamCMD...", progress)
            
            if progress_callback:
                progress_callback("Extracting SteamCMD...", 0.5)
            
            # Extract and cleanup
            try:
                shutil.unpack_archive(zip_path, self.steamcmd_path)
            finally:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
            
            # Run SteamCMD first time to update itself
            if progress_callback:
                progress_callback("Initializing SteamCMD...", 0.7)
            
            steamcmd_exe = os.path.join(self.steamcmd_path, "steamcmd.exe")
            subprocess.run(f'"{steamcmd_exe}" +quit', 
                         shell=True,
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         check=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)
            
            if progress_callback:
                progress_callback("SteamCMD installed", 1.0)

    def _update_server_files(self, progress_callback: Optional[Callable] = None) -> None:
        """Update DST dedicated server files using SteamCMD"""
        try:
            if progress_callback:
                progress_callback("Creating directories...", 0.1)
            
            # Create steamapps directory structure
            steamapps_path = os.path.join(self.steamcmd_path, "steamapps")
            dst_server_path = os.path.join(steamapps_path, "common", "Don't Starve Together Dedicated Server")
            
            # Ensure directories exist
            os.makedirs(steamapps_path, exist_ok=True)
            os.makedirs(dst_server_path, exist_ok=True)
            
            if progress_callback:
                progress_callback("Running SteamCMD...", 0.2)
            
            # Run SteamCMD with proper path escaping
            steamcmd_exe = os.path.join(self.steamcmd_path, "steamcmd.exe")
            
            # Create command string with proper escaping
            cmd = [
                steamcmd_exe,
                "+@ShutdownOnFailedCommand", "0",
                "+@NoPromptForPassword", "1",
                "+force_install_dir", dst_server_path,
                "+login", "anonymous",
                "+app_update", "343050", "validate",
                "+quit"
            ]
            
            # Execute SteamCMD with arguments
            process = subprocess.Popen(
                " ".join(f'"{arg}"' if " " in str(arg) else str(arg) for arg in cmd),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Monitor process output
            current_phase = "Initializing"
            base_progress = 0.2
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    line = line.strip()
                    if progress_callback:
                        # Update phase based on output
                        if "Downloading update" in line:
                            current_phase = "Downloading"
                            progress_callback("Downloading server files...", base_progress)
                        elif "Verifying installation" in line:
                            current_phase = "Verifying"
                            base_progress = 0.7
                            progress_callback("Verifying files...", base_progress)
                        elif "Update state" in line:
                            try:
                                percentage_str = re.search(r'(\d+(?:\.\d+)?)%', line)
                                if percentage_str:
                                    percentage = float(percentage_str.group(1)) / 100
                                    if current_phase == "Downloading":
                                        progress = 0.2 + (percentage * 0.5)  # 20-70%
                                    else:  # Verifying
                                        progress = 0.7 + (percentage * 0.2)  # 70-90%
                                    progress_callback(f"{current_phase}: {line}", progress)
                            except:
                                progress_callback(line, base_progress)
                        elif "Success!" in line:
                            progress_callback("Download complete!", 0.9)
                        elif "error" in line.lower():
                            progress_callback(f"Error: {line}", base_progress)
                            raise RuntimeError(f"SteamCMD error: {line}")
                        else:
                            # Show other important messages
                            progress_callback(line, base_progress)
            
            if process.returncode != 0:
                error = process.stderr.read()
                raise subprocess.CalledProcessError(process.returncode, cmd, stderr=error)
            
            if progress_callback:
                progress_callback("Verifying installation...", 0.9)
            
            # Check if server files exist after installation
            server_exe = os.path.join(dst_server_path, "bin64", 
                                    "dontstarve_dedicated_server_nullrenderer_x64.exe")
            if not os.path.exists(server_exe):
                raise RuntimeError(f"Server executable not found at {server_exe}")
            
            if progress_callback:
                progress_callback("Server files updated successfully", 1.0)
                
        except subprocess.CalledProcessError as e:
            error_msg = f"SteamCMD failed: {e.stderr if e.stderr else str(e)}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Failed to update server files: {str(e)}")

    def create_server(self, server_name: str, settings: Dict[str, Any], progress_callback: Optional[Callable] = None) -> None:
        """Create a new DST dedicated server"""
        try:
            if progress_callback:
                progress_callback("Creating server directories...", 0.1)
            
            # Create server directory structure
            server_path = Path(self.base_path) / server_name
            
            # Create main directories
            os.makedirs(server_path, exist_ok=True)
            os.makedirs(server_path / "Master", exist_ok=True)
            os.makedirs(server_path / "Caves", exist_ok=True)
            
            if progress_callback:
                progress_callback("Creating server configuration...", 0.2)
            
            # Create server configuration first
            self.config_manager.create_server_config(server_name)
            self.config_manager.update_server_config(server_name, settings)
            
            # Create world configuration using specified preset or default
            preset = settings.get('world_preset', 'default')
            world_overrides = settings.get('world_overrides')
            self.world_manager.create_world_config(server_name, preset, world_overrides)
            
            # Create server files directory later to avoid issues with copying
            server_dst_path = server_path / "server_files"
            if os.path.exists(server_dst_path):
                shutil.rmtree(server_dst_path)
            
            if progress_callback:
                progress_callback("Installing SteamCMD...", 0.3)
            
            # Install/update DST server files if needed
            self.install_steamcmd(lambda msg, prog: progress_callback(msg, 0.3 + prog * 0.2))
            
            if progress_callback:
                progress_callback("Updating server files...", 0.5)
            
            self._update_server_files(lambda msg, prog: progress_callback(msg, 0.5 + prog * 0.3))
            
            if progress_callback:
                progress_callback("Copying server files...", 0.8)
            
            # Copy DST server files to server-specific directory
            dst_server_path = os.path.join(self.steamcmd_path, 
                                         "steamapps", 
                                         "common", 
                                         "Don't Starve Together Dedicated Server")
            
            # Ensure server files directory exists
            server_dst_path = os.path.join(self.base_path, server_name, "server_files")
            os.makedirs(server_dst_path, exist_ok=True)
            
            # Copy server files
            if progress_callback:
                progress_callback("Copying server files...", 0.8)
            
            if os.path.exists(server_dst_path):
                shutil.rmtree(server_dst_path)
            shutil.copytree(dst_server_path, server_dst_path)
            
            if progress_callback:
                progress_callback("Finalizing setup...", 0.9)
            
            # Install mods if specified
            if 'mods' in settings:
                if progress_callback:
                    progress_callback("Setting up mods...", 0.95)
                
                # Create mods directory in server_files
                server_files_path = os.path.join(self.base_path, server_name, "server_files")
                mods_path = os.path.join(server_files_path, "mods")
                os.makedirs(mods_path, exist_ok=True)
                
                # Create empty mod files if they don't exist
                setup_path = os.path.join(mods_path, "dedicated_server_mods_setup.lua")
                settings_path = os.path.join(mods_path, "modsettings.lua")
                
                if not os.path.exists(setup_path):
                    with open(setup_path, 'w', newline='\n') as f:
                        f.write("-- Generated by DST Server Manager\n")
                
                if not os.path.exists(settings_path):
                    with open(settings_path, 'w', newline='\n') as f:
                        f.write("-- Generated by DST Server Manager\n")
                
                # Add each mod through the mod manager
                for mod_id, mod_config in settings['mods'].items():
                    self.mod_manager.add_mod(server_name, mod_id, mod_config)
            
            # Create startup script
            self._create_startup_script(server_name)
            
            if progress_callback:
                progress_callback("Server created successfully!", 1.0)
            
        except Exception as e:
            print(e)
            # Clean up on failure
            if os.path.exists(server_path):
                shutil.rmtree(server_path)
            raise RuntimeError(f"Failed to create server: {str(e)}")

    def update_server_config(self, server_name: str, settings: Dict[str, Any]) -> None:
        """Update server configuration"""
        self.config_manager.update_server_config(server_name, settings)

    def delete_server(self, server_name: str) -> None:
        """Delete a server and all its files"""
        try:
            # Stop server if running
            if server_name in self.running_servers:
                self.stop_server(server_name)
            
            # Delete server files
            server_path = Path(self.base_path) / server_name
            if server_path.exists():
                shutil.rmtree(server_path)
            
            # Remove server from mod settings
            if server_name in self.mod_manager.mod_settings.get('servers', {}):
                del self.mod_manager.mod_settings['servers'][server_name]
                self.mod_manager.save_mod_settings()
            
            # Delete server config
            self.config_manager.delete_server_config(server_name)
            
            logger.info(f"Successfully deleted server {server_name}")
        except Exception as e:
            logger.error(f"Error deleting server {server_name}: {str(e)}")
            raise

    def start_server(self, server_name: str, console_callbacks: Optional[Dict] = None) -> bool:
        """
        Start a DST dedicated server
        
        Args:
            server_name: Name of the server to start
            console_callbacks: Optional dictionary with 'master' and 'caves' callback functions
                             to receive console output
        """
        try:
            # Get server config
            config = self.config_manager.get_server_config(server_name)
        except Exception as e:
            logger.error(f"Failed to get server config: {str(e)}")
            config = {}
        
        # Get server-specific DST path
        server_dst_path = os.path.join(self.base_path, server_name, "server_files")
        dst_server_path = os.path.join(server_dst_path, "bin64")
        
        # Verify server executable exists
        server_exe = os.path.join(dst_server_path, "dontstarve_dedicated_server_nullrenderer_x64.exe")
        if not os.path.exists(server_exe):
            raise RuntimeError(f"Server executable not found at {server_exe}")
        
        # Start both Master and Caves shards in separate command prompts
        processes = []
        for shard in ["Master", "Caves"]:
            # Build command with proper path escaping
            cmd = f'start "DST {server_name} {shard}" cmd /k "cd /d "{dst_server_path}" && "{server_exe}" -console -cluster "{server_name}" -shard {shard}"'
            
            # Start the process
            process = subprocess.Popen(
                cmd,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            processes.append(process)
        
        # Store running server info
        self.running_servers[server_name] = {
            'processes': processes,
            'start_time': time.time(),
            'status': 'running'
        }
        
        return True

    def stop_server(self, server_name: str) -> bool:
        """Stop a running server"""
        if server_name not in self.running_servers:
            return False
            
        server_info = self.running_servers[server_name]
        
        # Release used ports
        if 'ports' in server_info:
            self.used_ports.difference_update(server_info['ports'])
        
        # Stop processes
        for process in server_info['processes']:
            try:
                process.terminate()
                process.wait(timeout=5)  # Wait for process to terminate
            except:
                try:
                    process.kill()  # Force kill if terminate fails
                except:
                    pass
        
        del self.running_servers[server_name]
        return True

    def get_server_status(self, server_name: str) -> Dict[str, Any]:
        """Get current status of a server"""
        try:
            config = self.config_manager.get_server_config(server_name)
            mods = self.mod_manager.get_server_mods(server_name)
            
            status = {
                'name': config.get('name', server_name),
                'description': config.get('description', ''),
                'max_players': config.get('max_players', 6),
                'game_mode': config.get('game_mode', 'survival'),
                'mods': list(mods.keys()),
                'world_preset': config.get('world_preset', 'default'),
                'running': False,
                'uptime': None
            }
        except Exception as e:
            logger.error(f"Error getting server status for {server_name}: {str(e)}")
            status = {
                'name': server_name,
                'description': 'Error loading configuration',
                'max_players': 6,
                'game_mode': 'survival',
                'mods': [],
                'world_preset': 'default',
                'running': False,
                'uptime': None
            }
        
        # Add running status if server is active
        if server_name in self.running_servers:
            server_info = self.running_servers[server_name]
            status['running'] = True
            status['uptime'] = time.time() - server_info['start_time']
            
            # Check if processes are still running
            all_running = all(p.poll() is None for p in server_info['processes'])
            if not all_running:
                status['running'] = False
                del self.running_servers[server_name]
        
        return status

    def get_running_servers(self) -> List[str]:
        """Get list of currently running servers"""
        # Update and clean up running servers list
        for server_name in list(self.running_servers.keys()):
            if not all(p.poll() is None for p in self.running_servers[server_name]['processes']):
                del self.running_servers[server_name]
        
        return list(self.running_servers.keys())

    def list_servers(self) -> List[str]:
        """Get list of all configured servers"""
        return list(self.config_manager.get_all_servers().keys())

    def set_cluster_token(self, token: str) -> None:
        """Set the cluster token for server authentication"""
        self.config_manager.set_cluster_token(token)
        
        # Create cluster_token.txt for each server
        for server_name in self.list_servers():
            token_path = Path(self.base_path) / server_name / "cluster_token.txt"
            with open(token_path, 'w') as f:
                f.write(token)

    def _create_startup_script(self, server_name: str) -> None:
        """Create batch scripts to start, stop, and update the server"""
        server_dst_path = os.path.join(self.base_path, server_name, "server_files")
        
        # Create start script
        start_content = f"""@echo off
title DST Server - {server_name}
echo Starting Don't Starve Together server: {server_name}
echo ===============================================

cd /D "{server_dst_path}\\bin64"

echo Starting Master shard...
start "DST {server_name} Master" /min cmd /c dontstarve_dedicated_server_nullrenderer_x64.exe -console -cluster {server_name} -shard Master
timeout /t 5

echo Starting Caves shard...
start "DST {server_name} Caves" /min cmd /c dontstarve_dedicated_server_nullrenderer_x64.exe -console -cluster {server_name} -shard Caves

echo Server started! Check the opened console windows for details.
echo To stop the server, run stop_server.bat
pause
"""
        
        # Create stop script
        stop_content = f"""@echo off
title DST Server Stop - {server_name}
echo Stopping Don't Starve Together server: {server_name}
echo ===============================================

taskkill /FI "WINDOWTITLE eq DST {server_name} Master*" /T /F
taskkill /FI "WINDOWTITLE eq DST {server_name} Caves*" /T /F

echo Server stopped!
timeout /t 3
"""

        # Create update script
        update_content = f"""@echo off
title DST Server Update - {server_name}
echo Updating Don't Starve Together server: {server_name}
echo ===============================================

echo Stopping server if running...
call stop_server.bat

echo Updating server files...
cd /D "C:\\steamcmd"
steamcmd.exe +login anonymous +force_install_dir "{server_dst_path}" +app_update 343050 validate +quit

echo Server updated!
echo You can now start the server using start_server.bat
pause
"""
        
        # Write start script
        start_path = Path(self.base_path) / server_name / "start_server.bat"
        with open(start_path, 'w', newline='\n') as f:
            f.write(start_content)
            
        # Write stop script
        stop_path = Path(self.base_path) / server_name / "stop_server.bat"
        with open(stop_path, 'w', newline='\n') as f:
            f.write(stop_content)
            
        # Write update script
        update_path = Path(self.base_path) / server_name / "update_server.bat"
        with open(update_path, 'w', newline='\n') as f:
            f.write(update_content)
