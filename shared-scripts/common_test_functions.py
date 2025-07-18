#!/usr/bin/env python3

import os
import sys
import platform
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

def get_env_var_name(runtime: str) -> str:
    """Get the environment variable name for the runtime."""
    package_manager = get_package_manager(runtime)
    return f"EXHORT_{package_manager.upper()}_PATH"

def get_commands(language: str, cli_dir: str, scenario_dir: str, manifest: str) -> List[str]:
    """Get the commands to run for a scenario."""
    commands = []
    
    if language == "javascript":
        # Convert CLI_DIR to absolute path and normalize for Windows
        cli_dir = str(Path(cli_dir).absolute())
        if platform.system() == "Windows":
            # For Windows, convert to proper drive letter format
            if cli_dir.startswith("/") and len(cli_dir) > 2 and cli_dir[2] == "/":
                drive_letter = cli_dir[1]
                rest_of_path = cli_dir[3:]
                cli_dir = f"{drive_letter}:/{rest_of_path}"
        
        commands.extend([
            f"npx --yes file:///{cli_dir}/cli.tgz component {scenario_dir}/{manifest}",
            f"npx --yes file:///{cli_dir}/cli.tgz stack {scenario_dir}/{manifest}",
            f"npx --yes file:///{cli_dir}/cli.tgz stack {scenario_dir}/{manifest} --summary",
            f"npx --yes file:///{cli_dir}/cli.tgz stack {scenario_dir}/{manifest} --html"
        ])
    elif language == "java":
        commands.extend([
            f"java -jar {cli_dir}/cli.jar component {scenario_dir}/{manifest}",
            f"java -jar {cli_dir}/cli.jar stack {scenario_dir}/{manifest}",
            f"java -jar {cli_dir}/cli.jar stack {scenario_dir}/{manifest} --summary",
            f"java -jar {cli_dir}/cli.jar stack {scenario_dir}/{manifest} --html"
        ])
    else:
        print(f"Unknown language: {language}", file=sys.stderr)
        sys.exit(1)
    
    return commands 