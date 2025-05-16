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

# Function to get the latest version of a package
get_latest_version() {
    local package="$1"
    case "$package" in
        openjdk) echo "21";;
        maven) echo "3.9.9";;
        gradle) echo "8.14";;
        *) echo "Unsupported package: $package"; exit 1;;
    esac
}


# Function to install packages based on OS
install_package() {
    local package="$1"
    local version=get_latest_version "${package}"
    case "$OS" in
        linux)
            sudo apt-get update
            sudo apt-get remove --purge -y "${package}"
            sudo apt-get install -y "${package}-${version}"
            ;;
        macos)
            brew uninstall "${package}"
            brew install "${package}@${version}"
            ;;
        windows)
            choco uninstall "${package}" -y
            choco install "${package}" --version="${version}" -y
            ;;
    esac
}

case "$RUNTIME" in
  "maven")
    echo "Installing Maven..."
    install_package openjdk
    install_package maven;;
    esac
    echo "Installed Java version:"
    java -version
    echo "Installed Maven version:"
    mvn -v
    ;;
  "gradle-groovy"|"gradle-kotlin")
    echo "Installing Gradle..."
    install_package openjdk gradle;;
    esac
    echo "Installed Java version:"
    java -version
    echo "Installed Gradle version:"
    gradle -v
    ;;
  # "npm")
  #   echo "Installing npm..."
  #   case "$OS" in
  #       linux)      install_package npm;;
  #       macos)      install_package node;;
  #       windows)    choco install nodejs -y;;
  #   esac
  #   echo "Installed npm version:" 
  #   npm -v
  #   echo "Installed node version:"
  #   node -v
  #   ;;
  # "yarn-classic")
  #   echo "Installing Yarn Classic..."
  #   npm install -g yarn@1
  #   echo "Installed yarn version:"
  #   yarn -v
  #   ;;
  # "yarn-berry")
  #   echo "Installing Yarn Berry..."
  #   corepack enable
  #   corepack prepare yarn@stable --activate
  #   echo "Installed yarn version:"
  #   yarn -v
  #   ;;
  # "pnpm")
  #   echo "Installing pnpm..."
  #   npm install -g pnpm
  #   echo "Installed pnpm version:"
  #   pnpm -v
  #   ;;
  # "go-1.20")
  #   echo "Installing Go 1.20..."
  #   install_package golang-go
  #   # Install specific version if needed
  #   go install "golang.org/dl/go1.20.14@latest"
  #   "go1.20.14" download
  #   ;;
  # "go-latest")
  #   echo "Installing latest Go..."
  #   install_package golang-go
  #   echo "Installed Go version:"
  #   go version
  #   ;;
  # "python-3.10-pip")
  #   echo "Installing Python 3.10 and pip..."
  #   case "$OS" in
  #       linux)      install_package python3.10 python3-pip;;
  #       macos)      install_package python@3.10;;
  #       windows)    install_package python3.10;;
  #   esac
  #   echo "Installed Python version:"
  #   python --version
  #   echo "Installed pip version:"
  #   pip --version
  #   ;;
  # "python-3.12-pip")
  #   echo "Installing Python 3.12 and pip..."
  #   case "$OS" in
  #       linux)      install_package python3.12 python3-pip;;
  #       macos)      install_package python@3.12;;
  #       windows)    install_package python3.12;;
  #   esac
  #   echo "Installed Python version:"
  #   python --version
  #   echo "Installed pip version:"
  #   pip --version
  #   ;;
  "none")
    echo "No additional runtime setup required."
    ;;
  *)
    echo "Unknown runtime: $RUNTIME"
    exit 1
    ;;
esac

echo "Runtime setup complete." 