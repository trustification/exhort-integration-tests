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

def validate_analysis(output: Dict[str, Any], spec: Dict[str, Any], analysis_type: str) -> bool:
    """Validate analysis results against spec.yaml expectations."""
    print(f"Output structure: {json.dumps(output, indent=2)}")
    print(f"Expected structure: {json.dumps(spec[analysis_type], indent=2)}")
    
    expected = spec[analysis_type]
    actual = output
    
    # Validate scanned metrics
    scanned_fields = ['total', 'direct', 'transitive']
    for field in scanned_fields:
        if actual['scanned'][field] != expected['scanned'][field]:
            print(f"❌ {analysis_type} scanned {field} mismatch: expected {expected['scanned'][field]}, got {actual['scanned'][field]}")
            return False
    
    # Validate all providers and their sources
    for provider_name, provider_spec in expected.items():
        if provider_name == 'scanned':  # Skip scanned metrics as they're handled above
            continue
            
        if provider_name not in actual['providers']:
            print(f"❌ {analysis_type} missing provider: {provider_name}")
            return False
            
        provider = actual['providers'][provider_name]
        
        # Handle both single source and multiple sources
        if isinstance(provider_spec, dict) and any(isinstance(v, dict) for v in provider_spec.values()):
            # Multiple sources case
            for source_name, source_spec in provider_spec.items():
                if source_name not in provider['sources']:
                    print(f"❌ {analysis_type} provider {provider_name} missing source: {source_name}")
                    return False
                    
                source = provider['sources'][source_name]
                if 'summary' not in source:
                    print(f"❌ {analysis_type} provider {provider_name} source {source_name} missing summary")
                    return False
                    
                # Validate all fields in the source summary
                for field, expected_value in source_spec.items():
                    if field not in source['summary']:
                        print(f"❌ {analysis_type} provider {provider_name} source {source_name} missing field: {field}")
                        return False
                    if source['summary'][field] != expected_value:
                        print(f"❌ {analysis_type} provider {provider_name} source {source_name} {field} mismatch: expected {expected_value}, got {source['summary'][field]}")
                        return False
        else:
            # Single source case (backward compatibility)
            if 'summary' not in provider:
                print(f"❌ {analysis_type} provider {provider_name} missing summary")
                return False
                
            # Validate all fields in the provider summary
            for field, expected_value in provider_spec.items():
                if field not in provider['summary']:
                    print(f"❌ {analysis_type} provider {provider_name} missing field: {field}")
                    return False
                if provider['summary'][field] != expected_value:
                    print(f"❌ {analysis_type} provider {provider_name} {field} mismatch: expected {expected_value}, got {provider['summary'][field]}")
                    return False
    
    return True

def validate_html_output(output: str) -> bool:
    """Basic validation of HTML output."""
    if not output.strip():
        print("❌ HTML output is empty")
        return False
    
    if not output.lower().startswith("<!doctype html") and not output.lower().startswith("<html"):
        print("❌ Output doesn't appear to be valid HTML")
        return False
    
    print("✅ HTML output appears valid")
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
    
    manifest_file = get_manifest_file(runtime)
    commands = get_commands(language, cli_dir, str(scenario_dir), manifest_file)
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if spec['expect_success']:
                if result.returncode == 0:
                    print("✅ Command succeeded as expected")
                    
                    # Handle HTML output
                    if "--html" in cmd:
                        if not validate_html_output(result.stdout):
                            return False
                        continue
                    
                    # Parse the command output as JSON
                    try:
                        output = json.loads(result.stdout)
                        
                        # Determine which validation to run based on the command
                        if "component" in cmd:
                            print("Validating component analysis...")
                            if not validate_analysis(output, spec, 'component_analysis'):
                                print("❌ Component analysis validation failed")
                                return False
                            print("✅ Component analysis validation passed")
                        elif "stack" in cmd and not any(flag in cmd for flag in ["--summary", "--html"]):
                            print("Validating stack analysis...")
                            if not validate_analysis(output, spec, 'stack_analysis'):
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