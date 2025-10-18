# validate_config.py
"""
Config Validation CLI Tool

Validates config.yaml and reports any errors or warnings.
Useful for checking config before deployment or committing changes.

Usage:
    python scripts/validate_config.py [config_file]

Examples:
    python scripts/validate_config.py
    python scripts/validate_config.py config.yaml
    python scripts/validate_config.py config.example.yaml
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config_loader import load_config, ConfigValidationError


def validate_config_file(config_path: str) -> bool:
    """
    Validate a config file and print results.

    Returns:
        True if valid, False if invalid
    """
    print("=" * 70)
    print(f"VALIDATING: {config_path}")
    print("=" * 70)

    # Check file exists
    if not Path(config_path).exists():
        print(f"\n[ERROR] File not found: {config_path}")
        return False

    # Try to load config
    try:
        config = load_config(config_path, use_cache=False)
    except ConfigValidationError as e:
        print(f"\n[VALIDATION FAILED]")
        print(f"  {e}")
        return False
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

    # Config is valid
    total, enabled = config.count_sites()
    all_sites = config.get_all_sites()
    enabled_sites = config.get_enabled_sites()

    print(f"\n[VALIDATION PASSED]")
    print(f"\n  Sites:")
    print(f"    Total: {total}")
    print(f"    Enabled: {enabled}")
    print(f"    Disabled: {total - enabled}")

    # Check parser distribution
    parser_counts = {}
    for site_key, site_config in all_sites.items():
        parser = site_config.get("parser", "specials")
        parser_counts[parser] = parser_counts.get(parser, 0) + 1

    print(f"\n  Parser types:")
    for parser_type, count in sorted(parser_counts.items()):
        print(f"    {parser_type}: {count}")

    # Check for sites with custom selectors
    sites_with_selectors = [k for k, v in all_sites.items() if "selectors" in v]
    print(f"\n  Custom selectors: {len(sites_with_selectors)} sites")

    # Check for sites with overrides
    sites_with_overrides = [k for k, v in all_sites.items() if "overrides" in v]
    print(f"  Per-site overrides: {len(sites_with_overrides)} sites")

    # Check for sites with Lagos paths
    sites_with_lagos = [k for k, v in all_sites.items() if "lagos_paths" in v]
    print(f"  Lagos-specific paths: {len(sites_with_lagos)} sites")

    # Warnings
    warnings = []

    # Warn if all sites are disabled
    if enabled == 0:
        warnings.append("All sites are disabled - scraper will do nothing")

    # Warn if most sites are disabled
    if total > 0 and enabled < (total * 0.5):
        warnings.append(f"More than 50% of sites are disabled ({total - enabled}/{total})")

    # Warn if custom parser modules don't exist
    custom_sites = [k for k, v in all_sites.items() if v.get("parser") == "custom"]
    for site_key in custom_sites:
        module_path = Path(f"parsers/{site_key}.py")
        if not module_path.exists():
            warnings.append(f"Custom parser module not found: {module_path}")

    # Display warnings
    if warnings:
        print(f"\n[WARNINGS]")
        for warning in warnings:
            print(f"  - {warning}")

    # Global settings summary
    global_settings = config.get_global_settings()
    print(f"\n  Global settings:")
    print(f"    Fallback order: {' -> '.join(global_settings['fallback_order'])}")
    print(f"    Geocoding: {'enabled' if global_settings['geocoding']['enabled'] else 'disabled'}")
    print(f"    Max pages: {global_settings['pagination']['max_pages']}")
    print(f"    Export formats: {', '.join(global_settings['export']['formats'])}")

    print(f"\n" + "=" * 70)
    print(f"[SUCCESS] Configuration is valid!")
    print("=" * 70)

    return True


def main():
    """Main entry point."""
    # Get config path from command line or use default
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "config.yaml"

    # Validate config
    is_valid = validate_config_file(config_path)

    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
