@echo off
setlocal enabledelayedexpansion

REM SecureMed-QR: create venv, install requirements, then run app

cd /d "%~dp0\.."

set "PROJECT_DIR=%cd%"
set "VENV_DIR=%PROJECT_DIR%\venv"

echo ------------------------------------------------------------
echo SecureMed-QR setup & run (Windows)
echo Project: %PROJECT_DIR%
echo ------------------------------------------------------------

if not exist "%VENV_DIR%" (
  echo Creating virtual environment at venv...
  python -m venv "%VENV_DIR%"
) else (
  echo Virtual environment already exists.
)

echo Activating venv...
call "%VENV_DIR%\Scripts\activate.bat"

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements...
pip install -r requirements.txt

echo Starting app...
python run.py
endlocal
