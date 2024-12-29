# DSTServerKit

A comprehensive toolkit for managing Don't Starve Together dedicated servers. Easily create, configure, and manage servers with features like mod management, save imports, and server configuration.

## Prerequisites

Before using DSTServerKit, you need to install SteamCMD, which is required for downloading and updating the Don't Starve Together dedicated server.

### Installing SteamCMD

The recommended way to install SteamCMD on Windows is using Chocolatey:

1. First, install Chocolatey if you haven't already. Open PowerShell as Administrator and run:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

2. Install SteamCMD using Chocolatey:
```powershell
choco install steamcmd
```

Alternatively, you can manually install SteamCMD:
1. Create a folder `C:\steamcmd`
2. Download [steamcmd.zip](https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip)
3. Extract the contents to `C:\steamcmd`
4. Run `steamcmd.exe` once to complete installation

### Installing DST Dedicated Server

After installing SteamCMD, you need to install the Don't Starve Together dedicated server. Open Command Prompt and run:

```batch
cd C:\steamcmd
steamcmd +force_install_dir "C:\steamcmd\steamapps\common\Don't Starve Together Dedicated Server" +login anonymous +app_update 343050 validate +quit
```

This will download and install the DST dedicated server. The command breakdown:
- `+force_install_dir`: Specify installation directory
- `+login anonymous`: Log in anonymously (no Steam account needed)
- `+app_update 343050`: Download/update DST dedicated server (343050 is the app ID)
- `validate`: Verify file integrity
- `+quit`: Exit when done

### Getting Your Cluster Token

You'll need a cluster token to run your server. To get one:

1. Open Don't Starve Together on Steam
2. Click on 'Play'
3. Click on 'Hosts'
4. Click on 'Dedicated Servers'
5. Click 'Generate Server Token'
6. Copy the token and paste it into DSTServerKit when creating a new server

The token looks like a long string of random characters. Keep this token safe as you'll need it for each server you create.

## Quick Start Guide

1. Install prerequisites:
   ```powershell
   # Install Chocolatey (PowerShell Admin)
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   
   # Install SteamCMD
   choco install steamcmd
   
   # Install DST Server
   cd C:\steamcmd
   steamcmd +force_install_dir "C:\steamcmd\steamapps\common\Don't Starve Together Dedicated Server" +login anonymous +app_update 343050 validate +quit
   ```

2. Get your cluster token from DST game menu

3. Run DSTServerKit:
   ```batch
   start_gui.bat
   ```

4. Create your first server:
   - Click "+" to create new server
   - Enter server name and settings
   - Paste your cluster token
   - Click "Create Server"

5. Start playing:
   - Click "Start Server"
   - Open DST and connect via Browse Games

## Features

- Create and manage multiple DST servers
- Import/export world saves
- Manage server mods with Steam Workshop integration
- Configure server settings through a user-friendly interface
- Start/stop servers with real-time status monitoring
- Import saves and mods from existing servers

## Installation

### Python Requirements

- Python 3.8 or higher
- pip (Python package installer)

Required packages:
- customtkinter
- requests
- PyYAML
- Pillow

You can check your Python version by running:
```batch
python --version
```

If you need to install Python, download it from [python.org](https://www.python.org/downloads/) and make sure to check "Add Python to PATH" during installation.

## Troubleshooting

### Common Issues

1. **"steamcmd is not recognized"**
   - Make sure SteamCMD is installed correctly
   - Try reinstalling using Chocolatey
   - Check if `C:\steamcmd` is in your system PATH

2. **"Failed to load server config"**
   - Ensure you have write permissions in your Documents folder
   - Try running the application as administrator

3. **"Server won't start"**
   - Verify your cluster token is correct
   - Check if the DST dedicated server is installed properly
   - Make sure no other server is using the same ports

4. **"Mods not loading"**
   - Verify the mod IDs are correct
   - Check if the mods are compatible with your server version
   - Try reinstalling the mods through Steam Workshop

### Getting Help

If you encounter any issues:
1. Check the log file at `dst_server_manager.log`
2. Look for error messages in the console
3. Make sure all prerequisites are installed correctly

### Installing DSTServerKit

1. Clone this repository:
```batch
git clone https://github.com/yourusername/DSTServerKit.git
cd DSTServerKit
```

2. Install dependencies:
```batch
pip install -r requirements.txt
```

## Usage

1. Double-click `start_gui.bat` in the DSTServerKit folder

Or run from command prompt:
```batch
start_gui.bat
```

When first starting the application:
1. Enter your cluster token (see "Getting Your Cluster Token" above)
2. Create a new server using the "+" button
3. Configure server settings and mods
4. Start the server using the "Start Server" button

## Configuration

### Configuration Files

The application stores its configuration in:
- `%USERPROFILE%\Documents\Klei\DoNotStarveTogether\server_config.yml` - Server configurations
- `%USERPROFILE%\Documents\Klei\DoNotStarveTogether\mod_config.json` - Mod settings

### Server Settings

When creating a new server, you can configure:
- Server Name and Description
- Game Mode (Survival, Endless, Wilderness)
- Max Players
- PvP Mode
- World Preset
- Password Protection
- Pause When Empty

### Port Forwarding

To make your server accessible from the internet, you need to forward these ports in your router:

- Server Port (UDP): 10999 (default)
- Steam Port (UDP): 27016
- Authentication Port (UDP): 8768

Steps to forward ports:
1. Access your router's admin panel (usually http://192.168.1.1)
2. Find the port forwarding section
3. Add rules for each port above
4. Point them to your computer's local IP address
5. Save changes and restart your router if required

### World Presets

Available world presets:
- **Default**: Standard DST world settings
- **Endless**: Long seasons, more resources
- **Wilderness**: Random settings, more challenging

You can customize these settings further in the server configuration.

### Managing Mods

To add mods to your server:
1. Go to the "Mods" tab in server settings
2. Enter the mod's Workshop ID (found in the mod's Steam Workshop URL)
3. Click "Add Mod"
4. Enable/disable mods using the checkboxes
5. Configure mod settings if available

You can find mod IDs in the Steam Workshop URL:
```
https://steamcommunity.com/sharedfiles/filedetails/?id=XXXXXXX
                                                      ↑
                                                   Mod ID
```

### Importing Existing Saves

You can import saves from:
- Existing DST dedicated servers
- Local DST game saves
- Other DSTServerKit servers

To import a save:
1. Go to server settings
2. Click "Import Save"
3. Select the source server
4. Click "Import"

The import will copy:
- World save files
- Mod configurations
- World settings

## Development

To set up the development environment:

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
```

### Server Maintenance

#### Backups
Your server saves are stored in:
```
%USERPROFILE%\Documents\Klei\DoNotStarveTogether\[server_name]\save\
```

It's recommended to:
- Make regular backups of this folder
- Back up before installing new mods
- Keep backups of working configurations

#### Updates
To update your DST dedicated server:
1. Stop all running servers
2. Run the update command:
```batch
cd C:\steamcmd
steamcmd +force_install_dir "C:\steamcmd\steamapps\common\Don't Starve Together Dedicated Server" +login anonymous +app_update 343050 validate +quit
```
3. Restart your servers

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests if available
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to new functions/classes
- Update README for significant changes
- Test your changes thoroughly

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to Klei Entertainment for Don't Starve Together
- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
