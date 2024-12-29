@echo off
if exist "dist\dst-server-manager.exe" (
    echo Starting DST Server Manager...
    start "" "dist\dst-server-manager.exe"
) else (
    echo Error: Executable not found!
    echo Please run build.bat first to create the executable.
    pause
)
