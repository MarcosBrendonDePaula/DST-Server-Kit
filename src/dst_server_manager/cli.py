#!/usr/bin/env python3
import argparse
import json
import sys
from dst_server_manager import ServerManager
from pathlib import Path

def create_parser():
    parser = argparse.ArgumentParser(description='Don\'t Starve Together Server Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize server manager and install SteamCMD')

    # Create server command
    create_parser = subparsers.add_parser('create', help='Create a new server')
    create_parser.add_argument('name', help='Server name')
    create_parser.add_argument('--config', type=str, help='Path to server configuration JSON file')
    create_parser.add_argument('--preset', default='default', 
                             choices=['default', 'endless', 'wilderness'],
                             help='World preset to use')

    # Update server command
    update_parser = subparsers.add_parser('update', help='Update server configuration')
    update_parser.add_argument('name', help='Server name')
    update_parser.add_argument('--config', type=str, help='Path to server configuration JSON file')

    # Delete server command
    delete_parser = subparsers.add_parser('delete', help='Delete a server')
    delete_parser.add_argument('name', help='Server name')

    # Start server command
    start_parser = subparsers.add_parser('start', help='Start a server')
    start_parser.add_argument('name', help='Server name')

    # List servers command
    subparsers.add_parser('list', help='List all servers')

    # Server status command
    status_parser = subparsers.add_parser('status', help='Get server status')
    status_parser.add_argument('name', help='Server name')

    # Set cluster token command
    token_parser = subparsers.add_parser('token', help='Set cluster token')
    token_parser.add_argument('token', help='Cluster token from Klei account')

    # Mod commands
    mod_parser = subparsers.add_parser('mod', help='Mod management commands')
    mod_subparsers = mod_parser.add_subparsers(dest='mod_command', help='Mod commands')

    # Add mod
    mod_add = mod_subparsers.add_parser('add', help='Add a mod to server')
    mod_add.add_argument('server', help='Server name')
    mod_add.add_argument('mod_id', help='Steam Workshop mod ID')
    mod_add.add_argument('--config', type=str, help='Path to mod configuration JSON file')

    # Remove mod
    mod_remove = mod_subparsers.add_parser('remove', help='Remove a mod from server')
    mod_remove.add_argument('server', help='Server name')
    mod_remove.add_argument('mod_id', help='Steam Workshop mod ID')

    # List mods
    mod_list = mod_subparsers.add_parser('list', help='List server mods')
    mod_list.add_argument('server', help='Server name')

    return parser

def load_json_file(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)

def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = ServerManager()

    try:
        if args.command == 'init':
            manager.install_steamcmd()
            print("Server manager initialized and SteamCMD installed")

        elif args.command == 'create':
            settings = {}
            if args.config:
                settings = load_json_file(args.config)
            settings['world_preset'] = args.preset
            manager.create_server(args.name, settings)
            print(f"Server '{args.name}' created successfully")

        elif args.command == 'update':
            if args.config:
                settings = load_json_file(args.config)
                manager.update_server(args.name, settings)
                print(f"Server '{args.name}' updated successfully")
            else:
                print("Error: --config is required for update command")

        elif args.command == 'delete':
            manager.delete_server(args.name)
            print(f"Server '{args.name}' deleted successfully")

        elif args.command == 'start':
            print(f"Starting server '{args.name}'...")
            manager.start_server(args.name)
            print("Server started. Check the opened console windows for server status")

        elif args.command == 'list':
            servers = manager.list_servers()
            if servers:
                print("Available servers:")
                for server in servers:
                    print(f"  - {server}")
            else:
                print("No servers configured")

        elif args.command == 'status':
            status = manager.get_server_status(args.name)
            print(f"\nServer '{args.name}' status:")
            for key, value in status.items():
                print(f"  {key}: {value}")

        elif args.command == 'token':
            manager.set_cluster_token(args.token)
            print("Cluster token set successfully")

        elif args.command == 'mod':
            if args.mod_command == 'add':
                config = {}
                if args.config:
                    config = load_json_file(args.config)
                manager.mod_manager.add_mod(args.server, args.mod_id, config)
                print(f"Mod {args.mod_id} added to server '{args.server}'")

            elif args.mod_command == 'remove':
                manager.mod_manager.remove_mod(args.server, args.mod_id)
                print(f"Mod {args.mod_id} removed from server '{args.server}'")

            elif args.mod_command == 'list':
                mods = manager.mod_manager.get_server_mods(args.server)
                if mods:
                    print(f"\nMods installed on server '{args.server}':")
                    for mod_id in mods:
                        print(f"  - {mod_id}")
                else:
                    print(f"No mods installed on server '{args.server}'")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
