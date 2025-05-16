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
SCENARIOS_DIR="$SCRIPT_DIR/../scenarios/$(get_scenario_base_dir $RUNTIME)"

# Get manifest file name
MANIFEST=$(get_manifest_file "$RUNTIME")

if [ ! -d "$SCENARIOS_DIR" ]; then
  echo "No scenarios found for runtime: $RUNTIME"
  exit 0
fi

# Only run the simple scenario
SCENARIO="$SCENARIOS_DIR/simple"
if [ ! -d "$SCENARIO" ]; then
  echo "Simple scenario not found for runtime: $RUNTIME"
  exit 0
fi

echo "---"
echo "Scenario: No runtime available"
echo "Description: It fails when no runtime is available"
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
  # Set the environment variable to an invalid path
  ENV_VAR_NAME=$(get_env_var_name "$RUNTIME")
  export "$ENV_VAR_NAME"="INVALID"
  $CMD
  STATUS=$?
  unset "$ENV_VAR_NAME"
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
