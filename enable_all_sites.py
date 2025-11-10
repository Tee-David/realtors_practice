"""
Enable all sites in config.yaml for full scrape.
"""

import yaml

def enable_all_sites():
    """Enable all sites in config.yaml."""
    config_path = 'config.yaml'

    # Read config
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    if 'sites' not in config:
        print("[ERROR] No sites section in config.yaml")
        return False

    # Enable all sites
    enabled_count = 0
    for site_key, site_config in config['sites'].items():
        if not site_config.get('enabled', False):
            site_config['enabled'] = True
            enabled_count += 1

    # Write back to config
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    total_sites = len(config['sites'])
    print(f"[SUCCESS] Enabled {enabled_count} sites")
    print(f"[INFO] Total sites now enabled: {total_sites}")

    return True

if __name__ == '__main__':
    print("=" * 60)
    print("ENABLING ALL SITES IN CONFIG.YAML")
    print("=" * 60)
    print()

    success = enable_all_sites()

    print()
    if success:
        print("[SUCCESS] All sites enabled!")
    else:
        print("[ERROR] Failed to enable sites")
