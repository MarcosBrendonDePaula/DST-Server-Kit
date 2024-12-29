import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

class WorldManager:
    WORLD_PRESETS = {
        "default": {
            "overworld": {
                "location": "forest",
                "season_start": "default",
                "world_size": "default",
                "branching": "default",
                "loop": "default",
                "specialevent": "default",
                "autumn": "default",
                "winter": "default",
                "spring": "default",
                "summer": "default",
                "day": "default",
                "resources": "default",
                "unpredictable": "default"
            },
            "caves": {
                "location": "caves",
                "season_start": "default",
                "world_size": "default",
                "branching": "default",
                "loop": "default",
                "specialevent": "default",
                "day": "default",
                "resources": "default",
                "unpredictable": "default"
            }
        },
        "endless": {
            "overworld": {
                "location": "forest",
                "season_start": "autumn",
                "world_size": "huge",
                "branching": "most",
                "loop": "default",
                "specialevent": "default",
                "autumn": "very_long",
                "winter": "very_long",
                "spring": "very_long",
                "summer": "very_long",
                "day": "long",
                "resources": "plenty",
                "unpredictable": "never"
            },
            "caves": {
                "location": "caves",
                "season_start": "autumn",
                "world_size": "huge",
                "branching": "most",
                "loop": "default",
                "specialevent": "default",
                "day": "long",
                "resources": "plenty",
                "unpredictable": "never"
            }
        },
        "wilderness": {
            "overworld": {
                "location": "forest",
                "season_start": "autumn",
                "world_size": "default",
                "branching": "random",
                "loop": "never",
                "specialevent": "often",
                "autumn": "random",
                "winter": "random",
                "spring": "random",
                "summer": "random",
                "day": "default",
                "resources": "default",
                "unpredictable": "always"
            },
            "caves": {
                "location": "caves",
                "season_start": "autumn",
                "world_size": "default",
                "branching": "random",
                "loop": "never",
                "specialevent": "often",
                "day": "default",
                "resources": "default",
                "unpredictable": "always"
            }
        }
    }

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or os.path.expanduser("~\\Documents\\Klei\\DoNotStarveTogether")

    def create_world_config(self, server_name: str, preset: str = "default", overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create world configuration files for a server using a preset and optional overrides"""
        if preset not in self.WORLD_PRESETS:
            raise ValueError(f"Invalid preset: {preset}")

        # Deep copy the preset config to avoid modifying the original
        config = {
            world_type: {k: v for k, v in settings.items()}
            for world_type, settings in self.WORLD_PRESETS[preset].items()
        }

        # Apply any overrides
        if overrides:
            for world_type in ['overworld', 'caves']:
                if world_type in overrides:
                    config[world_type].update(overrides[world_type])

        server_path = Path(self.base_path) / server_name
        
        try:
            # Create worldgenoverride.lua for both overworld and caves
            for world_type in ['overworld', 'caves']:
                world_settings = config[world_type]
                shard_name = "Master" if world_type == "overworld" else "Caves"
                
                world_path = server_path / shard_name
                os.makedirs(world_path, exist_ok=True)
                
                self._create_worldgenoverride(world_path, world_settings)
        except Exception as e:
            raise RuntimeError(f"Failed to create world configuration: {str(e)}")

        return config

    def _create_worldgenoverride(self, path: Path, settings: Dict[str, Any]) -> None:
        """Create worldgenoverride.lua file with specified settings"""
        try:
            lua_content = "return {\n"
            lua_content += '  override_enabled = true,\n'
            lua_content += '  preset = "CUSTOM",\n'
            lua_content += '  overrides = {\n'
            
            for key, value in settings.items():
                if isinstance(value, bool):
                    value = str(value).lower()
                elif isinstance(value, (int, float)):
                    value = str(value)
                else:
                    value = f'"{value}"'
                lua_content += f'    {key} = {value},\n'
            
            lua_content += '  },\n'
            lua_content += '}\n'

            with open(path / "worldgenoverride.lua", 'w', newline='\n') as f:
                f.write(lua_content)
        except Exception as e:
            raise RuntimeError(f"Failed to create worldgenoverride.lua: {str(e)}")

    def get_available_presets(self) -> List[str]:
        """Get list of available world presets"""
        return list(self.WORLD_PRESETS.keys())

    def get_preset_settings(self, preset: str) -> Dict[str, Any]:
        """Get settings for a specific preset"""
        if preset not in self.WORLD_PRESETS:
            raise ValueError(f"Invalid preset: {preset}")
        return {
            world_type: {k: v for k, v in settings.items()}
            for world_type, settings in self.WORLD_PRESETS[preset].items()
        }

    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate world generation settings"""
        required_worlds = ['overworld', 'caves']
        if not all(world in settings for world in required_worlds):
            return False

        # Add more validation as needed
        return True

    def import_save(self, source_server: str, target_server: str) -> None:
        """Import save files from one server to another"""
        # Handle cluster-based paths
        if "/" in source_server:
            base_dir, cluster = source_server.split("/", 1)
            source_path = Path(self.base_path) / base_dir / cluster
        else:
            source_path = Path(self.base_path) / source_server

        target_path = Path(self.base_path) / target_server

        if not source_path.exists():
            raise ValueError(f"Source server '{source_server}' not found")
        
        # Ensure target server exists and has proper structure
        os.makedirs(target_path, exist_ok=True)
        os.makedirs(target_path / "Master", exist_ok=True)
        os.makedirs(target_path / "Caves", exist_ok=True)

        try:
            # Copy save files from Master (overworld)
            source_master = source_path / "Master"
            target_master = target_path / "Master"
            if source_master.exists():
                # Copy save files
                save_files = list(source_master.glob("save/*"))
                if save_files:
                    os.makedirs(target_master / "save", exist_ok=True)
                    for file in save_files:
                        target_file = target_master / "save" / file.name
                        if file.is_file():
                            with open(file, 'rb') as src, open(target_file, 'wb') as dst:
                                dst.write(src.read())
                
                # Copy modoverrides.lua if exists
                source_modoverrides = source_master / "modoverrides.lua"
                if source_modoverrides.exists():
                    target_modoverrides = target_master / "modoverrides.lua"
                    with open(source_modoverrides, 'r') as src, open(target_modoverrides, 'w') as dst:
                        dst.write(src.read())

            # Copy save files from Caves
            source_caves = source_path / "Caves"
            target_caves = target_path / "Caves"
            if source_caves.exists():
                # Copy save files
                save_files = list(source_caves.glob("save/*"))
                if save_files:
                    os.makedirs(target_caves / "save", exist_ok=True)
                    for file in save_files:
                        target_file = target_caves / "save" / file.name
                        if file.is_file():
                            with open(file, 'rb') as src, open(target_file, 'wb') as dst:
                                dst.write(src.read())
                
                # Copy modoverrides.lua if exists
                source_modoverrides = source_caves / "modoverrides.lua"
                if source_modoverrides.exists():
                    target_modoverrides = target_caves / "modoverrides.lua"
                    with open(source_modoverrides, 'r') as src, open(target_modoverrides, 'w') as dst:
                        dst.write(src.read())
        except Exception as e:
            raise RuntimeError(f"Failed to import save files: {str(e)}")

    def get_save_details(self, server_name: str, base_path: Optional[Path] = None) -> Dict[str, Any]:
        """Get detailed information about a server's save files"""
        if base_path is None:
            server_path = Path(self.base_path) / server_name
        else:
            server_path = base_path
            
        master_save = server_path / "Master" / "save"
        caves_save = server_path / "Caves" / "save"
        
        save_info = {
            "name": server_name,
            "master": None,
            "caves": None,
            "last_save": None
        }
        
        try:
            # Get Master (overworld) save details
            if master_save.exists():
                master_info = {}
                server_txt = master_save / "server.txt"
                session_txt = master_save / "session.txt"
                
                if server_txt.exists():
                    master_info["last_save"] = server_txt.stat().st_mtime
                    save_info["last_save"] = server_txt.stat().st_mtime
                    # Try to read basic info from server.txt
                    try:
                        with open(server_txt, 'r') as f:
                            content = f.read()
                            if "season" in content.lower():
                                master_info["season"] = content.lower().split("season")[1].split()[0]
                            if "day" in content.lower():
                                master_info["day"] = content.lower().split("day")[1].split()[0]
                    except:
                        pass
                
                if session_txt.exists():
                    try:
                        with open(session_txt, 'r') as f:
                            content = f.read()
                            if "tick" in content.lower():
                                master_info["playtime"] = int(content.lower().split("tick")[1].split()[0]) / 60  # Convert to minutes
                    except:
                        pass
                
                save_info["master"] = master_info
            
            # Get Caves save details
            if caves_save.exists():
                caves_info = {}
                server_txt = caves_save / "server.txt"
                session_txt = caves_save / "session.txt"
                
                if server_txt.exists():
                    caves_info["last_save"] = server_txt.stat().st_mtime
                    if not save_info["last_save"] or server_txt.stat().st_mtime > save_info["last_save"]:
                        save_info["last_save"] = server_txt.stat().st_mtime
                
                if session_txt.exists():
                    try:
                        with open(session_txt, 'r') as f:
                            content = f.read()
                            if "tick" in content.lower():
                                caves_info["playtime"] = int(content.lower().split("tick")[1].split()[0]) / 60  # Convert to minutes
                    except:
                        pass
                
                save_info["caves"] = caves_info
        except Exception as e:
            print(f"Error getting save details: {str(e)}")
            
        return save_info

    def list_servers_with_saves(self) -> List[Dict[str, Any]]:
        """List all servers that have save files with detailed information"""
        servers = []
        base_path = Path(self.base_path)
        
        if base_path.exists():
            try:
                # First check direct server directories
                for server_dir in base_path.iterdir():
                    if server_dir.is_dir():
                        # Check for direct server structure
                        master_save = server_dir / "Master" / "save"
                        caves_save = server_dir / "Caves" / "save"
                        
                        if master_save.exists() or caves_save.exists():
                            save_info = self.get_save_details(server_dir.name)
                            if save_info.get("last_save") is None:
                                save_info["last_save"] = 0
                            servers.append(save_info)
                        
                        # Check for cluster-based structure
                        for cluster_dir in server_dir.glob("Cluster_*"):
                            if cluster_dir.is_dir():
                                cluster_master = cluster_dir / "Master" / "save"
                                cluster_caves = cluster_dir / "Caves" / "save"
                                
                                if cluster_master.exists() or cluster_caves.exists():
                                    # Get mods from modoverrides.lua if exists
                                    mods = {}
                                    modoverrides_path = cluster_dir / "Master" / "modoverrides.lua"
                                    if modoverrides_path.exists():
                                        try:
                                            with open(modoverrides_path, 'r') as f:
                                                content = f.read()
                                                # Extract mod IDs using regex
                                                import re
                                                mod_matches = re.findall(r'\["workshop-(\d+)"\]', content)
                                                mods = {mod_id: True for mod_id in mod_matches}
                                        except:
                                            pass
                                    
                                    save_info = self.get_save_details(
                                        f"{server_dir.name}/{cluster_dir.name}",
                                        base_path=cluster_dir
                                    )
                                    save_info["mods"] = mods
                                    if save_info.get("last_save") is None:
                                        save_info["last_save"] = 0
                                    servers.append(save_info)
            except Exception as e:
                print(f"Error listing servers with saves: {str(e)}")
        
        return sorted(servers, key=lambda x: x.get("last_save", 0) or 0, reverse=True)
