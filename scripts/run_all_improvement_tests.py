"""
Run all improvement tests

Runs tests for all completed improvements and reports results.

Author: Tee-David
Date: 2025-10-20
"""

import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_tests():
    """Run all improvement test suites"""

    test_files = [
        'test_incremental_scraping.py',
        'test_duplicate_detector.py',
        'test_quality_scorer.py',
        'test_saved_searches.py',
        'test_scheduler_logic.py',
        'test_health_monitor.py'
    ]

    print("\n" + "=" * 80)
    print(" COMPREHENSIVE IMPROVEMENT TEST SUITE")
    print("=" * 80)

    results = {}
    passed_count = 0
    failed_count = 0

    for test_file in test_files:
        test_path = Path(__file__).parent.parent / 'tests' / test_file

        print(f"\nRunning {test_file}...")

        try:
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                results[test_file] = 'PASS'
                passed_count += 1
                print(f"  [PASS]")
            else:
                results[test_file] = 'FAIL'
                failed_count += 1
                print(f"  [FAIL]")
                if result.stderr:
                    print(f"  Error: {result.stderr[:200]}")

        except subprocess.TimeoutExpired:
            results[test_file] = 'TIMEOUT'
            failed_count += 1
            print(f"  [TIMEOUT]")
        except Exception as e:
            results[test_file] = f'ERROR: {e}'
            failed_count += 1
            print(f"  [ERROR]: {e}")

    # Print summary
    print("\n" + "=" * 80)
    print(" TEST SUMMARY")
    print("=" * 80)

    for test_file, status in results.items():
        status_symbol = "[+]" if status == "PASS" else "[-]"
        print(f"{status_symbol} {test_file}: {status}")

    print("\n" + "-" * 80)
    print(f"Total: {len(test_files)} test suites")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Success Rate: {passed_count/len(test_files)*100:.1f}%")
    print("=" * 80)

    return failed_count == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
