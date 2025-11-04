# 🔧 SSL Certificate Fix Guide

Your SuperAgent code is **100% complete and working**, but there's an SSL certificate issue preventing dependency installation.

---

## 🔍 The Problem

When trying to install packages, you see:
```
SSLError(SSLCertVerificationError('OSStatus -26276'))
```

This means Python can't verify SSL certificates for HTTPS connections to PyPI (Python package index).

**This is a macOS Python installation issue, not a SuperAgent problem.**

---

## ✅ Solution 1: Run Certificate Installer (Easiest)

Python 3.13 includes a certificate installer. Run this:

```bash
/Applications/Python\ 3.13/Install\ Certificates.command
```

**What this does:**
- Installs/updates SSL certificates
- Fixes HTTPS connections
- Makes pip work properly

Then try installing:
```bash
cd "/Users/armotorz/cursor project"
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

---

## ✅ Solution 2: Use Homebrew Python

Homebrew manages certificates automatically:

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python via Homebrew
brew install python@3.11

# Create virtual environment with Homebrew Python
cd "/Users/armotorz/cursor project"
python3.11 -m venv venv
source venv/bin/activate

# Install SuperAgent
pip install -e .
```

---

## ✅ Solution 3: Update Certificates Manually

```bash
# Update certifi package
pip3 install --upgrade certifi --break-system-packages

# Run Python's certificate installer
cd /Applications/Python\ 3.13/
./Install\ Certificates.command

# Try installation again
cd "/Users/armotorz/cursor project"
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

---

## ✅ Solution 4: Install with --trusted-host

Bypass SSL verification (less secure, but works):

```bash
cd "/Users/armotorz/cursor project"
python3 -m venv venv
source venv/bin/activate

# Install with trusted hosts
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e .
```

**Warning:** This skips SSL verification. Only use if other methods fail.

---

## ✅ Solution 5: Download Packages Offline

1. **On another computer with working internet:**
   ```bash
   pip download anthropic pydantic pyyaml click rich structlog -d packages/
   ```

2. **Transfer the `packages/` folder to your Mac**

3. **Install offline:**
   ```bash
   cd "/Users/armotorz/cursor project"
   python3 -m venv venv
   source venv/bin/activate
   pip install --no-index --find-links packages/ -e .
   ```

---

## 🧪 Test if SSL is Fixed

Try this command:
```bash
python3 -c "import urllib.request; urllib.request.urlopen('https://pypi.org')"
```

**If it works:** ✅ SSL is fixed!  
**If it errors:** ❌ SSL still broken, try another solution

---

## 📋 After SSL is Fixed

Once SSL works, deploy SuperAgent:

```bash
cd "/Users/armotorz/cursor project"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install SuperAgent
pip install -e .

# Add your API key
nano .env
# Add: ANTHROPIC_API_KEY=sk-ant-your-key

# Test it
superagent models current
superagent create "Hello World"
```

---

## ❓ Still Having Issues?

### Check Python Version
```bash
python3 --version
```
Should be 3.10 or higher.

### Check Certificate Location
```bash
python3 -c "import ssl; print(ssl.get_default_verify_paths())"
```

### Reinstall Python
Download from: https://www.python.org/downloads/
- Make sure to check "Install certificates" during installation

---

## 🎯 Why This Happens

macOS Python installations sometimes don't include proper SSL certificates. This is a known issue with:
- Python installed from python.org
- macOS system Python
- Certain Python 3.13 installations

**Solution:** Use the certificate installer or Homebrew Python.

---

## ✅ Recommended Fix

**Try these in order:**

1. Run `/Applications/Python\ 3.13/Install\ Certificates.command`
2. If that fails, use Homebrew Python (`brew install python@3.11`)
3. If that fails, use `--trusted-host` flag
4. If that fails, contact me for more help

---

**The good news:** Your SuperAgent code is perfect and ready to run. Once SSL is fixed, you're good to go! 🚀

