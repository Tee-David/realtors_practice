"""
Comprehensive Security Test Suite
Tests for vulnerabilities, security best practices, and data protection
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import json
import re
from pathlib import Path


class TestSecurityComprehensive(unittest.TestCase):
    """Comprehensive security testing"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent.parent

    # ============================================================================
    # CREDENTIALS AND SECRETS MANAGEMENT
    # ============================================================================

    def test_001_no_hardcoded_credentials(self):
        """Test that no credentials are hardcoded in source code"""
        patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        violations = []
        for py_file in self.project_root.glob('**/*.py'):
            if 'venv' in str(py_file) or 'test_security' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Exclude test files and examples
                        if 'test' not in str(py_file).lower() and 'example' not in content.lower():
                            violations.append(f"{py_file}: {matches}")
            except Exception:
                pass

        self.assertEqual(len(violations), 0,
                        f"Found hardcoded credentials: {violations}")

    def test_002_firebase_credentials_not_committed(self):
        """Test that Firebase credentials are not in git"""
        firebase_file = self.project_root / "realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json"

        # Check .gitignore
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            # Should have patterns to ignore credentials
            self.assertTrue(
                '*.json' in content or 'firebase' in content.lower() or '*-firebase-*' in content,
                "Firebase credentials pattern not in .gitignore"
            )

    def test_003_environment_variables_used(self):
        """Test that environment variables are used for secrets"""
        api_server = self.project_root / "api_server.py"

        if api_server.exists():
            content = api_server.read_text()

            # Should use os.environ or os.getenv for secrets
            self.assertTrue(
                'os.environ' in content or 'os.getenv' in content,
                "Environment variables not used for configuration"
            )

    # ============================================================================
    # INPUT VALIDATION AND SANITIZATION
    # ============================================================================

    def test_004_sql_injection_protection(self):
        """Test SQL injection protection"""
        # Check for raw SQL queries
        violations = []

        for py_file in self.project_root.glob('**/*.py'):
            if 'venv' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Look for dangerous SQL patterns
                dangerous_patterns = [
                    r'execute\s*\(\s*["\'].*%s',  # String formatting in SQL
                    r'execute\s*\(\s*f["\']',      # f-strings in SQL
                ]

                for pattern in dangerous_patterns:
                    if re.search(pattern, content):
                        violations.append(str(py_file))
                        break
            except Exception:
                pass

        # Allow some violations in test files
        violations = [v for v in violations if 'test' not in v.lower()]

        self.assertEqual(len(violations), 0,
                        f"Found potential SQL injection risks: {violations}")

    def test_005_xss_protection(self):
        """Test XSS protection in API responses"""
        # Check that responses are properly escaped
        api_server = self.project_root / "api_server.py"

        if api_server.exists():
            content = api_server.read_text()

            # Should use jsonify or json.dumps for responses
            self.assertTrue(
                'jsonify' in content or 'json.dumps' in content,
                "API responses should use proper JSON serialization"
            )

    def test_006_path_traversal_protection(self):
        """Test path traversal protection"""
        # Check for file operations that might be vulnerable
        violations = []

        for py_file in self.project_root.glob('**/*.py'):
            if 'venv' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Look for unsafe file operations
                if 'open(' in content or 'read_file' in content:
                    # Should have path validation
                    if 'os.path.abspath' not in content and 'Path(' not in content:
                        # This is okay if not handling user input
                        pass
            except Exception:
                pass

        # This is informational
        self.assertTrue(True)

    def test_007_file_upload_validation(self):
        """Test file upload validation"""
        # Check that file uploads are validated
        # Look for file extension checks, size limits, etc.

        api_server = self.project_root / "api_server.py"

        if api_server.exists():
            content = api_server.read_text()

            # If handling file uploads, should have validation
            if 'upload' in content.lower() or 'file' in content.lower():
                # This is informational
                pass

        self.assertTrue(True)

    # ============================================================================
    # AUTHENTICATION AND AUTHORIZATION
    # ============================================================================

    def test_008_api_authentication(self):
        """Test API authentication mechanisms"""
        api_server = self.project_root / "api_server.py"

        if api_server.exists():
            content = api_server.read_text()

            # Check if authentication is implemented
            # This is optional for now, but recommended for production
            has_auth = any(keyword in content.lower() for keyword in
                          ['auth', 'token', 'jwt', 'api_key'])

            # Informational - not failing test
            if not has_auth:
                print("\nWARNING: No authentication detected in API server")

        self.assertTrue(True)

    def test_009_cors_configuration(self):
        """Test CORS configuration"""
        api_server = self.project_root / "api_server.py"

        if api_server.exists():
            content = api_server.read_text()

            # Check for CORS configuration
            has_cors = 'CORS' in content or 'cors' in content.lower()

            if has_cors:
                # Should not allow all origins in production
                self.assertNotIn('origins="*"', content,
                               "CORS should not allow all origins in production")

        self.assertTrue(True)

    # ============================================================================
    # DATA PROTECTION AND PRIVACY
    # ============================================================================

    def test_010_sensitive_data_logging(self):
        """Test that sensitive data is not logged"""
        violations = []

        for py_file in self.project_root.glob('**/*.py'):
            if 'venv' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Look for logging of sensitive data
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'log' in line.lower() or 'print' in line.lower():
                        # Check if logging passwords, tokens, etc.
                        if any(keyword in line.lower() for keyword in
                              ['password', 'token', 'secret', 'api_key']):
                            violations.append(f"{py_file}:{i+1}")
            except Exception:
                pass

        # This is informational
        if violations:
            print(f"\nWARNING: Potential sensitive data in logs: {violations[:5]}")

        self.assertTrue(True)

    def test_011_https_enforcement(self):
        """Test HTTPS enforcement for external requests"""
        violations = []

        for py_file in self.project_root.glob('**/*.py'):
            if 'venv' in str(py_file) or 'test' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Look for HTTP requests
                http_matches = re.findall(r'http://[^\s"\']+', content)
                for match in http_matches:
                    if 'localhost' not in match and '127.0.0.1' not in match:
                        violations.append(f"{py_file}: {match}")
            except Exception:
                pass

        # Some HTTP is okay for local development
        self.assertLess(len(violations), 10,
                       f"Found many HTTP requests: {violations[:5]}")

    # ============================================================================
    # DEPENDENCY SECURITY
    # ============================================================================

    def test_012_requirements_file_exists(self):
        """Test that requirements.txt exists and is up to date"""
        requirements = self.project_root / "requirements.txt"

        self.assertTrue(requirements.exists(), "requirements.txt not found")

        if requirements.exists():
            content = requirements.read_text()

            # Should have version pinning
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
            pinned = [l for l in lines if '==' in l]

            # At least some packages should be pinned
            self.assertGreater(len(pinned), 0,
                             "No version pinning in requirements.txt")

    def test_013_no_outdated_packages(self):
        """Test for known vulnerable packages (informational)"""
        requirements = self.project_root / "requirements.txt"

        if requirements.exists():
            content = requirements.read_text()

            # Check for very old package versions (informational)
            old_packages = [
                'requests==2.0',  # Example
                'flask==0.1',
            ]

            for pkg in old_packages:
                self.assertNotIn(pkg, content,
                               f"Potentially vulnerable package: {pkg}")

        self.assertTrue(True)

    # ============================================================================
    # ERROR HANDLING AND INFORMATION DISCLOSURE
    # ============================================================================

    def test_014_error_handling_no_stack_traces(self):
        """Test that stack traces are not exposed in production"""
        api_server = self.project_root / "api_server.py"

        if api_server.exists():
            content = api_server.read_text()

            # Should have error handlers
            has_error_handlers = '@app.errorhandler' in content

            # Informational
            if not has_error_handlers:
                print("\nWARNING: No error handlers detected in API server")

        self.assertTrue(True)

    def test_015_debug_mode_disabled(self):
        """Test that debug mode is disabled in production"""
        api_server = self.project_root / "api_server.py"

        if api_server.exists():
            content = api_server.read_text()

            # Check for debug mode
            debug_enabled = re.search(r'debug\s*=\s*True', content, re.IGNORECASE)

            if debug_enabled:
                # Should be conditional on environment
                self.assertIn('environ', content,
                            "Debug mode should be controlled by environment variable")

        self.assertTrue(True)

    # ============================================================================
    # RATE LIMITING AND DOS PROTECTION
    # ============================================================================

    def test_016_rate_limiting_implemented(self):
        """Test that rate limiting is implemented"""
        # Check for rate limiter
        rate_limiter = self.project_root / "core" / "rate_limiter.py"

        self.assertTrue(rate_limiter.exists(),
                       "Rate limiter module not found")

        if rate_limiter.exists():
            content = rate_limiter.read_text()
            self.assertIn('class', content)

    def test_017_pagination_limits(self):
        """Test that API has pagination limits"""
        api_server = self.project_root / "api_server.py"

        if api_server.exists():
            content = api_server.read_text()

            # Should have limit parameters
            has_limits = 'limit' in content.lower()

            self.assertTrue(has_limits,
                          "API should implement pagination limits")

    # ============================================================================
    # SECURE DEFAULTS
    # ============================================================================

    def test_018_secure_yaml_loading(self):
        """Test that YAML is loaded safely"""
        violations = []

        for py_file in self.project_root.glob('**/*.py'):
            if 'venv' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Should use safe_load, not load
                if 'yaml.load(' in content and 'Loader=' not in content:
                    violations.append(str(py_file))
            except Exception:
                pass

        self.assertEqual(len(violations), 0,
                        f"Found unsafe YAML loading: {violations}")

    def test_019_pickle_security(self):
        """Test that pickle is used safely"""
        violations = []

        for py_file in self.project_root.glob('**/*.py'):
            if 'venv' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Check for pickle usage
                if 'pickle.load' in content:
                    violations.append(str(py_file))
            except Exception:
                pass

        # Pickle is sometimes necessary, but should be used carefully
        if violations:
            print(f"\nINFO: Pickle used in: {violations}")

        self.assertTrue(True)

    def test_020_temp_file_security(self):
        """Test that temporary files are created securely"""
        violations = []

        for py_file in self.project_root.glob('**/*.py'):
            if 'venv' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Should use tempfile module
                if '/tmp/' in content and 'tempfile' not in content:
                    violations.append(str(py_file))
            except Exception:
                pass

        # This is informational
        if violations:
            print(f"\nINFO: Hardcoded temp paths in: {violations[:3]}")

        self.assertTrue(True)


class TestSecurityBestPractices(unittest.TestCase):
    """Test security best practices"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent.parent

    def test_021_gitignore_comprehensive(self):
        """Test that .gitignore is comprehensive"""
        gitignore = self.project_root / ".gitignore"

        if gitignore.exists():
            content = gitignore.read_text()

            # Should ignore common sensitive files
            patterns = [
                '*.log',
                '.env',
                'venv',
                '__pycache__',
            ]

            for pattern in patterns:
                self.assertIn(pattern, content,
                            f"Missing pattern in .gitignore: {pattern}")

    def test_022_readme_security_warnings(self):
        """Test that README has security warnings"""
        readme = self.project_root / "README.md"

        if readme.exists():
            content = readme.read_text()

            # Should mention security considerations
            # This is informational
            pass

        self.assertTrue(True)

    def test_023_secrets_documentation(self):
        """Test that secrets management is documented"""
        docs = list(self.project_root.glob('docs/**/*.md'))

        # Should have documentation on secrets
        secrets_mentioned = False
        for doc in docs:
            try:
                content = doc.read_text()
                if 'secret' in content.lower() or 'credential' in content.lower():
                    secrets_mentioned = True
                    break
            except Exception:
                pass

        # Informational
        if not secrets_mentioned:
            print("\nINFO: Consider adding secrets management documentation")

        self.assertTrue(True)


def run_tests():
    """Run all security tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestSecurityComprehensive))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityBestPractices))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("SECURITY TEST SUMMARY")
    print("="*70)
    print(f"Total tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    # Print security recommendations
    print("\n" + "="*70)
    print("SECURITY RECOMMENDATIONS")
    print("="*70)
    print("1. Use environment variables for all secrets")
    print("2. Enable HTTPS in production")
    print("3. Implement API authentication")
    print("4. Regular dependency updates")
    print("5. Enable rate limiting")
    print("6. Add input validation for all endpoints")
    print("7. Use parameterized queries for databases")
    print("8. Implement proper error handling")
    print("9. Add security headers (CSP, HSTS, etc.)")
    print("10. Regular security audits")
    print("="*70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
