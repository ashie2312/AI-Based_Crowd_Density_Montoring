# Installation Troubleshooting Guide

## Python 3.13 Compatibility Issues

If you're using Python 3.13 and encountering installation errors, follow these steps:

### Step 1: Update pip and setuptools

```bash
python -m pip install --upgrade pip setuptools wheel
```

### Step 2: Install packages individually (if batch install fails)

If `pip install -r requirements.txt` fails, try installing packages in this order:

```bash
# Core dependencies first
pip install setuptools>=69.0.0 wheel
pip install numpy>=1.26.0
pip install Pillow>=10.1.0
pip install python-dotenv>=1.0.0

# Flask ecosystem
pip install Werkzeug>=3.0.1
pip install Flask>=3.0.0
pip install Flask-CORS>=4.0.0
pip install Flask-SQLAlchemy>=3.1.1
pip install Flask-JWT-Extended>=4.6.0

# Computer vision and AI
pip install opencv-python>=4.8.1.78
pip install ultralytics>=8.1.0

# WebSocket support
pip install python-socketio>=5.10.0
pip install flask-socketio>=5.3.6

# Security
pip install bcrypt>=4.1.2
```

### Step 3: Alternative - Use Python 3.11 or 3.12

If you continue to have issues with Python 3.13, consider using Python 3.11 or 3.12, which have better package compatibility:

1. **Install Python 3.11 or 3.12:**
   - Download from: https://www.python.org/downloads/
   - Or use pyenv: `pyenv install 3.11.9`

2. **Create a new virtual environment:**
   ```bash
   python3.11 -m venv venv
   # or
   python3.12 -m venv venv
   ```

3. **Activate and install:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

### Step 4: If ultralytics installation fails

The ultralytics package might have issues. Try:

```bash
# Install torch first (required by ultralytics)
pip install torch torchvision

# Then install ultralytics
pip install ultralytics
```

### Step 5: Verify installation

After installation, verify all packages:

```bash
python -c "import flask; import ultralytics; import cv2; import numpy; print('All packages installed successfully!')"
```

## Common Errors and Solutions

### Error: `AttributeError: module 'pkgutil' has no attribute 'ImpImporter'`

**Solution:** This is a Python 3.13 compatibility issue. Update setuptools:
```bash
pip install --upgrade setuptools>=69.0.0
```

### Error: `numpy` installation fails

**Solution:** Install numpy with a compatible version:
```bash
pip install numpy>=1.26.0
```

### Error: `ultralytics` installation fails

**Solution:** Install PyTorch first, then ultralytics:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install ultralytics
```

### Error: `opencv-python` installation fails

**Solution:** Try installing the headless version:
```bash
pip install opencv-python-headless
```

## Recommended Python Version

For best compatibility, use **Python 3.11** or **Python 3.12**. These versions have the best package ecosystem support.

## Still Having Issues?

1. Check your Python version: `python --version`
2. Check your pip version: `pip --version`
3. Update pip: `python -m pip install --upgrade pip`
4. Clear pip cache: `pip cache purge`
5. Try installing in a fresh virtual environment
