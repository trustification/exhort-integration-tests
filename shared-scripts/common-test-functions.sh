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

# Function to get commands based on language
get_commands() {
  local LANGUAGE="$1"
  local CLI_DIR="$2"
  local SCENARIO="$3"
  local MANIFEST="$4"

  case "$LANGUAGE" in
    "javascript")
      echo "npx --yes file:$CLI_DIR/cli.tgz component $SCENARIO/$MANIFEST"
      echo "npx --yes file:$CLI_DIR/cli.tgz stack $SCENARIO/$MANIFEST"
      echo "npx --yes file:$CLI_DIR/cli.tgz stack $SCENARIO/$MANIFEST --summary"
      echo "npx --yes file:$CLI_DIR/cli.tgz stack $SCENARIO/$MANIFEST --html"
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

# Function to parse spec.yaml
parse_spec_yaml() {
  local SCENARIO="$1"
  python3 -c '
import sys, yaml
with open(sys.argv[1]) as f:
  d = yaml.safe_load(f)
  for k in ["title", "description", "expect_success"]:
    v = d.get(k, "")
    print(f"{k.upper()}=\"{v}\"")
' "$SCENARIO/spec.yaml"
} 