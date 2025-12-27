"""Test which routes are registered"""
import sys
import os
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-3071684e9a.json'

from api_server import app

print("Registered routes:")
for rule in app.url_map.iter_rules():
    if 'for-sale' in rule.rule:
        print(f"  {rule.rule} -> {rule.endpoint}")
