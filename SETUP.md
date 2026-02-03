# Setup Instructions

## Python Version Compatibility

**IMPORTANT**: This project currently requires **Python 3.11, 3.12, or 3.13**.

Python 3.14 is not yet supported due to `greenlet` (SQLAlchemy dependency) not having pre-built wheels for Python 3.14.

### Check Your Python Version

```bash
python3 --version
```

### Installing the Correct Python Version (if needed)

**On macOS (using Homebrew)**:
```bash
brew install python@3.13
python3.13 -m venv venv
```

**On Ubuntu/Debian**:
```bash
sudo apt install python3.13 python3.13-venv
python3.13 -m venv venv
```

**On Windows**:
Download Python 3.13 from python.org

## Installation Steps

### 1. Create Virtual Environment

```bash
# Using Python 3.13 (or 3.11/3.12)
python3.13 -m venv venv

# Activate virtual environment
source venv/bin/activate          # macOS/Linux
# OR
venv\Scripts\activate              # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser (~300MB) that Playwright will use.

### 4. Configure Environment

```bash
# Copy template
cp .env.example .env

# Set your OpenAI API key
python main.py config set-openai-key sk-your-api-key-here
```

### 5. Verify Installation

```bash
# Should show help
python main.py --help

# Should show empty agent list
python main.py agent list

# Should show config (with warnings about OpenAI key if not set)
python main.py config show
```

## Troubleshooting

### "greenlet" build errors

**Solution**: Use Python 3.11, 3.12, or 3.13 instead of 3.14.

### "playwright not found"

**Solution**:
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall playwright
pip install playwright
playwright install chromium
```

### Database permission errors

**Solution**:
```bash
# Ensure data directory has write permissions
chmod -R 755 data/
```

### Import errors

**Solution**:
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

Once installed, see README.md for usage instructions.

Quick start:
```bash
# Add your first TikTok account
python main.py agent add

# View statistics
python main.py stats
```
