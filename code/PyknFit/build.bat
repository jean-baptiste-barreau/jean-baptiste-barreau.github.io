@echo off
REM build.bat - Construit l'exécutable PyknFit sous Windows
cd /d "%~dp0"

echo === Installation des dependances de build ===
python -m pip install --upgrade pip
python -m pip install pyinstaller pillow

echo.
echo === Construction de l'executable ===
python build_exe.py

echo.
echo === Termine. Voir dist\PyknFit.exe ===
pause