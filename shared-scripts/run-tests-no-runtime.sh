#!/bin/bash
set -e

# Source common functions
source "$(dirname "$0")/common-test-functions.sh"

LANGUAGE="$1"
CLI_DIR="$2"
RUNTIME="$3"

SCENARIOS_DIR="scenarios/$RUNTIME"

# Get manifest file name
MANIFEST=$(get_manifest_file "$RUNTIME")

if [ ! -d "$SCENARIOS_DIR" ]; then
  echo "No scenarios found for runtime: $RUNTIME"
  exit 0
fi

for SCENARIO in "$SCENARIOS_DIR"/*; do
  if [ -d "$SCENARIO" ] && [ -f "$SCENARIO/spec.yaml" ]; then
    echo "---"
    # Parse YAML using common function
    eval $(parse_spec_yaml "$SCENARIO")

    echo "Scenario: $TITLE"
    echo "Description: $DESCRIPTION"
    echo "Manifest: $SCENARIO/$MANIFEST"
    echo "Expecting failure (no runtime available)"

    # Get commands using common function and read into array
    COMMANDS=()
    while IFS= read -r cmd; do
      COMMANDS+=("$cmd")
    done < <(get_commands "$LANGUAGE" "$CLI_DIR" "$SCENARIO" "$MANIFEST")

    # Execute each command
    for CMD in "${COMMANDS[@]}"; do
      echo "Executing: $CMD"
      set +e
      $CMD
      STATUS=$?
      set -e

      # All commands should fail since no runtime is available
      if [ $STATUS -eq 0 ]; then
        echo "❌ Command succeeded but expected failure (no runtime available)"
        exit 1
      else
        echo "✅ Command failed as expected (no runtime available)"
      fi
    done
    echo "---"
  fi
done 