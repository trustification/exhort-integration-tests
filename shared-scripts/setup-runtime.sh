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
  "yarn-berry")
    echo "Installing Yarn Berry..."
    # Enable corepack and prepare Yarn Berry
    npm uninstall -g yarn
    corepack enable
    corepack prepare yarn@4.9.1 --activate
    echo "Installed yarn version:"
    yarn -v
    ;;
  "pnpm")
    echo "Installing pnpm..."
    corepack enable
    corepack prepare pnpm@latest-10 --activate
    echo "Installed pnpm version:"
    pnpm -v
    ;;
  "go-1.20")
    echo "Installing Go 1.20..."
    case "$OS" in
      macos)
        # Use Homebrew for Go on macOS
        brew install go@1.20
        # Set up Go 1.20 as default (keg-only formula)
        export PATH="/opt/homebrew/opt/go@1.20/bin:$PATH"
        export GOROOT="/opt/homebrew/opt/go@1.20/libexec"
        # Persist environment variables for subsequent steps
        echo "PATH=$PATH" >> $GITHUB_ENV
        echo "GOROOT=$GOROOT" >> $GITHUB_ENV
        ;;
      *)
        echo "Go is already installed on $OS"
        ;;
    esac
    
    echo "Installed Go version:"
    go version
    ;;
  "go-latest")
    echo "Installing latest Go..."
    case "$OS" in
      macos)
        brew install go@1.24
        export PATH="/opt/homebrew/opt/go@1.24/bin:$PATH"
        export GOROOT="/opt/homebrew/opt/go@1.24/libexec"
        echo "PATH=$PATH" >> $GITHUB_ENV
        echo "GOROOT=$GOROOT" >> $GITHUB_ENV
        ;;
      *)
        echo "Go is already installed on $OS"
        ;;
    esac
    echo "Installed Go version:"
    go version
    ;;
  "python-3.10-pip")
    echo "TODO: Install Python 3.10 and pip..."
    ;;
  
  "none")
    echo "No additional runtime setup required."
    ;;
  *)
    echo "Nothing to install for: $RUNTIME"
    exit 0
    ;;
esac

echo "Runtime setup complete." 