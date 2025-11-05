"""
Check GitHub Actions workflow configurations for potential issues
"""
import yaml
import os
from pathlib import Path

def check_workflow_file(file_path):
    """Check a single workflow file for common issues"""
    print(f"\n{'='*80}")
    print(f"Checking: {file_path.name}")
    print('='*80)

    issues = []
    warnings = []

    try:
        with open(file_path, 'r') as f:
            workflow = yaml.safe_load(f)

        # Check 1: Valid YAML
        print("[OK] Valid YAML syntax")

        # Check 2: Has jobs
        if 'jobs' not in workflow:
            issues.append("Missing 'jobs' key")
        else:
            print(f"[OK] Found {len(workflow['jobs'])} job(s)")

            # Check each job
            for job_name, job_config in workflow['jobs'].items():
                print(f"\n  Job: {job_name}")

                # Check runner
                if 'runs-on' in job_config:
                    print(f"    [OK] Runner: {job_config['runs-on']}")
                else:
                    issues.append(f"Job '{job_name}' missing 'runs-on'")

                # Check steps
                if 'steps' in job_config:
                    print(f"    [OK] Steps: {len(job_config['steps'])}")

                    # Check for Playwright installation
                    for step in job_config['steps']:
                        step_name = step.get('name', 'Unnamed step')

                        if 'playwright' in step_name.lower():
                            print(f"    [OK] Playwright step found: {step_name}")

                        # Check for Python setup
                        if 'uses' in step and 'setup-python' in step['uses']:
                            python_version = step.get('with', {}).get('python-version', 'not specified')
                            print(f"    [OK] Python version: {python_version}")

                        # Check for dependency installation
                        if 'run' in step and 'pip install' in step['run']:
                            print(f"    [OK] Dependencies installation step found")

                            # Check if requirements.txt is used
                            if 'requirements.txt' in step['run']:
                                if os.path.exists('requirements.txt'):
                                    print(f"    [OK] requirements.txt exists")
                                else:
                                    issues.append("requirements.txt referenced but not found")

                # Check for secrets
                if 'env' in job_config:
                    secrets_used = [k for k, v in job_config['env'].items() if isinstance(v, str) and 'secrets.' in v]
                    if secrets_used:
                        print(f"    [WARN] Secrets used: {', '.join(secrets_used)}")
                        warnings.append(f"Job '{job_name}' uses secrets - ensure they're configured in GitHub")

        # Check 3: Trigger configuration
        if 'on' in workflow:
            triggers = workflow['on']
            if isinstance(triggers, dict):
                print(f"\n[OK] Triggers: {', '.join(triggers.keys())}")
            else:
                print(f"\n[OK] Trigger: {triggers}")
        else:
            warnings.append("No trigger ('on') defined")

        # Check 4: Common Playwright issues
        workflow_str = str(workflow)
        if 'playwright' in workflow_str.lower():
            print("\n[WARN] Playwright detected - Common issues:")
            print("  1. Need to run: playwright install")
            print("  2. Need system dependencies: playwright install-deps")
            print("  3. Headless mode should be enabled in CI")

            if 'playwright install-deps' in workflow_str:
                print("  [OK] playwright install-deps found")
            else:
                warnings.append("Missing 'playwright install-deps' - may fail on Linux runners")

            if 'playwright install' in workflow_str:
                print("  [OK] playwright install found")
            else:
                warnings.append("Missing 'playwright install' - browsers not installed")

        # Summary
        print(f"\n{'-'*80}")
        if issues:
            print(f"[ERROR] ISSUES ({len(issues)}):")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("[OK] No critical issues found")

        if warnings:
            print(f"\n[WARN]  WARNINGS ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning}")

        return issues, warnings

    except yaml.YAMLError as e:
        print(f"[ERROR] YAML parsing error: {e}")
        return [f"YAML error: {e}"], []
    except Exception as e:
        print(f"[ERROR] Error checking workflow: {e}")
        return [f"Error: {e}"], []

def check_requirements():
    """Check if requirements.txt exists and has necessary packages"""
    print(f"\n{'='*80}")
    print("Checking requirements.txt")
    print('='*80)

    if not os.path.exists('requirements.txt'):
        print("[ERROR] requirements.txt not found")
        return False

    with open('requirements.txt', 'r') as f:
        requirements = f.read()

    required_packages = ['playwright', 'pyyaml', 'requests', 'pandas', 'openpyxl']
    missing = []

    for package in required_packages:
        if package.lower() in requirements.lower():
            print(f"[OK] {package} found")
        else:
            missing.append(package)
            print(f"[WARN] {package} not found")

    if missing:
        print(f"\n[WARN]  Missing packages: {', '.join(missing)}")
        return False

    return True

def main():
    print("\n" + "="*80)
    print("GitHub Actions Workflow Diagnostics")
    print("="*80)

    # Check workflows directory
    workflows_dir = Path('.github/workflows')
    if not workflows_dir.exists():
        print("[ERROR] .github/workflows directory not found")
        return

    # Get all workflow files
    workflow_files = list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))

    if not workflow_files:
        print("[ERROR] No workflow files found")
        return

    print(f"\nFound {len(workflow_files)} workflow file(s)")

    # Check each workflow
    all_issues = []
    all_warnings = []

    for workflow_file in workflow_files:
        issues, warnings = check_workflow_file(workflow_file)
        all_issues.extend(issues)
        all_warnings.extend(warnings)

    # Check requirements.txt
    check_requirements()

    # Final summary
    print(f"\n{'='*80}")
    print("OVERALL SUMMARY")
    print('='*80)
    print(f"Total workflow files: {len(workflow_files)}")
    print(f"Total issues: {len(all_issues)}")
    print(f"Total warnings: {len(all_warnings)}")

    if all_issues:
        print("\n[ERROR] CRITICAL ISSUES - These will cause failures:")
        for issue in set(all_issues):
            print(f"  - {issue}")

    if all_warnings:
        print("\n[WARN]  WARNINGS - May cause issues:")
        for warning in set(all_warnings):
            print(f"  - {warning}")

    if not all_issues and not all_warnings:
        print("\n[OK] All workflows look good!")

    # Common fixes
    print(f"\n{'='*80}")
    print("COMMON FIXES FOR GITHUB ACTIONS FAILURES")
    print('='*80)
    print("""
1. Playwright Browser Installation Issues:
   - Add these steps BEFORE running scraper:
     ```yaml
     - name: Install Playwright browsers
       run: playwright install chromium

     - name: Install system dependencies
       run: playwright install-deps
     ```

2. Missing Dependencies:
   - Ensure requirements.txt includes all packages
   - Install with: pip install -r requirements.txt

3. Timeout Issues:
   - Set reasonable timeouts: timeout-minutes: 30
   - Use page caps to limit scraping: RP_PAGE_CAP=10

4. Memory Issues:
   - Use ubuntu-latest runner (has more memory)
   - Scrape fewer sites in parallel
   - Clear caches between runs

5. Environment Variables:
   - Set RP_HEADLESS=1 for CI environments
   - Use RP_NO_AUTO_WATCHER=1 to skip watcher
   - Set reasonable limits: RP_PAGE_CAP=20

6. Secrets Configuration:
   - Go to: Settings > Secrets and variables > Actions
   - Add required secrets (API keys, tokens, etc.)
""")

if __name__ == "__main__":
    main()
