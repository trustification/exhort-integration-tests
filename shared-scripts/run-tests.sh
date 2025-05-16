#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source common functions
source "$SCRIPT_DIR/common-test-functions.sh"

LANGUAGE="$1"
CLI_DIR="$2"
RUNTIME="$3"

# Use the correct path for scenarios
SCENARIOS_DIR="$SCRIPT_DIR/../scenarios/$RUNTIME"

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
    echo "Expect success: $EXPECT_SUCCESS"

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

      if [ "$(echo "$EXPECT_SUCCESS" | tr '[:upper:]' '[:lower:]')" = "true" ]; then
        if [ $STATUS -eq 0 ]; then
          echo "✅ Success as expected"
        else
          echo "❌ Expected success but command failed"
          exit 1
        fi
      else
        if [ $STATUS -ne 0 ]; then
          echo "✅ Failure as expected"
        else
          echo "❌ Expected failure but command succeeded"
          exit 1
        fi
      fi
    done
    echo "---"
  fi
done 