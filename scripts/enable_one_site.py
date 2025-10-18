# enable_one_site.py
"""
Quick utility to enable only one site for testing.

Usage:
    python enable_one_site.py npc
    python enable_one_site.py propertypro
"""

import sys
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def enable_one_site(site_key: str):
    """Enable only the specified site, disable all others."""
    config_path = Path("config.yaml")

    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Check if site exists
    if site_key not in config["sites"]:
        print(f"ERROR: Site '{site_key}' not found in config.yaml")
        print("\nAvailable sites:")
        for key in sorted(config["sites"].keys())[:15]:
            print(f"  - {key}")
        print("  - ... and more")
        sys.exit(1)

    # Disable all sites except the specified one
    for key in config["sites"].keys():
        config["sites"][key]["enabled"] = (key == site_key)

    # Save config
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    site_name = config["sites"][site_key].get("name", site_key)
    print(f"[OK] Enabled: {site_key} ({site_name})")
    print(f"[OK] Disabled: {len(config['sites']) - 1} other sites")
    print(f"\nReady to test! Run: python main.py")

def list_sites():
    """List all available sites."""
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print("Available sites:")
    for site_key, site_config in sorted(config["sites"].items()):
        enabled = "[ENABLED]" if site_config.get("enabled") else "[DISABLED]"
        name = site_config.get("name", site_key)
        print(f"  {enabled:<12} {site_key:<25} - {name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enable_one_site.py <site_key>")
        print("       python enable_one_site.py --list")
        print()
        list_sites()
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_sites()
    else:
        site_key = sys.argv[1]
        enable_one_site(site_key)
