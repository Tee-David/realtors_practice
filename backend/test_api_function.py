"""Test the API function directly"""
import sys
import os
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'

from api_server import app

# Create a test request context
with app.test_request_context('/api/firestore/for-sale?limit=200&offset=0'):
    from api_server import firestore_for_sale
    print("Calling firestore_for_sale()...")
    try:
        result = firestore_for_sale()
        print(f"Success! Result type: {type(result)}")
        if hasattr(result, 'get_json'):
            print(f"JSON: {result.get_json()}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
