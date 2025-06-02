#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from common_test_functions import (
    get_manifest_file,
    get_scenario_base_dir,
    get_commands,
    get_env_var_name
)

def run_no_runtime_test(language: str, cli_dir: str, runtime: str) -> bool:
    """Run the no-runtime test for a specific runtime."""
    script_dir = Path(__file__).parent
    scenarios_dir = script_dir.parent / "scenarios" / get_scenario_base_dir(runtime)
    
    if not scenarios_dir.exists():
        print(f"No scenarios found for runtime: {runtime}")
        return True
    
    # Only run the simple scenario
    scenario_dir = scenarios_dir / "simple"
    if not scenario_dir.exists():
        print(f"Simple scenario not found for runtime: {runtime}")
        return True
    
    print("---")
    print("Scenario: No runtime available")
    print("Description: It fails when no runtime is available")
    print(f"Manifest: {scenario_dir}/{get_manifest_file(runtime)}")
    print("Expecting failure (no runtime available)")
    
    commands = get_commands(language, cli_dir, str(scenario_dir), get_manifest_file(runtime))
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        
        # Set the environment variable to an invalid path
        env_var_name = get_env_var_name(runtime)
        original_env = os.environ.get(env_var_name)
        os.environ[env_var_name] = "INVALID"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # All commands should fail since no runtime is available
            if result.returncode == 0:
                print("❌ Command succeeded but expected failure (no runtime available)")
                return False
            else:
                print("✅ Command failed as expected (no runtime available)")
        finally:
            # Restore original environment variable
            if original_env is not None:
                os.environ[env_var_name] = original_env
            else:
                del os.environ[env_var_name]
    
    print("---")
    return True

def main():
    if len(sys.argv) != 4:
        print("Usage: run_tests_no_runtime.py <language> <cli_dir> <runtime>")
        sys.exit(1)
    
    language = sys.argv[1]
    cli_dir = sys.argv[2]
    runtime = sys.argv[3]
    
    success = run_no_runtime_test(language, cli_dir, runtime)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 