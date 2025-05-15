#!/bin/bash
set -e

RUNTIME="$1"

echo "Setting up runtime: $RUNTIME"

case "$RUNTIME" in
  "java-maven")
    echo "Installing Maven..."
    sudo apt-get update
    sudo apt-get install -y maven
    ;;
  "java-gradle-groovy"|"java-gradle-kotlin")
    echo "Installing Gradle..."
    sudo apt-get update
    sudo apt-get install -y gradle
    ;;
  "npm")
    echo "Installing npm..."
    sudo apt-get update
    sudo apt-get install -y npm
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
    sudo apt-get update
    sudo apt-get install -y golang-1.20-go
    export PATH="/usr/lib/go-1.20/bin:$PATH"
    ;;
  "go-latest")
    echo "Installing latest Go..."
    sudo apt-get update
    sudo apt-get install -y golang-go
    ;;
  "python-3.10-pip")
    echo "Installing Python 3.10 and pip..."
    sudo apt-get update
    sudo apt-get install -y python3.10 python3-pip
    ;;
  "python-3.12-pip")
    echo "Installing Python 3.12 and pip..."
    sudo apt-get update
    sudo apt-get install -y python3.12 python3-pip
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