"""Test API endpoints"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("Testing /api/firestore/properties...")
try:
    response = requests.get(f"{BASE_URL}/api/firestore/properties?limit=3")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n\nTesting /api/firestore/for-sale...")
try:
    response = requests.get(f"{BASE_URL}/api/firestore/for-sale?limit=3")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n\nTesting /api/firestore/dashboard...")
try:
    response = requests.get(f"{BASE_URL}/api/firestore/dashboard")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total properties: {data.get('data', {}).get('total_properties', 0)}")
    print(f"For sale: {data.get('data', {}).get('total_for_sale', 0)}")
    print(f"For rent: {data.get('data', {}).get('total_for_rent', 0)}")
except Exception as e:
    print(f"Error: {e}")
