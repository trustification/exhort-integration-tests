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
    local packages=("$@")
    case "$OS" in
        linux)
            sudo apt-get update
            sudo apt-get install -y "${packages[@]}"
            ;;
        macos)
            brew install "${packages[@]}"
            ;;
        windows)
            for package in "${packages[@]}"; do
                if [[ "$package" == *"go"* ]]; then
                    # Use chocolatey for Go on Windows
                    choco install golang --version=1.20.14 -y
                elif [[ "$package" == *"python"* ]]; then
                    # Use chocolatey for Python on Windows
                    choco install python --version=3.10 -y
                else
                    # Use chocolatey for other packages
                    choco install "$package" -y
                fi
            done
            ;;
    esac
}

case "$RUNTIME" in
  "maven")
    echo "Installing Maven..."
    case "$OS" in
        linux)      install_package maven;;
        macos)      install_package maven;;
        windows)    choco install maven -y;;
    esac
    echo "Installed Maven version:"
    mvn -v
    ;;
  "gradle-groovy"|"gradle-kotlin")
    echo "Installing Gradle..."
    case "$OS" in
        linux)      install_package gradle;;
        macos)      install_package gradle;;
        windows)    choco install gradle -y;;
    esac
    echo "Installed Gradle version:"
    gradle -v
    ;;
  "npm")
    echo "Installing npm..."
    case "$OS" in
        linux)      install_package npm;;
        macos)      install_package node;;
        windows)    choco install nodejs -y;;
    esac
    echo "Installed npm version:" 
    npm -v
    echo "Installed node version:"
    node -v
    ;;
  "yarn-classic")
    echo "Installing Yarn Classic..."
    npm install -g yarn@1
    echo "Installed yarn version:"
    yarn -v
    ;;
  "yarn-berry")
    echo "Installing Yarn Berry..."
    corepack enable
    corepack prepare yarn@stable --activate
    echo "Installed yarn version:"
    yarn -v
    ;;
  "pnpm")
    echo "Installing pnpm..."
    npm install -g pnpm
    echo "Installed pnpm version:"
    pnpm -v
    ;;
  "go-1.20")
    echo "Installing Go 1.20..."
    install_package golang-go
    # Install specific version if needed
    go install "golang.org/dl/go1.20.14@latest"
    "go1.20.14" download
    ;;
  "go-latest")
    echo "Installing latest Go..."
    install_package golang-go
    echo "Installed Go version:"
    go version
    ;;
  "python-3.10-pip")
    echo "Installing Python 3.10 and pip..."
    case "$OS" in
        linux)      install_package python3.10 python3-pip;;
        macos)      install_package python@3.10;;
        windows)    install_package python3.10;;
    esac
    echo "Installed Python version:"
    python --version
    echo "Installed pip version:"
    pip --version
    ;;
  "python-3.12-pip")
    echo "Installing Python 3.12 and pip..."
    case "$OS" in
        linux)      install_package python3.12 python3-pip;;
        macos)      install_package python@3.12;;
        windows)    install_package python3.12;;
    esac
    echo "Installed Python version:"
    python --version
    echo "Installed pip version:"
    pip --version
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