#!/usr/bin/env python3
"""
Example script demonstrating how to use the DST Server Manager programmatically.
This can be useful for automation or integration with other tools.
"""

from dst_server_manager import ServerManager

def main():
    # Initialize the server manager
    manager = ServerManager()
    
    # Install SteamCMD if not already installed
    manager.install_steamcmd()
    
    # Set cluster token (required for server authentication)
    manager.set_cluster_token("YOUR_CLUSTER_TOKEN")
    
    # Create a server with custom settings
    server_settings = {
        "name": "Python Test Server",
        "description": "Created via Python script",
        "game_mode": "survival",
        "max_players": 6,
        "pvp": False,
        "pause_when_empty": True,
        "password": "testpass123",
        "world_preset": "endless",
        "world_overrides": {
            "overworld": {
                "season_start": "autumn",
                "world_size": "huge",
                "branching": "most",
                "resources": "plenty"
            },
            "caves": {
                "world_size": "huge",
                "branching": "most",
                "resources": "plenty"
            }
        }
    }
    
    # Create the server
    manager.create_server("testserver", server_settings)
    
    # Add some popular mods
    # Global Position (Show Player Position)
    manager.mod_manager.add_mod("testserver", "378160973", {
        "ENABLEPINGS": True,
        "SHOWPLAYERICONS": True
    })
    
    # Increased Stack Size
    manager.mod_manager.add_mod("testserver", "374550642", {
        "MAXSTACKSIZE": 99
    })
    
    # Get server status
    status = manager.get_server_status("testserver")
    print("\nServer Status:")
    for key, value in status.items():
        print(f"{key}: {value}")
    
    # List all configured servers
    print("\nConfigured Servers:")
    for server in manager.list_servers():
        print(f"- {server}")
    
    # Start the server
    print("\nStarting server...")
    manager.start_server("testserver")
    print("Server started! Check the opened console windows for server status.")

def cleanup_example():
    """
    Optional cleanup function to remove the test server.
    Uncomment the call at the bottom if you want to use it.
    """
    manager = ServerManager()
    try:
        manager.delete_server("testserver")
        print("Test server deleted successfully")
    except Exception as e:
        print(f"Error deleting server: {e}")

if __name__ == "__main__":
    main()
    # Uncomment the following line to cleanup the test server
    # cleanup_example()
