# Packaging PromptCrafter as a Desktop Application

This guide explains how to package the PromptCrafter Flask application as a standalone desktop application using PyInstaller.

## Prerequisites

- Python 3.7+ installed
- All dependencies installed via `pip install -r requirements.txt`

## Overview

PromptCrafter uses a PyQt wrapper (`pyqt_runner.py`) to embed the Flask web application within a desktop window. PyInstaller is then used to package everything into a standalone executable.

## Development vs Production Mode

The application can run in two modes:

1. **Development Mode** (default): Uses Flask's built-in development server
2. **Production Mode**: Uses Waitress as a production-ready WSGI server

To run in production mode, set the `FLASK_ENV` environment variable:

```bash
export FLASK_ENV=production
```

This setting will be respected both when running the app directly and through the PyQt wrapper.

## Building the Application

### Option 1: Using the Build Script

The simplest way to build the application is by using the provided build script:

```bash
./build.sh
```

This script will:
1. Create necessary directories
2. Check for an application icon
3. Install required dependencies
4. Clean previous builds
5. Run PyInstaller with the proper configuration

### Option 2: Manual Build

If you prefer to build manually:

1. Ensure you have all dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Run PyInstaller with the spec file:
   ```bash
   pyinstaller promptcrafter.spec
   ```

## Customization

### Application Icon

To customize the application icon:
1. Place your icon file at `static/img/icon.ico`
2. The build process will automatically use this icon

### Build Configuration

The PyInstaller configuration is defined in `promptcrafter.spec`. You can modify this file to:
- Add additional data files
- Configure hidden imports
- Change the executable name
- Adjust other packaging parameters

### Production Configuration

For production deployments, you may want to adjust:
- `config.py`: Update production settings like database URI and SECRET_KEY
- `app.py`: Tune Waitress configuration parameters if needed

## Troubleshooting

### Missing Modules

If the packaged application fails with "ModuleNotFoundError", add the missing module to the `hiddenimports` list in the spec file.

### Static Files Not Found

If templates or static files are not found, ensure they're properly included in the `datas` section of the spec file.

### Database Issues

The SQLite database will be packaged with the application. If you need to use a different database, update the configuration accordingly.

## Distribution

After building, the standalone executable will be available in the `dist/` directory. You can distribute this file directly to users.

For macOS or Windows, additional steps may be needed to create proper installers or app bundles. 