@echo off
echo Cleaning up previous builds...
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
if exist "src\dst_server_manager.egg-info" rd /s /q "src\dst_server_manager.egg-info"

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing build requirements...
python -m pip install --upgrade pip
python -m pip install --upgrade build
python -m pip install --upgrade twine

echo Building distribution...
python -m build

echo.
echo Distribution files created in dist/
echo.
echo To publish to PyPI, run:
echo python -m twine upload dist/*
echo.
echo To publish to Test PyPI first, run:
echo python -m twine upload --repository testpypi dist/*
echo.
echo Note: You will need your PyPI credentials.
echo You can create a PyPI account at: https://pypi.org/account/register/
echo.
pause

:PROMPT
SET /P AREYOUSURE=Do you want to publish to PyPI now (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO END

echo Publishing to PyPI...
python -m twine upload dist/*

:END
echo.
echo Done!
pause
