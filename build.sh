#!/bin/bash

echo "Starting PromptCrafter build process..."

# Create directories for static assets if they don't exist
mkdir -p static/img

# Check if icon exists, if not create a placeholder
if [ ! -f static/img/icon.ico ]; then
    echo "Note: No icon found at static/img/icon.ico"
    echo "      You can add your own icon file there before building"
fi

# Install dependencies if needed
echo "Ensuring all dependencies are installed..."
pip install -r requirements.txt

# Clean previous build
echo "Cleaning previous build..."
rm -rf build dist

# Build using the spec file
echo "Building application with PyInstaller..."
pyinstaller promptcrafter.spec

echo "Build completed!"
echo "Executable can be found in the dist/ directory" 