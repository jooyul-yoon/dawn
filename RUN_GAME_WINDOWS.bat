@echo off
setlocal EnableExtensions

rem Always run from the folder that contains this file.
cd /d "%~dp0"

set "VENV_DIR=.venv-windows"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

if exist "%VENV_PYTHON%" goto ensure_game

echo [Dawn Tactics] Looking for Python 3.12 or newer...
call :find_python
if errorlevel 1 goto python_missing

echo [Dawn Tactics] Creating the Windows environment...
%PYTHON_COMMAND% -m venv "%VENV_DIR%"
if errorlevel 1 goto environment_failed

:ensure_game
"%VENV_PYTHON%" -c "import dawn_tactics, pygame" >nul 2>&1
if not errorlevel 1 goto launch_game

echo [Dawn Tactics] Installing the game for the first launch...
echo Internet access may be needed for a minute.
"%VENV_PYTHON%" -m pip install -e .
if errorlevel 1 goto install_failed

:launch_game
echo [Dawn Tactics] Starting game...
"%VENV_PYTHON%" -m dawn_tactics %*
if errorlevel 1 goto game_failed
exit /b 0

:find_python
py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_COMMAND=py -3.12"
    exit /b 0
)

py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_COMMAND=py -3"
    exit /b 0
)

python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_COMMAND=python"
    exit /b 0
)

python3.12 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_COMMAND=python3.12"
    exit /b 0
)

exit /b 1

:python_missing
echo.
echo ERROR: Python 3.12 or newer was not found.
echo Install Python 3.12 from https://www.python.org/downloads/
echo During installation, enable "Add python.exe to PATH".
goto wait_on_error

:environment_failed
echo.
echo ERROR: The Python environment could not be created.
goto wait_on_error

:install_failed
echo.
echo ERROR: The game could not be installed.
echo Check the internet connection, then run this file again.
goto wait_on_error

:game_failed
echo.
echo ERROR: The game stopped because of an error.
echo Read the message above for the variable or file that needs attention.

:wait_on_error
echo.
pause
exit /b 1
