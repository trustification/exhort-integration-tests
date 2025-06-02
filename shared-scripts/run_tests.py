#!/usr/bin/env python3

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from common_test_functions import (
    get_manifest_file,
    get_scenario_base_dir,
    get_commands
)

def validate_component_analysis(output: Dict[str, Any], spec: Dict[str, Any]) -> bool:
    """Validate component analysis results against spec.yaml expectations."""
    expected = spec['component_analysis']
    actual = output
    
    # Validate scanned metrics
    scanned_fields = ['total', 'direct', 'transitive']
    for field in scanned_fields:
        if actual['scanned'][field] != expected['scanned'][field]:
            print(f"❌ Scanned {field} mismatch: expected {expected['scanned'][field]}, got {actual['scanned'][field]}")
            return False
    
    # Validate TPA provider metrics
    tpa_fields = ['total', 'direct', 'transitive', 'dependencies']
    for field in tpa_fields:
        if actual['tpa_provider'][field] != expected['tpa_provider'][field]:
            print(f"❌ TPA {field} mismatch: expected {expected['tpa_provider'][field]}, got {actual['tpa_provider'][field]}")
            return False
    
    return True

def validate_stack_analysis(output: Dict[str, Any], spec: Dict[str, Any]) -> bool:
    """Validate stack analysis results against spec.yaml expectations."""
    expected = spec['stack_analysis']
    actual = output
    
    # Validate scanned metrics
    scanned_fields = ['total', 'direct', 'transitive']
    for field in scanned_fields:
        if actual['scanned'][field] != expected['scanned'][field]:
            print(f"❌ Stack scanned {field} mismatch: expected {expected['scanned'][field]}, got {actual['scanned'][field]}")
            return False
    
    # Validate TPA provider metrics
    tpa_fields = ['total', 'direct', 'transitive', 'dependencies']
    for field in tpa_fields:
        if actual['tpa_provider'][field] != expected['tpa_provider'][field]:
            print(f"❌ Stack TPA {field} mismatch: expected {expected['tpa_provider'][field]}, got {actual['tpa_provider'][field]}")
            return False
    
    return True

def run_scenario(language: str, cli_dir: str, scenario_dir: Path, runtime: str) -> bool:
    """Run a single scenario and validate its results."""
    spec_file = scenario_dir / "spec.yaml"
    if not spec_file.exists():
        print(f"❌ No spec.yaml found for scenario: {scenario_dir}")
        return False
    
    with open(spec_file) as f:
        spec = yaml.safe_load(f)
    
    print("---")
    print(f"Scenario: {spec['title']}")
    print(f"Description: {spec['description']}")
    print(f"Manifest: {scenario_dir}/{get_manifest_file(runtime)}")
    print(f"Expect success: {spec['expect_success']}")
    
    commands = get_commands(language, cli_dir, str(scenario_dir), get_manifest_file(runtime))
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if spec['expect_success']:
                if result.returncode == 0:
                    print("✅ Command succeeded as expected")
                    
                    # Parse the command output as JSON
                    try:
                        output = json.loads(result.stdout)
                        
                        # Determine which validation to run based on the command
                        if "component" in cmd:
                            print("Validating component analysis...")
                            if not validate_component_analysis(output, spec):
                                print("❌ Component analysis validation failed")
                                return False
                            print("✅ Component analysis validation passed")
                        elif "stack" in cmd and not any(flag in cmd for flag in ["--summary", "--html"]):
                            print("Validating stack analysis...")
                            if not validate_stack_analysis(output, spec):
                                print("❌ Stack analysis validation failed")
                                return False
                            print("✅ Stack analysis validation passed")
                    except json.JSONDecodeError:
                        print("❌ Failed to parse command output as JSON")
                        print("Output:", result.stdout)
                        return False
                else:
                    print("❌ Expected success but command failed")
                    print(result.stdout)
                    print(result.stderr)
                    return False
            else:
                if result.returncode != 0:
                    print("✅ Failure as expected")
                else:
                    print("❌ Expected failure but command succeeded")
                    print(result.stdout)
                    print(result.stderr)
                    return False
        except subprocess.SubprocessError as e:
            print(f"❌ Error executing command: {e}")
            return False
    
    print("---")
    return True

def main():
    if len(sys.argv) != 4:
        print("Usage: run_tests.py <language> <cli_dir> <runtime>")
        sys.exit(1)
    
    language = sys.argv[1]
    cli_dir = sys.argv[2]
    runtime = sys.argv[3]
    
    script_dir = Path(__file__).parent
    scenarios_dir = script_dir.parent / "scenarios" / get_scenario_base_dir(runtime)
    
    if not scenarios_dir.exists():
        print(f"No scenarios found for runtime: {runtime}")
        sys.exit(0)
    
    success = True
    for scenario_dir in scenarios_dir.iterdir():
        if scenario_dir.is_dir() and (scenario_dir / "spec.yaml").exists():
            if not run_scenario(language, cli_dir, scenario_dir, runtime):
                success = False
                break
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 