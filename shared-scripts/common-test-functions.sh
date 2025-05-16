#!/bin/bash

# Function to get manifest file name based on runtime
get_manifest_file() {
  local RUNTIME="$1"
  case "$RUNTIME" in
    maven)
      echo "pom.xml"
      ;;
    gradle-groovy)
      echo "build.gradle"
      ;;
    gradle-kotlin)
      echo "build.gradle.kts"
      ;;
    npm|yarn-classic|yarn-berry|pnpm)
      echo "package.json"
      ;;
    go*|go)
      echo "go.mod"
      ;;
    python-*|python-pip)
      echo "requirements.txt"
      ;;
    *)
      echo "Unknown or unsupported runtime: $RUNTIME" >&2
      exit 1
      ;;
  esac
}

get_package_manager() {
  local RUNTIME="$1"
  case "$RUNTIME" in
    npm)
      echo "npm"
      ;;
    yarn-classic|yarn-berry)
      echo "yarn"
      ;;
    pnpm)
      echo "pnpm"
      ;;
    maven)
      echo "mvn"
      ;;
    gradle-groovy|gradle-kotlin)
      echo "gradle"
      ;;
    go*|go)
      echo "go"
      ;;
    python-*|python-pip)
      echo "pip"
      ;;
    *)
      echo "Unknown or unsupported runtime: $RUNTIME" >&2
      exit 1
      ;;
  esac
}

get_scenario_base_dir() {
  local RUNTIME="$1"
  case "$RUNTIME" in
    gradle-groovy|gradle-kotlin)
      echo $RUNTIME
      ;;
    yarn-classic|yarn-berry)
      echo $RUNTIME
      ;;
    *)
      echo $(get_package_manager $RUNTIME)
      ;;
  esac
}

get_env_var_name() {
  local RUNTIME="$1"
  local PACKAGE_MANAGER=$(get_package_manager $RUNTIME)
  echo "EXHORT_$(echo $PACKAGE_MANAGER | tr '[:lower:]' '[:upper:]')_PATH"
}

# Function to get commands based on language
get_commands() {
  local LANGUAGE="$1"
  local CLI_DIR="$2"
  local SCENARIO="$3"
  local MANIFEST="$4"

  case "$LANGUAGE" in
    "javascript")
      # Convert CLI_DIR to absolute path and normalize for Windows
      CLI_DIR="$(cd "$CLI_DIR" && pwd)"
      if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # For Windows, convert to proper drive letter format
        if [[ "$CLI_DIR" =~ ^/[a-zA-Z]/ ]]; then
          # Convert /d/... to d:/...
          drive_letter=$(echo "$CLI_DIR" | cut -d'/' -f2)
          rest_of_path=$(echo "$CLI_DIR" | cut -d'/' -f3-)
          CLI_DIR="${drive_letter}:/${rest_of_path}"
        fi
      fi
      echo "npx --yes file:///$CLI_DIR/cli.tgz component $SCENARIO/$MANIFEST"
      echo "npx --yes file:///$CLI_DIR/cli.tgz stack $SCENARIO/$MANIFEST"
      echo "npx --yes file:///$CLI_DIR/cli.tgz stack $SCENARIO/$MANIFEST --summary"
      echo "npx --yes file:///$CLI_DIR/cli.tgz stack $SCENARIO/$MANIFEST --html"
      ;;
    "java")
      echo "java -jar $CLI_DIR/cli.jar component $SCENARIO/$MANIFEST"
      echo "java -jar $CLI_DIR/cli.jar stack $SCENARIO/$MANIFEST"
      echo "java -jar $CLI_DIR/cli.jar stack $SCENARIO/$MANIFEST --summary"
      echo "java -jar $CLI_DIR/cli.jar stack $SCENARIO/$MANIFEST --html"
      ;;
    *)
      echo "Unknown language: $LANGUAGE" >&2
      exit 1
      ;;
  esac
}

# Function to parse spec properties
parse_spec() {
  local SCENARIO="$1"
  while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ $key =~ ^#.*$ ]] && continue
    [[ -z $key ]] && continue
    # Remove any quotes from the value
    value=$(echo "$value" | tr -d '"'"'")
    echo "$(echo "$key" | tr '[:lower:]' '[:upper:]')=\"$value\""
  done < "$SCENARIO/spec.properties"
} 