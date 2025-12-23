"""
Config Manager - Manage config.yaml programmatically
"""
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import logging
from core.config_loader import load_config, ConfigValidationError

logger = logging.getLogger(__name__)


class ConfigManager:
    """Helper class to manage config.yaml"""

    def __init__(self):
        self.config_path = Path("config.yaml")

    def _load_yaml(self) -> Dict:
        """Load config.yaml as dict"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _save_yaml(self, data: Dict):
        """Save dict to config.yaml"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def list_sites(self) -> Dict:
        """List all sites with their configurations"""
        try:
            config = load_config(str(self.config_path))
            sites = config.get_all_sites()

            result = {
                'total': len(sites),
                'enabled': len([s for s in sites.values() if s.get('enabled', False)]),
                'disabled': len([s for s in sites.values() if not s.get('enabled', False)]),
                'sites': []
            }

            for site_key, site_config in sites.items():
                result['sites'].append({
                    'site_key': site_key,
                    'name': site_config.get('name', site_key),
                    'url': site_config.get('url', ''),
                    'enabled': site_config.get('enabled', False),
                    'parser': site_config.get('parser', 'specials')
                })

            return result

        except Exception as e:
            logger.error(f"Error listing sites: {e}")
            raise

    def get_site(self, site_key: str) -> Optional[Dict]:
        """Get configuration for specific site"""
        try:
            data = self._load_yaml()
            sites = data.get('sites', {})

            if site_key not in sites:
                return None

            site_config = sites[site_key]
            site_config['site_key'] = site_key

            return site_config

        except Exception as e:
            logger.error(f"Error getting site {site_key}: {e}")
            raise

    def add_site(self, site_data: Dict) -> Dict:
        """
        Add new site to config.yaml

        Args:
            site_data: Site configuration dict with required fields:
                - site_key: unique identifier
                - name: display name
                - url: site URL
                - enabled: boolean
                - parser: parser type (default 'specials')
        """
        try:
            site_key = site_data.get('site_key')
            if not site_key:
                raise ValueError("site_key is required")

            # Validate required fields
            required_fields = ['name', 'url']
            for field in required_fields:
                if field not in site_data:
                    raise ValueError(f"{field} is required")

            # Load current config
            data = self._load_yaml()
            sites = data.get('sites', {})

            # Check if site already exists
            if site_key in sites:
                raise ValueError(f"Site {site_key} already exists")

            # Prepare site config
            new_site = {
                'name': site_data['name'],
                'url': site_data['url'],
                'enabled': site_data.get('enabled', False),
                'parser': site_data.get('parser', 'specials')
            }

            # Add optional fields
            if 'selectors' in site_data:
                new_site['selectors'] = site_data['selectors']
            if 'pagination' in site_data:
                new_site['pagination'] = site_data['pagination']
            if 'lagos_paths' in site_data:
                new_site['lagos_paths'] = site_data['lagos_paths']
            if 'overrides' in site_data:
                new_site['overrides'] = site_data['overrides']

            # Add to config
            sites[site_key] = new_site
            data['sites'] = sites

            # Save config
            self._save_yaml(data)

            # Validate new config
            try:
                load_config(str(self.config_path))
            except ConfigValidationError as e:
                # Rollback if validation fails
                del sites[site_key]
                self._save_yaml(data)
                raise ValueError(f"Config validation failed: {e}")

            logger.info(f"Added new site: {site_key}")

            return {
                'success': True,
                'site_key': site_key,
                'message': f'Site {site_key} added successfully'
            }

        except Exception as e:
            logger.error(f"Error adding site: {e}")
            raise

    def update_site(self, site_key: str, updates: Dict) -> Dict:
        """
        Update existing site configuration

        Args:
            site_key: Site identifier
            updates: Dict of fields to update
        """
        try:
            data = self._load_yaml()
            sites = data.get('sites', {})

            if site_key not in sites:
                raise ValueError(f"Site {site_key} not found")

            # Update fields
            site_config = sites[site_key]
            for key, value in updates.items():
                if key != 'site_key':  # Don't allow changing site_key
                    site_config[key] = value

            sites[site_key] = site_config
            data['sites'] = sites

            # Save config
            self._save_yaml(data)

            # Validate new config
            try:
                load_config(str(self.config_path))
            except ConfigValidationError as e:
                raise ValueError(f"Config validation failed: {e}")

            logger.info(f"Updated site: {site_key}")

            return {
                'success': True,
                'site_key': site_key,
                'message': f'Site {site_key} updated successfully'
            }

        except Exception as e:
            logger.error(f"Error updating site {site_key}: {e}")
            raise

    def delete_site(self, site_key: str) -> Dict:
        """
        Delete site from config.yaml

        Args:
            site_key: Site identifier
        """
        try:
            data = self._load_yaml()
            sites = data.get('sites', {})

            if site_key not in sites:
                raise ValueError(f"Site {site_key} not found")

            # Remove site
            del sites[site_key]
            data['sites'] = sites

            # Save config
            self._save_yaml(data)

            logger.info(f"Deleted site: {site_key}")

            return {
                'success': True,
                'site_key': site_key,
                'message': f'Site {site_key} deleted successfully'
            }

        except Exception as e:
            logger.error(f"Error deleting site {site_key}: {e}")
            raise

    def toggle_site(self, site_key: str) -> Dict:
        """
        Toggle site enabled/disabled status

        Args:
            site_key: Site identifier
        """
        try:
            data = self._load_yaml()
            sites = data.get('sites', {})

            if site_key not in sites:
                raise ValueError(f"Site {site_key} not found")

            # Toggle enabled status
            current_status = sites[site_key].get('enabled', False)
            sites[site_key]['enabled'] = not current_status

            data['sites'] = sites

            # Save config
            self._save_yaml(data)

            new_status = 'enabled' if not current_status else 'disabled'
            logger.info(f"Toggled site {site_key}: {new_status}")

            return {
                'success': True,
                'site_key': site_key,
                'enabled': not current_status,
                'message': f'Site {site_key} {new_status}'
            }

        except Exception as e:
            logger.error(f"Error toggling site {site_key}: {e}")
            raise

    def get_global_settings(self) -> Dict:
        """Get global settings from config"""
        try:
            data = self._load_yaml()
            return data.get('global_settings', {})
        except Exception as e:
            logger.error(f"Error getting global settings: {e}")
            raise

    def update_global_settings(self, updates: Dict) -> Dict:
        """
        Update global settings

        Args:
            updates: Dict of settings to update
        """
        try:
            data = self._load_yaml()
            global_settings = data.get('global_settings', {})

            # Update settings
            for key, value in updates.items():
                global_settings[key] = value

            data['global_settings'] = global_settings

            # Save config
            self._save_yaml(data)

            # Validate new config
            try:
                load_config(str(self.config_path))
            except ConfigValidationError as e:
                raise ValueError(f"Config validation failed: {e}")

            logger.info("Updated global settings")

            return {
                'success': True,
                'message': 'Global settings updated successfully'
            }

        except Exception as e:
            logger.error(f"Error updating global settings: {e}")
            raise
