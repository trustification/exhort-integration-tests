# Coding Conventions

This document describes the coding conventions, project structure, test patterns, and build commands for the exhort-integration-tests repository.

## Language and Framework

- **Primary language:** Python 3.11+
- **Testing framework:** Custom Python test orchestration using subprocess calls
- **CI/CD:** GitHub Actions workflows
- **Supported ecosystems:** Maven, Gradle (Groovy & Kotlin), npm, pnpm, Yarn (Classic & Berry), pip, pyproject (pip/uv/poetry), Cargo, Go, Syft

## Code Style

### Python

- Follow PEP 8 conventions for Python code
- Use 4 spaces for indentation (no tabs)
- Use snake_case for function and variable names
- Use SCREAMING_SNAKE_CASE for constants
- Use descriptive variable names that convey purpose
- Use docstrings for module-level functions explaining their purpose and parameters

### Shell Scripts

- Use `#!/bin/bash` shebang for all shell scripts
- Use `set -e` to fail on errors
- Use descriptive variable names in UPPERCASE for environment variables
- Use lowercase for local variables
- Include comments explaining non-obvious logic

## Naming Conventions

### Files and Directories

- Python scripts: Use snake_case (e.g., `run_tests.py`, `common_test_functions.py`)
- Shell scripts: Use kebab-case (e.g., `setup-runtime.sh`, `print-runtime.sh`)
- Scenario directories: Use kebab-case matching ecosystem name (e.g., `maven/simple`, `gradle-kotlin/simple`, `python-pip/simple`)
- Spec files: Always named `spec.yaml` within each scenario directory

### Functions and Constants

- Python functions: Use snake_case and descriptive names (e.g., `validate_analysis`, `get_manifest_file`)
- Constants: Use SCREAMING_SNAKE_CASE (e.g., `VALID_LICENSE_CATEGORIES`, `VULN_SUMMARY_FIELDS`)
- Test validation functions: Prefix with `validate_` (e.g., `validate_licenses`, `validate_html_output`)

## File Organization

### Project Structure

```
exhort-integration-tests/
├── scenarios/           # Test scenarios organized by ecosystem (e.g. maven/, npm/, cargo/)
├── shared-scripts/      # Test orchestration scripts (Python + Bash)
└── .github/workflows/   # GitHub Actions CI workflows
```

### Scenario Directory Structure

Each scenario directory must contain:
- A manifest file appropriate for the ecosystem (e.g., `pom.xml`, `package.json`, `go.mod`)
- A `spec.yaml` file defining expected test results

## spec.yaml Format

Every scenario must have a `spec.yaml` file with the following structure:

```yaml
title: Simple Maven Scenario
description: Test a simple Maven project with a few dependencies.
expect_success: true

stack_analysis:
  scanned:
    direct: 5               # Number of direct dependencies (deterministic, must match manifest)
    transitive: 40          # Number of transitive dependencies (deterministic, must match resolved tree)
    transitive_windows: 42  # Optional: OS-specific override for Windows (if different from base)
  providers:
    rhtpa:
      sources:
        - osv-github
        - redhat-csaf
  licenses:
    expected_providers:
      - deps.dev

component_analysis:
  scanned:
    direct: 5          # Number of direct dependencies
    transitive: 0      # Component analysis typically scans only direct deps
  providers:
    rhtpa:
      sources:
        - osv-github
  licenses:
    expected_providers:
      - deps.dev

license_check:
  expect_success: true
```

### spec.yaml Required Fields

- `title`: Brief descriptive title of the scenario
- `description`: Longer description of what is being tested
- `expect_success`: Boolean indicating if commands should succeed (true) or fail (false)
- `stack_analysis`: Expected results for stack analysis command
  - `scanned.direct`: Number of direct dependencies (must match manifest exactly)
  - `scanned.transitive`: Number of transitive dependencies (must match resolved dependency tree)
  - `scanned.transitive_windows`: (Optional) OS-specific override for Windows
  - `scanned.transitive_linux`: (Optional) OS-specific override for Linux
  - `scanned.transitive_macos`: (Optional) OS-specific override for macOS
  - `providers.<provider_name>.sources`: List of expected data sources
  - `licenses.expected_providers`: List of expected license providers
- `component_analysis`: Expected results for component analysis command (same structure as stack_analysis)
- `license_check.expect_success`: Boolean for license command expectations

### Transitive Dependency Counts

The `transitive` count in `spec.yaml` must be **deterministic and exact**. To determine the correct value:

1. Build the scenario project with its native tooling (e.g., `mvn dependency:tree`, `npm install && npm ls`)
2. Count the actual transitive dependencies in the resolved dependency tree
3. Use that exact count in the spec — do not estimate or use placeholder values
4. If dependency counts change (e.g., after updating a dependency), update the spec to match

### OS-Specific Transitive Count Overrides

Some ecosystems have platform-specific dependencies (e.g., Python's `colorama` on Windows). When the transitive count varies by OS, use OS-specific override fields:

- `transitive_windows`: Override for Windows (platform.system() == "Windows")
- `transitive_linux`: Override for Linux (platform.system() == "Linux")
- `transitive_macos`: Override for macOS (platform.system() == "Darwin")

The test runner checks for an OS-specific override first (`transitive_<os>`), then falls back to the base `transitive` field. The base `transitive` field is still required — it serves as the default for any OS without an explicit override.

Example:
```yaml
stack_analysis:
  scanned:
    direct: 2
    transitive: 10          # Default for Linux/macOS
    transitive_windows: 11  # Windows pulls in colorama as a platform-specific dependency
```

**Important:** Only `transitive` counts support OS overrides. The `direct` count should NOT have OS-specific variants, as direct dependencies are declared in the manifest and do not vary by platform.

## Error Handling

### Python Scripts

- Use meaningful exit codes (0 for success, 1 for failure)
- Print clear error messages to stdout with descriptive prefixes (`FAIL`, `PASS`, `WARN`)
- Use `try-except` blocks for subprocess calls and JSON parsing
- Validate all required data structures before processing (check for missing keys, type mismatches)
- Return boolean values from validation functions to indicate pass/fail

### Shell Scripts

- Use `set -e` to exit immediately on error
- Check command availability before use (e.g., `command -v`)
- Print descriptive messages for each installation step
- Handle OS-specific logic with case statements

## Testing Conventions

### Test Structure

Tests are organized as scenarios, each consisting of:
1. A real manifest file for a specific ecosystem
2. A `spec.yaml` defining expected behavior
3. Commands executed by `run_tests.py` that invoke the Exhort CLI

### Validation Approach

Tests validate responses using **structural and invariant checks**:

1. **Structural checks**: Verify required fields exist (`scanned`, `providers`, `licenses`)
2. **Deterministic checks**: Verify counts match expected values exactly (direct dependencies, transitive dependencies)
3. **Invariant checks**: Verify mathematical relationships hold:
   - `total == direct + transitive` (dependency counts)
   - `total == critical + high + medium + low` (vulnerability counts)
   - `total == permissive + weakCopyleft + strongCopyleft + unknown` (license categories)
   - All counts must be non-negative
4. **Provider checks**: Verify expected providers are present and have `ok: true` status with `code: 200`
5. **Liveness checks**: Warn if vulnerability totals are zero (may indicate data source issues)

### Adding a New Ecosystem Test Scenario

To add a new test scenario for an existing or new ecosystem:

1. Create a scenario directory: `scenarios/<ecosystem>/simple/` (use kebab-case)
2. Add a minimal but representative manifest file:
   - Include both direct and transitive dependencies
   - Use real dependencies that are likely to have vulnerability data
   - Keep the project minimal (4-5 direct dependencies is typical)
3. Create a `spec.yaml` following the format above:
   - Determine exact dependency counts by building the project locally
   - List expected providers and sources based on ecosystem support
   - Set `expect_success: true` for valid scenarios
4. If adding a new ecosystem runtime:
   - Update `common_test_functions.py`:
     - Add manifest filename to `get_manifest_file()`
     - Add package manager to `get_package_manager()`
     - Add scenario base directory to `get_scenario_base_dir()`
   - Update `setup-runtime.sh` to install the ecosystem tooling if needed
   - Add the runtime to the GitHub Actions matrix in `.github/workflows/integration.yml`

### Test Output Format

Test validation functions print results with prefixes:
- `PASS` — Check passed
- `FAIL` — Check failed (test should fail)
- `WARN` — Potential issue (does not fail test)

Example output:
```
---
Scenario: Simple Maven Scenario
Description: Test a simple Maven project with a few dependencies.
Manifest: /path/to/scenarios/maven/simple/pom.xml
Expect success: true
Executing: java -jar cli.jar component pom.xml
  PASS Command succeeded as expected
Validating component analysis...
  PASS component_analysis structural and invariant checks passed
  PASS component_analysis license checks passed
---
```

## Commit Messages

Follow Conventional Commits specification:

- Format: `<type>[optional scope]: <description>`
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`
- Scope examples: `maven`, `npm`, `gradle`, `cargo`, `ci`, `scripts`
- Examples:
  - `feat(npm): add yarn-berry simple scenario`
  - `fix(scripts): correct transitive dependency count validation`
  - `test(go): update spec.yaml with correct dependency counts`
  - `ci: add windows runner to integration tests`

## Dependencies

### Python

The project uses minimal Python dependencies:
- `pyyaml` — For reading spec.yaml files
- No other external dependencies for core test scripts

Test scenarios may install ecosystem-specific dependencies as part of the test (e.g., `requests`, `numpy`, `pandas` for python-pip scenarios), but these are not project dependencies.

### Ecosystem Runtimes

Each ecosystem requires its native tooling installed:
- **Maven:** `mvn` (Java 17+)
- **Gradle:** `gradle` (Java 17+)
- **npm/pnpm:** `npm`, `pnpm` (Node.js 20+)
- **Yarn Classic:** `yarn` v1.x (Node.js 20+)
- **Yarn Berry:** `yarn` v4.x (Node.js 20+, using corepack)
- **Go:** `go` 1.21+ or latest
- **Python pip:** `pip` (Python 3.10+)
- **Cargo:** `cargo` (Rust stable)
- **Syft:** `syft` CLI

## CI Checks

### All CI Checks

Run all checks before committing:

```bash
# Verify Python syntax (no formal linter configured, but code should be valid)
python3 -m py_compile shared-scripts/*.py

# Run integration tests locally (requires CLI artifact and runtime)
python3 shared-scripts/run_tests.py <language> <cli_dir> <runtime>
```

### GitHub Actions Workflow

The integration workflow (`.github/workflows/integration.yml`) runs tests across:
- **Operating systems:** Ubuntu, Windows, macOS
- **Runtimes:** All supported ecosystems and versions
- **Test phases:**
  1. Build CLI artifact (Java or JavaScript)
  2. Setup runtime environment
  3. Run tests without runtime-specific setup (`run_tests_no_runtime.py`)
  4. Setup ecosystem runtimes (`setup-runtime.sh`)
  5. Run full integration tests (`run_tests.py`)

## Test Execution

### Local Test Execution

To run tests locally:

1. Build or obtain the Exhort CLI artifact (Java JAR or JavaScript tarball)
2. Ensure the target ecosystem runtime is installed (e.g., `mvn`, `npm`, `go`)
3. Set environment variables:
   ```bash
   export TRUSTIFY_DA_DEV_MODE=true
   export TRUSTIFY_DA_BACKEND_URL='https://exhort.stage.devshift.net'
   ```
4. Run tests for a specific ecosystem:
   ```bash
   python3 shared-scripts/run_tests.py java /path/to/cli maven
   python3 shared-scripts/run_tests.py javascript /path/to/cli npm
   ```

### Test Runner Arguments

- `<language>`: CLI language (`java` or `javascript`)
- `<cli_dir>`: Directory containing `cli.jar` (Java) or `cli.tgz` (JavaScript)
- `<runtime>`: Target ecosystem runtime (e.g., `maven`, `npm`, `go-latest`, `python-3.12-pip`)

### Commands Executed Per Scenario

For each scenario, the test runner executes:
1. `component <manifest>` — Component analysis (direct dependencies only)
2. `stack <manifest>` — Full stack analysis (direct + transitive)
3. `stack <manifest> --summary` — Stack analysis summary output
4. `stack <manifest> --html` — HTML report generation
5. `license <manifest>` — License mismatch detection

Each command's output is validated against the `spec.yaml` expectations.

## Code Quality

- Keep test scenarios minimal but representative
- Ensure spec.yaml dependency counts are deterministic and accurate
- Validate all invariants (mathematical relationships between fields)
- Print clear failure messages that identify the exact field or check that failed
- Avoid hardcoded assumptions about vulnerability data (counts may change as databases update)
- Use structural validation (fields exist, types correct) over exact value matching for non-deterministic data
