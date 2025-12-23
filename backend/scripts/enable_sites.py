# enable_sites.py
"""
Enable multiple sites for testing.

Usage:
    python enable_sites.py npc propertypro property24 jiji lamudi
"""

import sys
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def enable_sites(site_keys: list):
    """Enable specified sites, disable all others."""
    config_path = Path("config.yaml")

    # Load config
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Check all sites exist
    missing = [key for key in site_keys if key not in config["sites"]]
    if missing:
        print(f"ERROR: Sites not found: {', '.join(missing)}")
        print("\nAvailable sites:")
        for key in sorted(config["sites"].keys())[:15]:
            print(f"  - {key}")
        sys.exit(1)

    # Enable specified sites, disable others
    for key in config["sites"].keys():
        config["sites"][key]["enabled"] = (key in site_keys)

    # Save config
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"[OK] Enabled {len(site_keys)} sites:")
    for key in site_keys:
        site_name = config["sites"][key].get("name", key)
        print(f"  [+] {key} - {site_name}")

    print(f"\n[OK] Disabled {len(config['sites']) - len(site_keys)} other sites")
    print(f"\nReady to scrape! Run: python main.py")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enable_sites.py site1 site2 site3 ...")
        print("\nExample:")
        print("  python enable_sites.py npc propertypro property24 jiji lamudi")
        sys.exit(1)

    site_keys = sys.argv[1:]
    enable_sites(site_keys)
