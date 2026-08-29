@echo off
REM SECRET backend - Windows dev launcher
REM Usage: run.bat [--no-migrate] [--check]

cd /d "%~dp0"

if "%1"=="--check" (
  python run.py --check
  goto :eof
)

if "%1"=="--no-migrate" (
  python run.py --no-migrate
  goto :eof
)

python run.py
