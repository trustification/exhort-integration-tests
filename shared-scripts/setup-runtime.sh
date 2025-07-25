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
  "go-1.21")
    echo "Installing Go 1.21..."
    case "$OS" in
      macos)
        # Use Homebrew for Go on macOS
        brew install go@1.21
        # Set up Go 1.21 as default (keg-only formula)
        export PATH="/opt/homebrew/opt/go@1.21/bin:$PATH"
        export GOROOT="/opt/homebrew/opt/go@1.21/libexec"
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
  "syft")
    echo "Installing Syft..."
    case "$OS" in
      windows)
        # Install Syft on Windows using the official installation script
        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b "$(pwd)"
        # Add current directory to PATH for this session
        export PATH="$(pwd):$PATH"
        # Persist PATH for subsequent steps
        echo "PATH=$PATH" >> $GITHUB_ENV
        ;;
      *)
        # Install Syft on Unix-like systems using the official installation script
        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sudo sh -s -- -b /usr/local/bin
        ;;
    esac
    echo "Installed Syft version:"
    syft version
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