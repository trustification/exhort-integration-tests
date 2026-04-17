#!/bin/bash
# Print installed versions of all ecosystem runtimes.
# Called by CI after setup-runtime.sh to log the test environment.
set -e

# Function to check version of a command
check_version() {
    local cmd=$1
    local name=$2
    echo "📦 $name:"
    if command -v "$cmd" >/dev/null 2>&1; then
        $cmd --version 2>/dev/null || $cmd -v 2>/dev/null || $cmd version 2>/dev/null || echo "Version not available"
    else
        echo "❌ Not present"
    fi
    echo
}

echo "🔍 Environment versions:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_version "java" "Java"
check_version "mvn" "Maven"
check_version "gradle" "Gradle"
check_version "npm" "npm"
check_version "node" "Node.js"
check_version "yarn" "Yarn"
check_version "pnpm" "pnpm"
check_version "go" "Go"
check_version "python" "Python"
check_version "pip" "pip"
check_version "syft" "Syft"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
