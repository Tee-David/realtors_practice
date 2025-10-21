"""Test _is_property_url function directly"""

# Import the function
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.specials import _is_property_url

# Test URLs we're seeing in output
test_urls = [
    "https://nigeriapropertycentre.com/lagos/ajah",  # Category link
    "https://nigeriapropertycentre.com/lagos/lekki",  # Category link
    "https://nigeriapropertycentre.com/for-rent/flats-apartments/lagos/showtype",  # Category link
    "https://nigeriapropertycentre.com/for-sale/houses/terraced-duplexes/abuja/kubwa/3154198-4-units-of-2-bedrooms-terraced-duplex",  # Actual property
]

print("=" * 80)
print("TESTING _is_property_url() FUNCTION")
print("=" * 80)
print()

for url in test_urls:
    result = _is_property_url(url)
    status = "[ACCEPTED]" if result else "[REJECTED]"
    print(f"{status}: {url}")
    print()

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
