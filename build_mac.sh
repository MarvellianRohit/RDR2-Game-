#!/bin/bash

# Crimson Trails - macOS Build Script
# Targets: ARM64 (Apple Silicon)

echo "--- Starting Crimson Trails Build Pipeline ---"

# 1. Check for PyInstaller
if ! command -v pyinstaller &> /dev/null
then
    echo "[Build] PyInstaller not found. Installing via pip3..."
    pip3 install pyinstaller
fi

# 2. Compile C Core
echo "[Build] Cleaning and Compiling C Core (ARM64)..."
make clean
make

if [ ! -f "libengine.dylib" ]; then
    echo "[Error] libengine.dylib failed to compile. Aborting."
    exit 1
fi

# 3. Create Standalone Bundle
echo "[Build] Packaging application with PyInstaller..."
# We use python3 -m PyInstaller to avoid PATH issues
python3 -m PyInstaller --noconsole --onefile \
    --add-data "libengine.dylib:." \
    --add-data "assets:assets" \
    --add-data "saves:saves" \
    --add-data "src:src" \
    -n "CrimsonTrails" \
    main.py

# 4. Success Message
if [ $? -eq 0 ]; then
    echo "--------------------------------------------"
    echo "BUILD COMPLETE: dist/CrimsonTrails"
    echo "--------------------------------------------"
else
    echo "[Error] Build pipeline failed."
    exit 1
fi
