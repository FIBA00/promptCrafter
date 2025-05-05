#!/bin/bash

echo "=== PromptCrafter Build Script ==="
echo "Starting build process..."

# Create directories for static assets if they don't exist
mkdir -p static/img

# Check if icon exists, if not create a placeholder note
if [ ! -f static/img/icon.ico ]; then
    echo "Note: No icon found at static/img/icon.ico"
    echo "      You can add your own icon file there before building"
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: No .env file found. Please create one before building."
    exit 1
fi

# Install dependencies
echo "Ensuring all dependencies are installed..."
pip install -r requirements.txt

# Clean previous build
echo "Cleaning previous build..."
rm -rf build dist

# Build using the spec file
echo "Building application with PyInstaller..."
pyinstaller promptcrafter.spec

# Check if build was successful
if [ -f "dist/PromptCrafter" ]; then
    echo ""
    echo "Build completed successfully!"
    echo "Executable can be found at: dist/PromptCrafter"
    echo ""
    echo "Note: The application is configured to run in $(grep -E "^FLASK_ENV=" .env | cut -d= -f2) mode"
    echo "      You can change this in the .env file"
else
    echo "Build failed. Please check the error messages above."
fi 