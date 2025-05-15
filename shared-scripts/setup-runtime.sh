#!/bin/bash
set -e

RUNTIME="$1"

echo "Setting up runtime: $RUNTIME"

# Detect OS
case "$(uname -s)" in
    Linux*)     OS=linux;;
    Darwin*)    OS=macos;;
    CYGWIN*|MINGW*|MSYS*) OS=windows;;
    *)          echo "Unsupported OS"; exit 1;;
esac

# Function to install packages based on OS
install_package() {
    local package=$1
    case "$OS" in
        linux)
            sudo apt-get update
            sudo apt-get install -y "$package"
            ;;
        macos)
            brew install "$package"
            ;;
        windows)
            if [[ "$package" == *"go"* ]]; then
                # Use winget for Go on Windows
                winget install GoLang.Go
            elif [[ "$package" == *"python"* ]]; then
                # Use winget for Python on Windows
                winget install Python.Python.3.10
            else
                # Use chocolatey for other packages
                choco install "$package" -y
            fi
            ;;
    esac
}

case "$RUNTIME" in
  "java-maven")
    echo "Installing Maven..."
    case "$OS" in
        linux)      install_package maven;;
        macos)      install_package maven;;
        windows)    choco install maven -y;;
    esac
    ;;
  "java-gradle-groovy"|"java-gradle-kotlin")
    echo "Installing Gradle..."
    case "$OS" in
        linux)      install_package gradle;;
        macos)      install_package gradle;;
        windows)    choco install gradle -y;;
    esac
    ;;
  "npm")
    echo "Installing npm..."
    case "$OS" in
        linux)      install_package npm;;
        macos)      install_package node;;
        windows)    choco install nodejs -y;;
    esac
    ;;
  "yarn-classic")
    echo "Installing Yarn Classic..."
    npm install -g yarn@1
    ;;
  "yarn-berry")
    echo "Installing Yarn Berry..."
    npm install -g yarn@berry
    ;;
  "pnpm")
    echo "Installing pnpm..."
    npm install -g pnpm
    ;;
  "go-1.20")
    echo "Installing Go 1.20..."
    case "$OS" in
        linux)
            install_package golang-1.20-go
            export PATH="/usr/lib/go-1.20/bin:$PATH"
            ;;
        macos)
            brew install go@1.20
            ;;
        windows)
            winget install GoLang.Go.1.20
            ;;
    esac
    ;;
  "go-latest")
    echo "Installing latest Go..."
    case "$OS" in
        linux)      install_package golang-go;;
        macos)      install_package go;;
        windows)    winget install GoLang.Go;;
    esac
    ;;
  "python-3.10-pip")
    echo "Installing Python 3.10 and pip..."
    case "$OS" in
        linux)      install_package python3.10 python3-pip;;
        macos)      brew install python@3.10;;
        windows)    winget install Python.Python.3.10;;
    esac
    ;;
  "python-3.12-pip")
    echo "Installing Python 3.12 and pip..."
    case "$OS" in
        linux)      install_package python3.12 python3-pip;;
        macos)      brew install python@3.12;;
        windows)    winget install Python.Python.3.12;;
    esac
    ;;
  "none")
    echo "No additional runtime setup required."
    ;;
  *)
    echo "Unknown runtime: $RUNTIME"
    exit 1
    ;;
esac

echo "Runtime setup complete." 