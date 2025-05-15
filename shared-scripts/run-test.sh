#!/bin/bash
set -e

LANGUAGE="$1"
CLI_DIR="$2"
RUNTIME="$3"

SCENARIOS_DIR="scenarios/$RUNTIME"

# Map runtime to manifest file name
case "$RUNTIME" in
  java-maven)
    MANIFEST="pom.xml"
    ;;
  java-gradle-groovy)
    MANIFEST="build.gradle"
    ;;
  java-gradle-kotlin)
    MANIFEST="build.gradle.kts"
    ;;
  npm|yarn-classic|yarn-berry|pnpm)
    MANIFEST="package.json"
    ;;
  go*|go)
    MANIFEST="go.mod"
    ;;
  python-*|python-pip)
    MANIFEST="requirements.txt"
    ;;
  *)
    echo "Unknown or unsupported runtime: $RUNTIME"
    exit 1
    ;;
esac

if [ ! -d "$SCENARIOS_DIR" ]; then
  echo "No scenarios found for runtime: $RUNTIME"
  exit 0
fi

for SCENARIO in "$SCENARIOS_DIR"/*; do
  if [ -d "$SCENARIO" ] && [ -f "$SCENARIO/spec.yaml" ]; then
    echo "---"
    # Parse YAML using python (for portability)
    eval $(python3 -c '
import sys, yaml
with open(sys.argv[1]) as f:
  d = yaml.safe_load(f)
  for k in ["title", "description", "expect_success"]:
    v = d.get(k, "")
    print(f"{k.upper()}=\"{v}\"")
' "$SCENARIO/spec.yaml")

    echo "Scenario: $TITLE"
    echo "Description: $DESCRIPTION"
    echo "Manifest: $SCENARIO/$MANIFEST"
    echo "Expect success: $EXPECT_SUCCESS"

    # Build the CLI command
    case "$LANGUAGE" in
      "javascript")
        CMD="node $CLI_DIR/dist/src/cli.js stack $SCENARIO/$MANIFEST"
        ;;
      "java")
        CMD="java -jar $CLI_DIR/cli.jar stack $SCENARIO/$MANIFEST"
        ;;
      *)
        echo "Unknown language: $LANGUAGE"
        exit 1
        ;;
    esac

    echo "Executing: $CMD"
    set +e
    $CMD
    STATUS=$?
    set -e

    if [ "$EXPECT_SUCCESS" = "true" ]; then
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
    echo "---"
  fi
done 