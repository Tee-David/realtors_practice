"""
Clear all documents from Firestore properties collection.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from core.firestore_enterprise import _get_firestore_client

def clear_firestore():
    """Delete all documents from properties collection."""
    db = _get_firestore_client()
    if not db:
        print("[ERROR] Could not connect to Firestore")
        return False

    print("[INFO] Connected to Firestore")

    # Get properties collection
    properties_ref = db.collection('properties')

    # Get all documents
    print("[INFO] Fetching all documents...")
    docs = list(properties_ref.stream())

    if not docs:
        print("[INFO] No documents to delete. Firestore is already empty.")
        return True

    print(f"[INFO] Found {len(docs)} documents to delete")

    # Delete in batches of 500 (Firestore limit)
    batch_size = 500
    deleted_count = 0

    for i in range(0, len(docs), batch_size):
        batch = db.batch()
        batch_docs = docs[i:i + batch_size]

        for doc in batch_docs:
            batch.delete(doc.reference)

        batch.commit()
        deleted_count += len(batch_docs)
        print(f"[INFO] Deleted {deleted_count}/{len(docs)} documents...")

    print(f"[SUCCESS] Deleted {deleted_count} documents from Firestore!")
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("CLEARING FIRESTORE PROPERTIES COLLECTION")
    print("=" * 60)
    print()

    success = clear_firestore()

    print()
    if success:
        print("[SUCCESS] Firestore cleared successfully!")
    else:
        print("[ERROR] Failed to clear Firestore")
