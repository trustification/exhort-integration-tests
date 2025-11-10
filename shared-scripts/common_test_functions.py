#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

def get_manifest_file(runtime: str) -> str:
    """Get the manifest file name based on runtime."""
    runtime = runtime.lower()

    if runtime.startswith("syft"):
        return "TODO: Implement OCI CLI support for Syft"
    
    if runtime.startswith('go'):
        return "go.mod"
    
    if runtime.startswith('python'):
        return "requirements.txt"
    
    manifest_map = {
        "maven": "pom.xml",
        "gradle-groovy": "build.gradle",
        "gradle-kotlin": "build.gradle.kts",
        "npm": "package.json",
        "yarn-classic": "package.json",
        "yarn-berry": "package.json",
        "pnpm": "package.json"
    }
    manifest = manifest_map.get(runtime)
    if not manifest:
        print(f"Unknown or unsupported runtime: {runtime}", file=sys.stderr)
        sys.exit(1)
    return manifest

def get_package_manager(runtime: str) -> str:
    """Get the package manager name based on runtime."""
    runtime = runtime.lower()
    
    if runtime.startswith("syft"):
        print(f"TODO: Implement Integration Test support for {runtime}")
        sys.exit(0)
    
    # Handle Go runtimes
    if runtime.startswith('go'):
        return "go"
    
    # Handle Python runtimes
    if runtime.startswith('python'):
        return "pip"
    
    package_manager_map = {
        "npm": "npm",
        "yarn-classic": "yarn",
        "yarn-berry": "yarn",
        "pnpm": "pnpm",
        "maven": "mvn",
        "gradle-groovy": "gradle",
        "gradle-kotlin": "gradle"
    }
    package_manager = package_manager_map.get(runtime)
    if not package_manager:
        print(f"Unknown or unsupported runtime: {runtime}", file=sys.stderr)
        sys.exit(1)
    return package_manager

def get_scenario_base_dir(runtime: str) -> str:
    """Get the base directory for scenarios based on runtime."""
    runtime = runtime.lower()

    # Handle Python runtimes
    if runtime.startswith('python'):
        return "python-pip"
    
    if runtime.startswith("go"):
        return "go"
    
    return runtime

def get_commands(language: str, cli_dir: str, scenario_dir: str, manifest: str) -> List[str]:
    """Get the commands to run for a scenario."""
    commands = []
    
    # Convert paths to Path objects and resolve to ensure proper cross-platform handling
    cli_path = Path(cli_dir).resolve()
    scenario_path = Path(scenario_dir).resolve()
    manifest_path = scenario_path / manifest
    
    if language == "javascript":
        # For file:// URLs, we need forward slashes even on Windows
        cli_url_path = cli_path.as_posix()
        manifest_arg = str(manifest_path)
        
        commands.extend([
            f"npx --yes file:///{cli_url_path}/cli.tgz component {manifest_arg}",
            f"npx --yes file:///{cli_url_path}/cli.tgz stack {manifest_arg}",
            f"npx --yes file:///{cli_url_path}/cli.tgz stack {manifest_arg} --summary",
            f"npx --yes file:///{cli_url_path}/cli.tgz stack {manifest_arg} --html"
        ])
    elif language == "java":
        cli_jar = cli_path / "cli.jar"
        manifest_arg = str(manifest_path)
        
        commands.extend([
            f"java -jar {cli_jar} component {manifest_arg}",
            f"java -jar {cli_jar} stack {manifest_arg}",
            f"java -jar {cli_jar} stack {manifest_arg} --summary",
            f"java -jar {cli_jar} stack {manifest_arg} --html"
        ])
    else:
        print(f"Unknown language: {language}", file=sys.stderr)
        sys.exit(1)
    
    return commands 