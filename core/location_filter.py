"""
core/location_filter.py

Multi-location filtering for Nigerian properties.

Features:
- Support for multiple Nigerian cities (Lagos, Abuja, Port Harcourt, etc.)
- Configurable target locations via config or environment variable
- City boundary detection with coordinates
- Location string validation
- Integration with existing geocoding system

Usage:
    from core.location_filter import LocationFilter

    # Filter for Lagos only (default)
    filter = LocationFilter()

    # Filter for multiple cities
    filter = LocationFilter(target_locations=['Lagos', 'Abuja', 'Port Harcourt'])

    # Check if location is in target cities
    if filter.is_target_location("Lekki Phase 1"):
        # Process listing
        pass

    # Filter listings by location
    filtered = filter.filter_listings_by_location(listings)
"""

import os
import logging
from typing import List, Dict, Optional, Tuple, Set
from functools import lru_cache

logger = logging.getLogger(__name__)
RP_DEBUG = os.getenv("RP_DEBUG") == "1"


class LocationFilter:
    """
    Multi-location filtering for Nigerian properties.

    Supports filtering for any Nigerian city/state with configurable target locations.
    """

    # Nigerian city data: bounding boxes and known areas
    CITY_DATA = {
        'Lagos': {
            'bounds': {
                'min_lat': 6.3876, 'max_lat': 6.7027,
                'min_lon': 3.0982, 'max_lon': 3.6964,
            },
            'areas': {
                # Islands
                'victoria island', 'vi', 'ikoyi', 'banana island', 'lekki', 'ajah', 'badore',
                'epe', 'sangotedo', 'awoyaya', 'lakowe', 'ibeju-lekki', 'chevron',
                'oniru', 'osapa', 'agungi', 'ilasan', 'ikate', 'oral estate',
                # Mainland
                'ikeja', 'surulere', 'yaba', 'ebute metta', 'mushin', 'apapa', 'ajegunle',
                'mainland', 'lagos mainland', 'festac', 'isolo', 'oshodi', 'ojota',
                'maryland', 'anthony', 'gbagada', 'bariga', 'somolu', 'shomolu',
                'ojodu', 'berger', 'magodo', 'ketu', 'mile 12', 'ikorodu',
                # Lekki/Ajah areas
                'lekki phase 1', 'lekki phase 2', 'lekki 1', 'lekki 2',
                'ajah', 'badore', 'addo', 'sangotedo', 'awoyaya', 'lakowe',
                'abraham adesanya', 'thomas estate', 'vgc', 'parkview',
                # Upscale areas
                'banana island', 'parkview estate', 'vgc', 'royal gardens',
                'richmond gate', 'pinnock beach', 'osborne', 'old ikoyi',
                # Emerging areas
                'abijo', 'bogije', 'eleko', 'shapati', 'ibeju', 'osoroko',
                # General
                'lagos', 'lagos state', 'lagos nigeria',
            }
        },
        'Abuja': {
            'bounds': {
                'min_lat': 8.8542, 'max_lat': 9.1825,
                'min_lon': 7.2621, 'max_lon': 7.6978,
            },
            'areas': {
                'abuja', 'fct', 'federal capital territory',
                # Districts
                'maitama', 'asokoro', 'wuse', 'wuse 2', 'garki', 'garki 2',
                'gwarimpa', 'jahi', 'utako', 'jabi', 'gudu', 'apo', 'durumi',
                'kubwa', 'lugbe', 'karu', 'nyanya', 'gwagwalada',
                # Areas
                'central business district', 'cbd', 'life camp', 'guzape',
                'katampe', 'mpape', 'lokogoma', 'kado', 'kuchingoro',
            }
        },
        'Port Harcourt': {
            'bounds': {
                'min_lat': 4.7161, 'max_lat': 4.9217,
                'min_lon': 6.9174, 'max_lon': 7.1077,
            },
            'areas': {
                'port harcourt', 'portharcourt', 'ph', 'rivers', 'rivers state',
                # Areas
                'g.r.a', 'gra', 'old gra', 'new gra', 'd-line', 'dline',
                'rumuokoro', 'rumuola', 'rumueme', 'rumuobiakani', 'rukpokwu',
                'eliozu', 'choba', 'alakahia', 'woji', 'trans amadi',
                'ada george', 'peter odili', 'location road', 'aba road',
                'elelenwo', 'port harcourt township', 'borokiri',
            }
        },
        'Ibadan': {
            'bounds': {
                'min_lat': 7.2447, 'max_lat': 7.5367,
                'min_lon': 3.7342, 'max_lon': 4.0986,
            },
            'areas': {
                'ibadan', 'oyo', 'oyo state',
                # Areas
                'bodija', 'jericho', 'agodi', 'mokola', 'oke-ado', 'sango',
                'challenge', 'ring road', 'dugbe', 'oke-ado', 'eleyele',
                'oluyole', 'apata', 'idi-ape', 'iwo road', 'ojoo',
                'moniya', 'new bodija', 'old bodija', 'ui', 'university of ibadan',
            }
        },
        'Kano': {
            'bounds': {
                'min_lat': 11.8445, 'max_lat': 12.1302,
                'min_lon': 8.3911, 'max_lon': 8.7216,
            },
            'areas': {
                'kano', 'kano state',
                # Areas
                'nassarawa', 'sabon gari', 'gwale', 'tarauni', 'dala',
                'fage', 'kano municipal', 'ungogo', 'bompai', 'hotoro',
                'gama', 'zoo road', 'ibrahim taiwo road',
            }
        },
        'Enugu': {
            'bounds': {
                'min_lat': 6.3540, 'max_lat': 6.5427,
                'min_lon': 7.4011, 'max_lon': 7.5870,
            },
            'areas': {
                'enugu', 'enugu state',
                # Areas
                'g.r.a', 'gra', 'independence layout', 'new haven', 'trans ekulu',
                'achara layout', 'uwani', 'asata', 'ogui', 'emene',
                'abakpa', 'coal camp', 'ncdc', 'maryland', 'garden city',
            }
        },
        'Calabar': {
            'bounds': {
                'min_lat': 4.8968, 'max_lat': 5.0844,
                'min_lon': 8.2762, 'max_lon': 8.3923,
            },
            'areas': {
                'calabar', 'cross river', 'cross river state',
                # Areas
                'marian', 'ekorinim', 'big qua', 'ediba', 'ikot ansa',
                'calabar south', 'calabar municipality', 'state housing',
            }
        },
        'Benin': {
            'bounds': {
                'min_lat': 6.2329, 'max_lat': 6.4238,
                'min_lon': 5.5279, 'max_lon': 5.6951,
            },
            'areas': {
                'benin', 'benin city', 'edo', 'edo state',
                # Areas
                'g.r.a', 'gra', 'ugbowo', 'uselu', 'ekosodin', 'sapele road',
                'airport road', 'ikpoba hill', 'new benin', 'upper sakponba',
                'ugbor', 'upper mission', 'forestry', 'trinity',
            }
        },
        'Ogun': {
            'bounds': {
                'min_lat': 6.5356, 'max_lat': 7.3972,
                'min_lon': 2.6930, 'max_lon': 3.9341,
            },
            'areas': {
                'ogun', 'ogun state',
                # Major cities
                'abeokuta', 'ijebu-ode', 'sagamu', 'shagamu', 'ota', 'ifo',
                'ilaro', 'agbara', 'mowe', 'ibafo', 'ewekoro', 'sango-ota',
                # Areas in Abeokuta
                'oke-mosan', 'isale igbein', 'itoku', 'iberekodo', 'obantoko',
                'kemta', 'adigbe', 'idi-aba', 'quarry road', 'ibara',
                # Ijebu areas
                'ijebu', 'ijebu ode', 'ijebu-ife', 'odogbolu', 'epe-ijebu',
                # Remo areas
                'remo', 'sagamu-remo', 'remo north',
                # Industrial/emerging
                'redemption camp', 'mowe-ibafo', 'arepo', 'magboro', 'berger',
                'ogba', 'warewa', 'isheri', 'ojodu-berger',
            }
        },
    }

    def __init__(self, target_locations: Optional[List[str]] = None, strict_mode: bool = False):
        """
        Initialize location filter.

        Args:
            target_locations: List of cities to filter for (e.g., ['Lagos', 'Abuja'])
                             If None, reads from RP_TARGET_LOCATIONS env var or defaults to ['Lagos']
            strict_mode: If True, require exact coordinate validation.
                        If False, allow string matching (faster, less accurate)
        """
        self.strict_mode = strict_mode

        # Get target locations from param, env var, or default to Lagos
        if target_locations is None:
            env_locations = os.getenv("RP_TARGET_LOCATIONS", "Lagos")
            target_locations = [loc.strip() for loc in env_locations.split(',')]

        # Normalize city names
        self.target_locations = []
        for loc in target_locations:
            # Match to known cities (case-insensitive)
            matched = False
            for city_name in self.CITY_DATA.keys():
                if loc.lower() == city_name.lower():
                    self.target_locations.append(city_name)
                    matched = True
                    break
            if not matched:
                logger.warning(f"Unknown city '{loc}' - skipping. Available: {list(self.CITY_DATA.keys())}")

        # Default to Lagos if no valid cities
        if not self.target_locations:
            self.target_locations = ['Lagos']
            logger.warning("No valid target locations specified. Defaulting to Lagos only.")

        # Build combined area sets for fast lookup
        self.target_areas: Set[str] = set()
        for city in self.target_locations:
            self.target_areas.update(self.CITY_DATA[city]['areas'])

        self.stats = {
            'checked': 0,
            'matched': 0,
            'filtered': 0,
            'unknown': 0,
        }

        if RP_DEBUG:
            logger.debug(f"LocationFilter initialized: target_locations={self.target_locations}, strict_mode={strict_mode}")

    def normalize_location(self, location: str) -> str:
        """
        Normalize location string for matching.

        Args:
            location: Raw location string

        Returns:
            Normalized lowercase location
        """
        if not location:
            return ""

        # Convert to lowercase
        loc = location.lower().strip()

        # Remove common suffixes
        for city in self.CITY_DATA.keys():
            loc = loc.replace(f', {city.lower()}', '').replace(f',{city.lower()}', '')
        loc = loc.replace(', nigeria', '').replace(',nigeria', '')
        loc = loc.replace(' nigeria', '')

        # Remove extra whitespace
        loc = ' '.join(loc.split())

        return loc

    def is_target_location_string(self, location: str) -> Optional[str]:
        """
        Check if location string matches any target city (fast string matching).

        Args:
            location: Location string from listing

        Returns:
            City name if matched, None if no match
        """
        if not location:
            return None

        normalized = self.normalize_location(location)

        # Check if matches any target area
        for area in self.target_areas:
            if area in normalized:
                # Find which city this area belongs to
                for city, data in self.CITY_DATA.items():
                    if city in self.target_locations and area in data['areas']:
                        if RP_DEBUG:
                            logger.debug(f"Location '{location}' matched {city} area: {area}")
                        return city

        return None

    def is_in_city_bounds(self, lat: float, lon: float, city: str) -> bool:
        """
        Check if coordinates are within city bounding box.

        Args:
            lat: Latitude
            lon: Longitude
            city: City name

        Returns:
            True if within city bounds
        """
        if city not in self.CITY_DATA:
            return False

        bounds = self.CITY_DATA[city]['bounds']
        return (
            bounds['min_lat'] <= lat <= bounds['max_lat'] and
            bounds['min_lon'] <= lon <= bounds['max_lon']
        )

    def is_target_location(self, location: str, coordinates: Optional[Dict] = None) -> bool:
        """
        Check if location is in any target city.

        Uses string matching first (fast), then coordinate validation if available.

        Args:
            location: Location string
            coordinates: Optional dict with 'lat' and 'lng' keys

        Returns:
            True if location matches any target city, False otherwise
        """
        self.stats['checked'] += 1

        # Try string matching first (fast)
        matched_city = self.is_target_location_string(location)

        if matched_city:
            self.stats['matched'] += 1
            return True

        # If strict mode and coordinates available, check bounds
        if self.strict_mode and coordinates:
            lat = coordinates.get('lat')
            lon = coordinates.get('lng')

            if lat is not None and lon is not None:
                for city in self.target_locations:
                    if self.is_in_city_bounds(float(lat), float(lon), city):
                        self.stats['matched'] += 1
                        if RP_DEBUG:
                            logger.debug(f"Location matched {city} by coordinates: ({lat}, {lon})")
                        return True

                # Coordinates don't match any target city
                self.stats['filtered'] += 1
                return False

        # Unknown - default to allow in non-strict mode
        self.stats['unknown'] += 1
        return not self.strict_mode

    def filter_listings_by_location(self, listings: List[Dict], location_key: str = 'location') -> Tuple[List[Dict], int]:
        """
        Filter listings to only include properties in target cities.

        Args:
            listings: List of listing dictionaries
            location_key: Key for location field in listing dict

        Returns:
            Tuple of (filtered_listings, num_filtered)
        """
        filtered_listings = []
        filtered_count = 0
        filtered_locations = []

        for listing in listings:
            location = listing.get(location_key, '')
            coordinates = listing.get('coordinates')

            if self.is_target_location(location, coordinates):
                filtered_listings.append(listing)
            else:
                filtered_count += 1
                filtered_locations.append(location)

        # Log summary
        if filtered_count > 0:
            target_str = ', '.join(self.target_locations)
            logger.info(f"Location filter ({target_str}): Removed {filtered_count} non-target properties. Remaining: {len(filtered_listings)}/{len(listings)}")

            if RP_DEBUG and filtered_locations:
                # Log examples of filtered locations
                for loc in filtered_locations[:5]:
                    logger.debug(f"  Filtered location: {loc}")

        return filtered_listings, filtered_count

    def validate_before_geocoding(self, location: str) -> bool:
        """
        Validate location before sending to geocoding API.

        Saves API calls by filtering out obvious non-target locations.

        Args:
            location: Location string to validate

        Returns:
            True if location should be geocoded, False to skip
        """
        # Quick string check
        matched_city = self.is_target_location_string(location)

        if matched_city:
            # Definitely in target city - allow geocoding
            return True

        # Unknown - allow geocoding in non-strict mode
        return not self.strict_mode

    def get_stats(self) -> dict:
        """
        Get statistics about location filtering.

        Returns:
            Dict with filtering stats
        """
        total = self.stats['checked']
        if total == 0:
            return {
                **self.stats,
                'target_locations': self.target_locations,
            }

        return {
            **self.stats,
            'target_locations': self.target_locations,
            'matched_pct': round(self.stats['matched'] / total * 100, 1),
            'filtered_pct': round(self.stats['filtered'] / total * 100, 1),
            'unknown_pct': round(self.stats['unknown'] / total * 100, 1),
        }


# Global location filter instance
_global_filter: Optional[LocationFilter] = None


def get_location_filter(target_locations: Optional[List[str]] = None, strict_mode: Optional[bool] = None) -> LocationFilter:
    """
    Get global location filter instance (singleton).

    Args:
        target_locations: Target cities (only used on first call)
        strict_mode: Strict coordinate validation (only used on first call)

    Returns:
        Global LocationFilter instance
    """
    global _global_filter

    if _global_filter is None:
        if strict_mode is None:
            strict_mode = os.getenv("RP_STRICT_LOCATION", "0") == "1"
        _global_filter = LocationFilter(target_locations=target_locations, strict_mode=strict_mode)

    return _global_filter


def reset_location_filter():
    """
    Reset global location filter (useful for testing).
    """
    global _global_filter
    _global_filter = None
