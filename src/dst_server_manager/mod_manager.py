import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import requests

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dst_server_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ModManager')

class ModManager:
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or os.path.expanduser("~\\Documents\\Klei\\DoNotStarveTogether")
        self.mod_settings_path = Path(self.base_path) / "mod_config.json"
        self.load_mod_settings()

    def load_mod_settings(self) -> None:
        """Load mod settings from JSON file or create default if not exists"""
        try:
            if self.mod_settings_path.exists():
                with open(self.mod_settings_path, 'r') as f:
                    loaded_settings = json.load(f)
                    
                # Handle migration from old format
                if 'installed_mods' in loaded_settings:
                    logger.info("Migrating from old mod settings format")
                    self.mod_settings = {'servers': {}}
                    
                    # Get list of servers
                    server_list = []
                    if os.path.exists(self.base_path):
                        server_list = [d for d in os.listdir(self.base_path) 
                                     if os.path.isdir(os.path.join(self.base_path, d))]
                    
                    # Copy mods to each server
                    for server in server_list:
                        self.mod_settings['servers'][server] = {}
                        for mod_id, mod_config in loaded_settings['installed_mods'].items():
                            self.mod_settings['servers'][server][mod_id] = mod_config.copy()
                    
                    self.save_mod_settings()
                    logger.info("Mod settings migration complete")
                else:
                    self.mod_settings = loaded_settings
            else:
                self.mod_settings = {'servers': {}}
                self.save_mod_settings()
        except Exception as e:
            logger.error(f"Error loading mod settings: {str(e)}")
            self.mod_settings = {'servers': {}}
            self.save_mod_settings()

    def save_mod_settings(self) -> None:
        """Save mod settings to JSON file"""
        os.makedirs(os.path.dirname(self.mod_settings_path), exist_ok=True)
        with open(self.mod_settings_path, 'w') as f:
            json.dump(self.mod_settings, f, indent=2)

    def add_mod(self, server_name: str, mod_id: Union[str, int], config: Optional[Dict] = None) -> None:
        """Add a mod to a server's configuration"""
        try:
            logger.info(f"Adding mod {mod_id} to server {server_name}")
            mod_id = str(mod_id)
            
            # Initialize server mods if not exists
            if server_name not in self.mod_settings['servers']:
                self.mod_settings['servers'][server_name] = {}
            
            # Add or update mod configuration
            mod_info = self._fetch_mod_info(mod_id)
            self.mod_settings['servers'][server_name][mod_id] = {
                'name': mod_info.get('name', 'Unknown Mod'),
                'version': mod_info.get('version', '1.0'),
                'enabled': True,
                'configuration_options': config or {}
            }
            self.save_mod_settings()
            logger.debug(f"Saved mod settings for {mod_id} in server {server_name}")

            # Create server directories if they don't exist
            server_path = Path(self.base_path) / server_name
            master_path = server_path / "Master"
            caves_path = server_path / "Caves"
            mods_path = server_path / "server_files" / "mods"
            
            logger.debug(f"Creating directories: {master_path}, {caves_path}, {mods_path}")
            os.makedirs(master_path, exist_ok=True)
            os.makedirs(caves_path, exist_ok=True)
            os.makedirs(mods_path, exist_ok=True)

            # Update mod configurations
            self._update_server_modsetup(server_name)
            
            logger.info(f"Successfully added mod {mod_id} to server {server_name}")
        except Exception as e:
            logger.error(f"Error adding mod {mod_id} to server {server_name}: {str(e)}", exc_info=True)
            raise

    def remove_mod(self, server_name: str, mod_id: Union[str, int]) -> None:
        """Remove a mod from a server's configuration"""
        try:
            logger.info(f"Removing mod {mod_id} from server {server_name}")
            mod_id = str(mod_id)
            
            # Remove mod from server settings
            if server_name in self.mod_settings['servers']:
                if mod_id in self.mod_settings['servers'][server_name]:
                    del self.mod_settings['servers'][server_name][mod_id]
                    self.save_mod_settings()
                    logger.debug(f"Removed mod {mod_id} from server {server_name}")
            
            # Update server files
            self._update_server_modsetup(server_name)
            logger.info(f"Successfully removed mod {mod_id} from server {server_name}")
        except Exception as e:
            logger.error(f"Error removing mod {mod_id} from server {server_name}: {str(e)}", exc_info=True)
            raise

    def get_server_mods(self, server_name: str) -> Dict[str, Dict]:
        """Get all mods configured for a server"""
        try:
            if server_name in self.mod_settings['servers']:
                return {
                    mod_id: {
                        'enabled': config.get('enabled', True),
                        'configuration_options': config.get('configuration_options', {})
                    }
                    for mod_id, config in self.mod_settings['servers'][server_name].items()
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting server mods: {str(e)}", exc_info=True)
            return {}

    def update_mod_config(self, server_name: str, mod_id: str, config: Dict) -> None:
        """Update a mod's configuration for a specific server"""
        try:
            mod_id = str(mod_id)
            if server_name in self.mod_settings['servers']:
                if mod_id in self.mod_settings['servers'][server_name]:
                    # Update server-specific mod settings
                    self.mod_settings['servers'][server_name][mod_id].update({
                        'enabled': config.get('enabled', True),
                        'configuration_options': config.get('configuration_options', {})
                    })
                    self.save_mod_settings()
                    
                    # Update server configuration files
                    self._update_server_modsetup(server_name)
        except Exception as e:
            logger.error(f"Error updating mod config: {str(e)}", exc_info=True)
            raise

    def _fetch_mod_info(self, mod_id: str) -> Dict:
        """Fetch mod information from Steam Workshop"""
        try:
            # Steam Workshop API requires POST for GetPublishedFileDetails
            response = requests.post(
                "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/",
                data={
                    "itemcount": "1",
                    "publishedfileids[0]": mod_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and 'publishedfiledetails' in data['response']:
                    mod_details = data['response']['publishedfiledetails'][0]
                    if mod_details.get('result', 0) == 1:  # Success
                        return {
                            'name': mod_details.get('title', f"Mod {mod_id}"),
                            'version': '1.0',
                            'description': mod_details.get('description', '')
                        }
            
            # Fallback to web scraping if API fails
            workshop_url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}"
            response = requests.get(workshop_url)
            if response.status_code == 200:
                # Look for the mod title in the page content
                content = response.text
                import re
                title_match = re.search(r'<div class="workshopItemTitle">([^<]+)</div>', content)
                if title_match:
                    return {
                        'name': title_match.group(1).strip(),
                        'version': '1.0'
                    }
            
            # If all attempts fail, return default
            return {
                'name': f"Mod {mod_id}",
                'version': '1.0'
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch mod info: {e}")
            return {'name': f"Mod {mod_id}", 'version': '1.0'}

    def _update_server_modsetup(self, server_name: str) -> None:
        """Update dedicated_server_mods_setup.lua and modsettings.lua"""
        try:
            logger.info(f"Updating mod setup for server {server_name}")
            server_path = Path(self.base_path) / server_name
            master_path = server_path / "Master"
            caves_path = server_path / "Caves"
            mods_path = server_path / "server_files" / "mods"
            
            # Create directories if they don't exist
            os.makedirs(master_path, exist_ok=True)
            os.makedirs(caves_path, exist_ok=True)
            os.makedirs(mods_path, exist_ok=True)
            
            # Get server's mods
            server_mods = self.mod_settings['servers'].get(server_name, {})
            
            # Create modoverrides.lua content
            modoverrides_content = "return {\n"
            for mod_id, mod_config in server_mods.items():
                if mod_config.get('enabled', True):
                    modoverrides_content += f'  ["workshop-{mod_id}"] = {{ configuration_options = {{\n'
                    for key, value in mod_config.get('configuration_options', {}).items():
                        if isinstance(value, bool):
                            value = str(value).lower()
                        elif isinstance(value, (int, float)):
                            value = str(value)
                        else:
                            value = f'"{value}"'
                        modoverrides_content += f'    {key} = {value},\n'
                    modoverrides_content += "  }, enabled = true },\n"
            modoverrides_content += "}\n"
            
            # Write modoverrides.lua to both Master and Caves directories
            for path in [master_path, caves_path]:
                modoverrides_path = path / "modoverrides.lua"
                with open(modoverrides_path, 'w', newline='\n') as f:
                    f.write(modoverrides_content)
                logger.debug(f"Created modoverrides.lua in {path}")
            
            # Get enabled mods
            enabled_mods = [
                mod_id for mod_id, config in server_mods.items()
                if config.get('enabled', True)
            ]
            
            # Update dedicated_server_mods_setup.lua
            setup_path = mods_path / "dedicated_server_mods_setup.lua"
            setup_content = [
                "--There are two functions that will install mods, ServerModSetup and ServerModCollectionSetup.",
                "--Put the calls to the functions in this file and they will be executed on boot.",
                "",
                "--ServerModSetup takes a string of a specific mod's Workshop id.",
                "--It will download and install the mod to your mod directory on boot.",
                "    --The Workshop id can be found at the end of the url to the mod's Workshop page.",
                "    --Example: http://steamcommunity.com/sharedfiles/filedetails/?id=350811795",
                "    --ServerModSetup(\"350811795\")",
                "",
                "--ServerModCollectionSetup takes a string of a specific mod's Workshop id.",
                "--It will download all the mods in the collection and install them to the mod directory on boot.",
                "    --The Workshop id can be found at the end of the url to the collection's Workshop page.",
                "    --Example: http://steamcommunity.com/sharedfiles/filedetails/?id=379114180",
                "    --ServerModCollectionSetup(\"379114180\")",
                "",
                "-- Mods configured for this server:",
                ""
            ]
            
            # Add mod setup calls
            for mod_id in enabled_mods:
                mod_name = server_mods[mod_id]["name"]
                setup_content.append(f'ServerModSetup("{mod_id}") -- {mod_name}')
            
            # Write setup file
            with open(setup_path, 'w', newline='\n') as f:
                f.write('\n'.join(setup_content))
            
            # Update modsettings.lua
            settings_path = mods_path / "modsettings.lua"
            settings_content = [
                "-- Use the \"ForceEnableMod\" function when developing a mod. This will cause the",
                "-- game to load the mod every time no matter what, saving you the trouble of",
                "-- re-enabling it from the main menu.",
                "--",
                "-- Note! You shout NOT do this for normal mod loading. Please use the Mods menu",
                "-- from the main screen instead.",
                "",
                "--ForceEnableMod(\"kioskmode_dst\")",
                "",
                "-- Use \"EnableModDebugPrint()\" to show extra information during startup.",
                "",
                "EnableModDebugPrint()",
                "",
                "-- Use \"EnableModError()\" to make the game more strict and crash on bad mod practices.",
                "",
                "--EnableModError()",
                "",
                "-- Use \"DisableModDisabling()\" to make the game stop disabling your mods when the game crashes",
                "",
                "--DisableModDisabling()",
                "",
                "-- Use \"DisableLocalModWarning()\" to make the game stop warning you when enabling local mods.",
                "",
                "--DisableLocalModWarning()",
                "",
                "-- Mods configured for this server:",
                "-- Note: These mods will be force-enabled on server startup",
                "",
                "-- Force enable configured mods"
            ]
            
            # Add force enable for each mod
            for mod_id in enabled_mods:
                settings_content.append(f'ForceEnableMod("workshop-{mod_id}")')
            
            # Write settings file
            with open(settings_path, 'w', newline='\n') as f:
                f.write('\n'.join(settings_content))
            
            logger.info(f"Successfully updated mod setup for server {server_name}")
        except Exception as e:
            logger.error(f"Error updating mod setup for server {server_name}: {str(e)}", exc_info=True)
            raise
