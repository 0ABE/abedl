@echo off
REM Setup script for ABEDL on Windows
REM This script activates the virtual environment and installs ABEDL

echo Activating virtual environment...
call venv\bin\activate.bat

echo.
echo Installing ABEDL in editable mode...
pip install -e .

echo.
echo Setup complete! You can now use the 'abedl' command.
echo Example: abedl download "https://cbn.com/video/flying-house-episode-1"
echo.
echo Note: Remember to activate the virtual environment before using ABEDL:
echo   venv\bin\activate
