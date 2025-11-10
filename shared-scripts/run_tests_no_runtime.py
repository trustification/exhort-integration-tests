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
    get_package_manager
)

def run_no_runtime_test(language: str, cli_dir: str, runtime: str) -> bool:
    """Run the no-runtime test for a specific runtime."""
    script_dir = Path(__file__).parent
    scenarios_dir = script_dir.parent / "scenarios" / get_scenario_base_dir(runtime)
    
    if not scenarios_dir.exists():
        print(f"No scenarios found for runtime: {runtime}")
        return True
    
    # Only run the simple scenario
    scenario_dir = (scenarios_dir / "simple").resolve()
    if not scenario_dir.exists():
        print(f"Simple scenario not found for runtime: {runtime}")
        return True
    
    print("---")
    print("Scenario: No runtime available")
    print("Description: It fails when no runtime is available")
    print(f"Manifest: {scenario_dir / get_manifest_file(runtime)}")
    print("Expecting failure (no runtime available)")
    
    commands = get_commands(language, cli_dir, str(scenario_dir), get_manifest_file(runtime))
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        
        # Store original environment variables that will be modified
        env_vars_to_restore = {}
        
        # Get both TRUSTIFY_DA_ and EXHORT_ env var names for this runtime
        package_manager = get_package_manager(runtime)
        trustify_var = f"TRUSTIFY_DA_{package_manager.upper()}_PATH"
        exhort_var = f"EXHORT_{package_manager.upper()}_PATH"
        
        # Set both environment variables to INVALID
        for env_var in [trustify_var, exhort_var]:
            env_vars_to_restore[env_var] = os.environ.get(env_var)
            os.environ[env_var] = "INVALID"
        
        # Set ALL possible environment variables to INVALID to ensure no runtime is available
        # This covers all possible runtime detection mechanisms
        # Support both TRUSTIFY_DA_ (new) and EXHORT_ (legacy) prefixes
        all_env_vars = [
            "TRUSTIFY_DA_PIP_PATH",
            "TRUSTIFY_DA_PIP3_PATH", 
            "TRUSTIFY_DA_PYTHON_PATH",
            "TRUSTIFY_DA_PYTHON3_PATH",
            "TRUSTIFY_DA_NPM_PATH",
            "TRUSTIFY_DA_PNPM_PATH",
            "TRUSTIFY_DA_YARN_PATH",
            "TRUSTIFY_DA_MVN_PATH",
            "TRUSTIFY_DA_GRADLE_PATH",
            "TRUSTIFY_DA_GO_PATH",
            "EXHORT_PIP_PATH",
            "EXHORT_PIP3_PATH", 
            "EXHORT_PYTHON_PATH",
            "EXHORT_PYTHON3_PATH",
            "EXHORT_NPM_PATH",
            "EXHORT_PNPM_PATH",
            "EXHORT_YARN_PATH",
            "EXHORT_MVN_PATH",
            "EXHORT_GRADLE_PATH",
            "EXHORT_GO_PATH"
        ]
        
        for env_var in all_env_vars:
            if env_var not in env_vars_to_restore:  # Don't override if already set above
                env_vars_to_restore[env_var] = os.environ.get(env_var)
            os.environ[env_var] = "INVALID"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # All commands should fail since no runtime is available
            if result.returncode == 0:
                print("❌ Command succeeded but expected failure (no runtime available)")
                return False
            else:
                print("✅ Command failed as expected (no runtime available)")
        finally:
            # Restore all original environment variables
            for env_var, original_value in env_vars_to_restore.items():
                if original_value is not None:
                    os.environ[env_var] = original_value
                else:
                    if env_var in os.environ:
                        del os.environ[env_var]
    
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