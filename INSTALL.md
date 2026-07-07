# Installing Big Mamba

Big Mamba requires Python 3.6 or higher. It works on Windows, macOS, and Linux.

---

## Method 1: pip install (Recommended)

Works on all operating systems. One command.

```bash
pip install big-mamba-lang
```

After installation, the `mamba` command is available globally:

```bash
mamba version
mamba repl
mamba run hello.mamba
```

If `pip` does not work, try:

```bash
python -m pip install big-mamba-lang
```

Or on Linux/macOS:

```bash
pip3 install big-mamba-lang
```

---

## Method 2: Install from source

```bash
git clone https://github.com/redhatsam09/big-mamba.git
cd big-mamba
pip install -e .
```

This installs Big Mamba in development mode. Changes to the source code take effect immediately.

---

## Method 3: Download and run directly

No installation needed. Just download and use `python mamba.py`:

```bash
git clone https://github.com/redhatsam09/big-mamba.git
cd big-mamba
python mamba.py run examples/hello.mamba
python mamba.py repl
```

---

## Prerequisites: Installing Python

Big Mamba needs Python 3.6+. If you do not have Python installed:

### Windows

Open PowerShell or Command Prompt:

```
winget install Python.Python.3
```

Or download from https://python.org/downloads

During installation, check the box "Add Python to PATH".

### macOS

Open Terminal:

```bash
brew install python
```

If you do not have Homebrew, install it first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Linux (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Linux (Fedora / Red Hat)

```bash
sudo dnf install python3 python3-pip
```

### Linux (Arch)

```bash
sudo pacman -S python python-pip
```

### Verify Python Installation

```bash
python --version
```

On Linux/macOS, you may need:

```bash
python3 --version
```

You need version 3.6 or higher.

---

## Quick Installer Scripts

### Windows

Download and double-click `install.bat`, or run in PowerShell:

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/redhatsam09/big-mamba/main/install.bat" -OutFile install.bat
.\install.bat
```

### macOS / Linux

One-line install:

```bash
curl -sSL https://raw.githubusercontent.com/redhatsam09/big-mamba/main/install.sh | bash
```

Or download and run:

```bash
curl -O https://raw.githubusercontent.com/redhatsam09/big-mamba/main/install.sh
chmod +x install.sh
./install.sh
```

---

## Verify Installation

After installing, run these commands to verify:

```bash
mamba version
```

Expected output:

```
Big Mamba v1.0.0
```

Start the REPL:

```bash
mamba repl
```

Run an example:

```bash
mamba run examples/hello.mamba
```

---

## Uninstall

```bash
pip uninstall big-mamba-lang
```

---

## Troubleshooting

### "mamba" command not found

Your Python scripts directory may not be in PATH.

**Windows:** Add `%APPDATA%\Python\Python3X\Scripts` to PATH.

**macOS/Linux:** Add `~/.local/bin` to PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Permission denied

Use `--user` flag:

```bash
pip install --user big-mamba-lang
```

Or on Linux:

```bash
sudo pip install big-mamba-lang
```

### pip not found

```bash
python -m ensurepip --upgrade
python -m pip install big-mamba-lang
```

---

## Platform Support

| Platform | Status | Install Command |
|----------|--------|----------------|
| Windows 10/11 | Supported | `pip install big-mamba-lang` |
| macOS 12+ | Supported | `pip3 install big-mamba-lang` |
| Ubuntu 20.04+ | Supported | `pip3 install big-mamba-lang` |
| Debian 11+ | Supported | `pip3 install big-mamba-lang` |
| Fedora 36+ | Supported | `pip3 install big-mamba-lang` |
| Arch Linux | Supported | `pip install big-mamba-lang` |
| CentOS 8+ | Supported | `pip3 install big-mamba-lang` |
| Alpine Linux | Supported | `pip3 install big-mamba-lang` |
| WSL | Supported | `pip3 install big-mamba-lang` |
| Termux (Android) | Supported | `pip install big-mamba-lang` |
| Raspberry Pi | Supported | `pip3 install big-mamba-lang` |

Any system with Python 3.6+ can run Big Mamba. No external dependencies required.
