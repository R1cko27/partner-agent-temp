@echo off
rem Launcher for the project venv.
rem chcp 65001 is required: without it the venv redirector fails on a
rem non-ASCII base interpreter path (C:\Users\<user>\...).
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if not exist ".venv\Scripts\python.exe" goto :novenv
".venv\Scripts\python.exe" %*
exit /b %ERRORLEVEL%
:novenv
echo [!] venv not found. Create it: python -m venv .venv
exit /b 1
