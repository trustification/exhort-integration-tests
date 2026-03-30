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

VALID_LICENSE_CATEGORIES = {"PERMISSIVE", "WEAK_COPYLEFT", "STRONG_COPYLEFT", "UNKNOWN"}

VULN_SUMMARY_FIELDS = [
    "direct", "transitive", "total", "dependencies",
    "critical", "high", "medium", "low",
    "remediations", "recommendations", "unscanned"
]

LICENSE_SUMMARY_FIELDS = [
    "total", "concluded", "permissive", "weakCopyleft",
    "strongCopyleft", "unknown", "deprecated", "osiApproved", "fsfLibre"
]


def validate_analysis(output: Dict[str, Any], spec: Dict[str, Any], analysis_type: str) -> bool:
    """Validate analysis results using structural and invariant checks."""
    if not output or not isinstance(output, dict):
        print(f"  FAIL {analysis_type} output is empty or not a dictionary")
        return False

    expected = spec[analysis_type]
    ok = True

    # --- Scanned validation ---
    if "scanned" not in output:
        print(f"  FAIL {analysis_type} missing 'scanned' key")
        return False

    scanned = output["scanned"]
    exp_scanned = expected.get("scanned", {})

    # Invariant: total == direct + transitive
    if scanned.get("total") != scanned.get("direct", 0) + scanned.get("transitive", 0):
        print(f"  FAIL {analysis_type} scanned.total ({scanned.get('total')}) != "
              f"direct ({scanned.get('direct')}) + transitive ({scanned.get('transitive')})")
        ok = False

    # Deterministic: direct count matches manifest
    if "direct" in exp_scanned:
        if scanned.get("direct") != exp_scanned["direct"]:
            print(f"  FAIL {analysis_type} scanned.direct: expected {exp_scanned['direct']}, "
                  f"got {scanned.get('direct')}")
            ok = False

    # Deterministic: transitive count must match exactly
    if "transitive" in exp_scanned:
        if scanned.get("transitive") != exp_scanned["transitive"]:
            print(f"  FAIL {analysis_type} scanned.transitive: expected {exp_scanned['transitive']}, "
                  f"got {scanned.get('transitive')}")
            ok = False


    # --- Provider validation ---
    if "providers" not in output:
        print(f"  FAIL {analysis_type} missing 'providers' key")
        return False

    if not isinstance(output["providers"], dict):
        print(f"  FAIL {analysis_type} 'providers' is not a dictionary")
        return False

    exp_providers = expected.get("providers", {})
    for provider_name, provider_spec in exp_providers.items():
        if provider_name not in output["providers"]:
            print(f"  FAIL {analysis_type} missing provider: {provider_name}")
            ok = False
            continue

        provider = output["providers"][provider_name]

        # Validate provider status
        status = provider.get("status", {})
        if not status.get("ok"):
            print(f"  FAIL {analysis_type} provider {provider_name} status not ok: {status}")
            ok = False
        if status.get("code") != 200:
            print(f"  FAIL {analysis_type} provider {provider_name} status code: {status.get('code')}")
            ok = False

        # Validate expected sources
        expected_sources = provider_spec.get("sources", [])
        actual_sources = provider.get("sources", {})

        for source_name in expected_sources:
            if source_name not in actual_sources:
                print(f"  FAIL {analysis_type} provider {provider_name} missing source: {source_name}")
                ok = False
                continue

            source = actual_sources[source_name]
            summary = source.get("summary")
            if not summary:
                print(f"  FAIL {analysis_type} provider {provider_name} source {source_name} missing summary")
                ok = False
                continue

            # Check all required fields exist
            for field in VULN_SUMMARY_FIELDS:
                if field not in summary:
                    print(f"  FAIL {analysis_type} {provider_name}/{source_name} missing field: {field}")
                    ok = False

            if not ok:
                continue

            # Invariant: total == critical + high + medium + low
            severity_sum = summary["critical"] + summary["high"] + summary["medium"] + summary["low"]
            if summary["total"] != severity_sum:
                print(f"  FAIL {analysis_type} {provider_name}/{source_name} "
                      f"total ({summary['total']}) != critical+high+medium+low ({severity_sum})")
                ok = False

            # Invariant: direct + transitive == total
            if summary["direct"] + summary["transitive"] != summary["total"]:
                print(f"  FAIL {analysis_type} {provider_name}/{source_name} "
                      f"direct+transitive ({summary['direct']+summary['transitive']}) != total ({summary['total']})")
                ok = False

            # Invariant: all counts non-negative
            for field in VULN_SUMMARY_FIELDS:
                if summary[field] < 0:
                    print(f"  FAIL {analysis_type} {provider_name}/{source_name} {field} is negative: {summary[field]}")
                    ok = False

            # Invariant: dependencies <= scanned total
            if summary["dependencies"] > scanned.get("total", 0):
                print(f"  FAIL {analysis_type} {provider_name}/{source_name} "
                      f"dependencies ({summary['dependencies']}) > scanned.total ({scanned.get('total')})")
                ok = False

            # Liveness: total > 0 for sources with known-vulnerable deps
            if summary["total"] == 0:
                print(f"  WARN {analysis_type} {provider_name}/{source_name} total vulnerabilities is 0")

    # --- License validation within analysis response ---
    if "licenses" in expected:
        if not validate_licenses(output, expected["licenses"], analysis_type):
            ok = False

    if ok:
        print(f"  PASS {analysis_type} structural and invariant checks passed")

    return ok


def validate_licenses(output: Dict[str, Any], license_spec: Dict[str, Any], context: str) -> bool:
    """Validate the licenses array in a component/stack analysis response."""
    if "licenses" not in output:
        print(f"  FAIL {context} missing 'licenses' key")
        return False

    licenses = output["licenses"]
    if not isinstance(licenses, list):
        print(f"  FAIL {context} 'licenses' is not a list")
        return False

    ok = True

    # Check expected providers are present
    expected_providers = license_spec.get("expected_providers", [])
    provider_names = [lic.get("status", {}).get("name") for lic in licenses]

    for expected_name in expected_providers:
        if expected_name not in provider_names:
            print(f"  FAIL {context} missing license provider: {expected_name} "
                  f"(found: {provider_names})")
            ok = False

    # Validate each license provider
    for lic_provider in licenses:
        status = lic_provider.get("status", {})
        name = status.get("name", "unknown")

        # Status checks (license providers may not have code/message fields)
        if not status.get("ok"):
            print(f"  FAIL {context} license provider {name} status not ok")
            ok = False

        # Summary structure
        summary = lic_provider.get("summary")
        if summary is None:
            print(f"  FAIL {context} license provider {name} missing summary")
            ok = False
            continue

        for field in LICENSE_SUMMARY_FIELDS:
            if field not in summary:
                print(f"  FAIL {context} license provider {name} missing summary field: {field}")
                ok = False

        if not ok:
            continue

        # Non-negative counts
        for field in LICENSE_SUMMARY_FIELDS:
            if summary[field] < 0:
                print(f"  FAIL {context} license provider {name} {field} is negative: {summary[field]}")
                ok = False

        # Invariant: category sum == total (for providers with data)
        if summary["total"] > 0:
            category_sum = (summary["permissive"] + summary["weakCopyleft"] +
                          summary["strongCopyleft"] + summary["unknown"])
            if summary["total"] != category_sum:
                print(f"  FAIL {context} license provider {name} "
                      f"total ({summary['total']}) != category sum ({category_sum})")
                ok = False

        # Validate package entries have valid categories
        packages = lic_provider.get("packages", {})
        for pkg_ref, pkg_data in packages.items():
            if not isinstance(pkg_data, dict):
                continue
            concluded = pkg_data.get("concluded")
            if concluded and isinstance(concluded, dict):
                category = concluded.get("category")
                if category and category not in VALID_LICENSE_CATEGORIES:
                    print(f"  FAIL {context} license provider {name} package {pkg_ref} "
                          f"invalid category: {category}")
                    ok = False

    if ok:
        print(f"  PASS {context} license checks passed")

    return ok


def validate_license_command(output: Dict[str, Any]) -> bool:
    """Validate the response from the license command."""
    if not output or not isinstance(output, dict):
        print("  FAIL license command output is empty or not a dictionary")
        return False

    ok = True

    # The response must have a mismatch field (boolean)
    if "mismatch" not in output:
        print("  FAIL license command missing 'mismatch' field")
        return False

    if not isinstance(output["mismatch"], bool):
        print(f"  FAIL license command 'mismatch' is not boolean: {output['mismatch']}")
        ok = False

    # Validate license objects if present and non-null
    for key in ["manifestLicense", "fileLicense"]:
        if key not in output or output[key] is None:
            continue
        lic = output[key]
        if not isinstance(lic, dict):
            print(f"  FAIL license command {key} is not a dictionary")
            ok = False
            continue

        # Must have identifiers list
        if "identifiers" not in lic or not isinstance(lic["identifiers"], list):
            print(f"  FAIL license command {key} missing or invalid 'identifiers'")
            ok = False

        # Must have expression string
        if "expression" not in lic or not isinstance(lic["expression"], str):
            print(f"  FAIL license command {key} missing or invalid 'expression'")
            ok = False

        # Must have valid category
        category = lic.get("category")
        if category and category not in VALID_LICENSE_CATEGORIES:
            print(f"  FAIL license command {key} invalid category: {category}")
            ok = False

    if ok:
        print("  PASS license command checks passed")

    return ok


def validate_html_output(output: str) -> bool:
    """Basic validation of HTML output."""
    if not output.strip():
        print("  FAIL HTML output is empty")
        return False

    if not output.lower().startswith("<!doctype html") and not output.lower().startswith("<html"):
        print("  FAIL Output doesn't appear to be valid HTML")
        return False

    print("  PASS HTML output appears valid")
    return True


def run_scenario(language: str, cli_dir: str, scenario_dir: Path, runtime: str) -> bool:
    """Run a single scenario and validate its results."""
    spec_file = scenario_dir / "spec.yaml"
    if not spec_file.exists():
        print(f"  FAIL No spec.yaml found for scenario: {scenario_dir}")
        return False

    with open(spec_file) as f:
        spec = yaml.safe_load(f)

    print("---")
    print(f"Scenario: {spec['title']}")
    print(f"Description: {spec['description']}")
    print(f"Manifest: {scenario_dir / get_manifest_file(runtime)}")
    print(f"Expect success: {spec['expect_success']}")

    manifest_file = get_manifest_file(runtime)
    commands = get_commands(language, cli_dir, str(scenario_dir), manifest_file)

    for cmd in commands:
        print(f"Executing: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if spec["expect_success"]:
                if result.returncode == 0:
                    print("  PASS Command succeeded as expected")

                    # Handle HTML output
                    if "--html" in cmd:
                        if not validate_html_output(result.stdout):
                            return False
                        continue

                    # Parse the command output as JSON
                    try:
                        output = json.loads(result.stdout)

                        if "component" in cmd:
                            print("Validating component analysis...")
                            if not validate_analysis(output, spec, "component_analysis"):
                                return False
                        elif "license" in cmd and "stack" not in cmd and "component" not in cmd:
                            print("Validating license command...")
                            license_spec = spec.get("license_check", {})
                            if license_spec.get("expect_success", True):
                                if not validate_license_command(output):
                                    return False
                        elif "stack" in cmd and not any(flag in cmd for flag in ["--summary", "--html"]):
                            print("Validating stack analysis...")
                            if not validate_analysis(output, spec, "stack_analysis"):
                                return False
                    except json.JSONDecodeError:
                        print("  FAIL Failed to parse command output as JSON")
                        print("Output:", result.stdout[:500])
                        return False
                else:
                    print("  FAIL Expected success but command failed")
                    print(result.stdout[:500])
                    print(result.stderr[:500])
                    return False
            else:
                if result.returncode != 0:
                    print("  PASS Failure as expected")
                else:
                    print("  FAIL Expected failure but command succeeded")
                    print(result.stdout[:500])
                    print(result.stderr[:500])
                    return False
        except subprocess.SubprocessError as e:
            print(f"  FAIL Error executing command: {e}")
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
            normalized_scenario_dir = scenario_dir.resolve()
            if not run_scenario(language, cli_dir, normalized_scenario_dir, runtime):
                success = False
                break

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
