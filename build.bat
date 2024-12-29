@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -e .
pip install pyinstaller

echo Creating resources directory...
if not exist "resources" mkdir resources

echo Building executable...
pyinstaller --name dst-server-manager ^
           --onefile ^
           --windowed ^
           --clean ^
           --add-data "venv/Lib/site-packages/customtkinter;customtkinter/" ^
           --hidden-import customtkinter ^
           --hidden-import PIL ^
           --hidden-import tkinter ^
           --hidden-import dst_server_manager.screens.server_list ^
           --hidden-import dst_server_manager.screens.server_create ^
           --hidden-import dst_server_manager.screens.server_config ^
           --hidden-import dst_server_manager.components.settings_tab ^
           --hidden-import dst_server_manager.components.mods_tab ^
           --hidden-import dst_server_manager.components.save_card ^
           --hidden-import dst_server_manager.components.server_card ^
           --hidden-import dst_server_manager.components.import_dialog ^
           --collect-data customtkinter ^
           --collect-data PIL ^
           --paths src ^
           src/dst_server_manager/gui.py

echo.
echo Build complete! The executable can be found in the dist folder.
echo Note: You can copy dst-server-manager.exe anywhere and run it.
echo.
pause
