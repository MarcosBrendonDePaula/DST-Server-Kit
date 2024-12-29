import os
import yaml
import shutil
import logging
import configparser
from pathlib import Path
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger('ConfigManager')

class ConfigManager:
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or os.path.expanduser("~\\Documents\\Klei\\DoNotStarveTogether")
        # Ensure base directory exists
        os.makedirs(self.base_path, exist_ok=True)
        self.config_path = Path(self.base_path) / "server_config.yml"
        self.mod_settings_path = Path(self.base_path) / "mod_config.json"
        # Initialize with default config
        self.config = self.get_default_config()
        # Load existing config if available
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from YAML file and merge with defaults"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f) or {}
                
            # Merge loaded config with defaults
            if loaded_config:
                # Update top-level settings
                self.config['steamcmd_path'] = loaded_config.get('steamcmd_path', self.config['steamcmd_path'])
                self.config['cluster_token'] = loaded_config.get('cluster_token', self.config['cluster_token'])
                
                # Merge server configurations
                if 'servers' in loaded_config:
                    for server_name, server_config in loaded_config['servers'].items():
                        if server_name not in self.config['servers']:
                            # Create new server config based on default
                            self.config['servers'][server_name] = self.get_default_config()['servers']['default'].copy()
                        # Update server config with loaded values
                        self.config['servers'][server_name].update(server_config)
                        
                        # Handle migration of mods from old format
                        if 'mods' in server_config:
                            try:
                                # Initialize mod settings for this server if needed
                                mod_settings = {'servers': {}}
                                if os.path.exists(self.mod_settings_path):
                                    with open(self.mod_settings_path, 'r') as f:
                                        mod_settings = json.load(f)
                                
                                if server_name not in mod_settings['servers']:
                                    mod_settings['servers'][server_name] = {}
                                
                                # Migrate mods to new format
                                for mod_id in server_config['mods']:
                                    if isinstance(mod_id, dict):
                                        # Handle old format with config
                                        mod_settings['servers'][server_name][mod_id['id']] = {
                                            'name': f"Mod {mod_id['id']}",
                                            'version': '1.0',
                                            'enabled': True,
                                            'configuration_options': mod_id.get('config', {})
                                        }
                                    else:
                                        # Handle simple mod ID
                                        mod_settings['servers'][server_name][str(mod_id)] = {
                                            'name': f"Mod {mod_id}",
                                            'version': '1.0',
                                            'enabled': True,
                                            'configuration_options': {}
                                        }
                                
                                # Save updated mod settings
                                with open(self.mod_settings_path, 'w') as f:
                                    json.dump(mod_settings, f, indent=2)
                                
                                # Remove mods from server config as they're now in mod_settings
                                del self.config['servers'][server_name]['mods']
                            except Exception as e:
                                logger.error(f"Failed to migrate mods for server {server_name}: {str(e)}")
            
            # Save merged configuration
            self.save_config()
            
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            # Keep using default config if loading fails
            self.save_config()

    def save_config(self) -> None:
        """Save current configuration to YAML file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)

    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration settings"""
        return {
            'steamcmd_path': "C:\\steamcmd",
            'cluster_token': "",
            'servers': {
                'default': {
                    'name': "My DST Server",
                    'description': "A Don't Starve Together Dedicated Server",
                    'game_mode': "survival",
                    'max_players': 6,
                    'pvp': False,
                    'pause_when_empty': True,
                    'password': "",
                    'server_port': 10999,
                    'master_server_port': 27018,
                    'authentication_port': 8768,
                    'world_overrides': {
                        'overworld': {},
                        'caves': {}
                    }
                }
            }
        }

    def create_server_config(self, server_name: str) -> Dict[str, Any]:
        """Create a new server configuration"""
        if server_name in self.config['servers']:
            raise ValueError(f"Server {server_name} already exists")
        
        try:
            # Create base server config
            default_server = self.get_default_config()['servers']['default'].copy()
            default_server['name'] = server_name  # Set the actual server name
            self.config['servers'][server_name] = default_server
            self.save_config()
            
            # Create server directory structure
            server_path = Path(self.base_path) / server_name
            os.makedirs(server_path, exist_ok=True)
            os.makedirs(server_path / "Master", exist_ok=True)
            os.makedirs(server_path / "Caves", exist_ok=True)
            
            # Create cluster.ini
            self._create_cluster_ini(server_name)
            
            # Create server.ini files
            self._create_server_ini(server_name, "Master")
            self._create_server_ini(server_name, "Caves")
            
            return self.config['servers'][server_name]
            
        except Exception as e:
            # Clean up on failure
            if server_name in self.config['servers']:
                del self.config['servers'][server_name]
                self.save_config()
            
            server_path = Path(self.base_path) / server_name
            if server_path.exists():
                shutil.rmtree(server_path)
            
            raise RuntimeError(f"Failed to create server configuration: {str(e)}")

    def update_server_config(self, server_name: str, settings: Dict[str, Any]) -> None:
        """Update server configuration with new settings"""
        if server_name not in self.config['servers']:
            raise ValueError(f"Server {server_name} does not exist")
        
        # Update internal config
        self.config['servers'][server_name].update(settings)
        self.save_config()
        
        # Update cluster.ini
        self._create_cluster_ini(server_name)

    def _create_cluster_ini(self, server_name: str) -> None:
        """Create or update cluster.ini file"""
        server_config = self.config['servers'][server_name]
        
        # Create INI content manually to ensure exact format
        ini_content = [
            "[GAMEPLAY]",
            f"game_mode = {server_config['game_mode']}",
            f"max_players = {server_config['max_players']}",
            f"pvp = {str(server_config['pvp']).lower()}",
            f"pause_when_empty = {str(server_config['pause_when_empty']).lower()}",
            "",
            "[NETWORK]",
            f"cluster_name = {server_config['name']}",
            f"cluster_description = {server_config['description']}",
            f"cluster_password = {server_config.get('password', '')}",
            "cluster_intention = cooperative",
            "",
            "[MISC]",
            "console_enabled = true",
            "",
            "[SHARD]",
            "shard_enabled = true",
            "bind_ip = 127.0.0.1",
            "master_ip = 127.0.0.1",
            "master_port = 10889",
            "cluster_key = defaultkey"
        ]
        
        # Write to file
        cluster_ini_path = Path(self.base_path) / server_name / "cluster.ini"
        with open(cluster_ini_path, 'w', newline='\n') as f:
            f.write('\n'.join(ini_content))

    def _create_server_ini(self, server_name: str, shard: str) -> None:
        """Create server.ini file for a shard"""
        # Create INI content manually to ensure exact format
        ini_content = [
            "[NETWORK]",
            f"server_port = {self.config['servers'][server_name]['server_port']}",
            "",
            "[SHARD]",
            f"is_master = {str(shard == 'Master').lower()}",
            f"name = {shard.lower()}",
            f"id = {shard.lower()}"
        ]
        
        # Write to file
        server_ini_path = Path(self.base_path) / server_name / shard / "server.ini"
        with open(server_ini_path, 'w', newline='\n') as f:
            f.write('\n'.join(ini_content))

    def delete_server_config(self, server_name: str) -> None:
        """Delete a server configuration"""
        if server_name not in self.config['servers']:
            raise ValueError(f"Server {server_name} does not exist")
        
        del self.config['servers'][server_name]
        self.save_config()

    def get_server_config(self, server_name: str) -> Dict[str, Any]:
        """Get configuration for a specific server"""
        if server_name not in self.config['servers']:
            raise ValueError(f"Server {server_name} does not exist")
        
        return self.config['servers'][server_name]

    def get_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration for all servers"""
        return self.config['servers']

    def set_cluster_token(self, token: str) -> None:
        """Set the cluster token for authentication"""
        self.config['cluster_token'] = token
        self.save_config()

    def get_cluster_token(self) -> str:
        """Get the cluster token"""
        return self.config['cluster_token']
