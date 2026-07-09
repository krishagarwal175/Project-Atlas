@echo off
REM Zero-build launcher — double-click to run Atlas without compiling an .exe.
REM Uses your installed Python. Same result as the built Atlas.exe.
cd /d "%~dp0.."
python desktop\atlas.py
