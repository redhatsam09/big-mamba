#!/usr/bin/env bash

set -e

echo ""
echo "  Big Mamba Installer"
echo "  ==================="
echo ""

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON=python3
    elif command -v python &> /dev/null; then
        PYTHON=python
    else
        echo "  Error: Python 3 is not installed."
        echo ""
        echo "  Install Python first:"
        echo ""
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "    brew install python"
        elif command -v apt &> /dev/null; then
            echo "    sudo apt update && sudo apt install python3 python3-pip"
        elif command -v dnf &> /dev/null; then
            echo "    sudo dnf install python3"
        elif command -v pacman &> /dev/null; then
            echo "    sudo pacman -S python"
        else
            echo "    Visit https://python.org/downloads"
        fi
        echo ""
        exit 1
    fi

    VERSION=$($PYTHON --version 2>&1 | cut -d' ' -f2)
    MAJOR=$(echo $VERSION | cut -d. -f1)
    MINOR=$(echo $VERSION | cut -d. -f2)

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 6 ]); then
        echo "  Error: Python 3.6+ is required. Found: $VERSION"
        exit 1
    fi

    echo "  Found Python $VERSION"
}

install_mamba() {
    echo "  Installing Big Mamba..."
    echo ""

    if command -v pip3 &> /dev/null; then
        PIP=pip3
    elif command -v pip &> /dev/null; then
        PIP=pip
    else
        PIP="$PYTHON -m pip"
    fi

    $PIP install big-mamba-lang

    echo ""
    echo "  Big Mamba installed successfully."
    echo ""
    echo "  Quick start:"
    echo "    mamba repl              Start interactive mode"
    echo "    mamba run file.mamba    Run a program"
    echo "    mamba help              Show all commands"
    echo ""
}

check_python
install_mamba
