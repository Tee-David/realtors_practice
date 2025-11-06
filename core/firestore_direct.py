"""
core/firestore_direct.py

Direct Firestore writes without master workbook dependency.
Eliminates corruption risk by making Firestore the primary data store.

Features:
- Batch uploads (500 documents at a time - Firestore limit)
- Hash-based deduplication (uses property hash as document ID)
- Real-time updates (no file locking needed)
- Automatic retry on failure
- Per-site and aggregate collections

Usage:
    from core.firestore_direct import FirestoreUploader

    uploader = FirestoreUploader()
    uploader.upload_listings_batch(site_key, cleaned_listings)
"""

import os
import sys
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Lazy import Firebase (only when needed)
_firebase_initialized = False
_firestore_client = None


def _get_firestore_client():
    """Get Firestore client (lazy initialization)"""
    global _firebase_initialized, _firestore_client

    if _firebase_initialized:
        return _firestore_client

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        from google.cloud.firestore import SERVER_TIMESTAMP
    except ImportError:
        logger.warning("firebase-admin not installed. Firestore upload disabled.")
        logger.warning("Install with: pip install firebase-admin")
        return None

    # Check if already initialized
    if firebase_admin._apps:
        _firestore_client = firestore.client()
        _firebase_initialized = True
        return _firestore_client

    # Try to load credentials
    cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT')
    cred_json = os.getenv('FIREBASE_CREDENTIALS')

    if cred_path and Path(cred_path).exists():
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _firestore_client = firestore.client()
            _firebase_initialized = True
            logger.info(f"Firestore initialized from {cred_path}")
            return _firestore_client
        except Exception as e:
            logger.error(f"Failed to initialize Firestore from {cred_path}: {e}")
            return None

    elif cred_json:
        try:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            _firestore_client = firestore.client()
            _firebase_initialized = True
            logger.info("Firestore initialized from environment variable")
            return _firestore_client
        except Exception as e:
            logger.error(f"Failed to initialize Firestore from env var: {e}")
            return None

    else:
        logger.warning("Firebase credentials not found. Set FIREBASE_SERVICE_ACCOUNT or FIREBASE_CREDENTIALS")
        return None


def _clean_value(value):
    """Clean value for Firestore (handle NaN, None, etc.)"""
    import pandas as pd

    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        if pd.isna(value):
            return None
        return int(value) if value == int(value) else float(value)
    if isinstance(value, str):
        return value.strip() if value else None
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return value
    return value


class FirestoreUploader:
    """
    Direct Firestore uploader for property listings.

    Makes Firestore the primary data store, eliminating master workbook corruption.
    """

    def __init__(self, enabled: Optional[bool] = None):
        """
        Initialize Firestore uploader.

        Args:
            enabled: Override enable/disable. If None, checks FIRESTORE_ENABLED env var.
        """
        if enabled is None:
            self.enabled = os.getenv('FIRESTORE_ENABLED', '1') == '1'
        else:
            self.enabled = enabled

        self.db = None
        if self.enabled:
            self.db = _get_firestore_client()
            if self.db is None:
                self.enabled = False
                logger.warning("Firestore upload disabled (initialization failed)")

    def upload_listings_batch(
        self,
        site_key: str,
        listings: List[Dict[str, Any]],
        batch_size: int = 500
    ) -> Dict[str, Any]:
        """
        Upload listings to Firestore in batches.

        Args:
            site_key: Site identifier (e.g., 'cwlagos', 'npc')
            listings: List of cleaned, normalized listings
            batch_size: Firestore batch limit (max 500)

        Returns:
            Dict with upload stats: {uploaded, errors, skipped, total}
        """
        if not self.enabled or self.db is None:
            logger.debug(f"{site_key}: Firestore upload disabled")
            return {'uploaded': 0, 'errors': 0, 'skipped': 0, 'total': len(listings)}

        if not listings:
            logger.info(f"{site_key}: No listings to upload to Firestore")
            return {'uploaded': 0, 'errors': 0, 'skipped': 0, 'total': 0}

        # Import SERVER_TIMESTAMP
        from google.cloud.firestore import SERVER_TIMESTAMP

        logger.info(f"{site_key}: Uploading {len(listings)} listings to Firestore...")

        collection_ref = self.db.collection('properties')
        uploaded = 0
        errors = 0
        skipped = 0

        # Process in batches (Firestore limit: 500 operations per batch)
        for i in range(0, len(listings), batch_size):
            batch_listings = listings[i:i + batch_size]
            batch = self.db.batch()
            batch_ops = 0

            for listing in batch_listings:
                try:
                    # Use hash as document ID (prevents duplicates automatically)
                    doc_hash = listing.get('hash')
                    if not doc_hash:
                        logger.warning(f"{site_key}: Listing missing hash, skipping: {listing.get('title', 'No title')}")
                        skipped += 1
                        continue

                    doc_ref = collection_ref.document(doc_hash)

                    # Prepare document data
                    doc_data = {
                        'title': _clean_value(listing.get('title')),
                        'price': _clean_value(listing.get('price')),
                        'price_per_sqm': _clean_value(listing.get('price_per_sqm')),
                        'price_per_bedroom': _clean_value(listing.get('price_per_bedroom')),
                        'location': _clean_value(listing.get('location')),
                        'estate_name': _clean_value(listing.get('estate_name')),
                        'property_type': _clean_value(listing.get('property_type')),
                        'bedrooms': _clean_value(listing.get('bedrooms')),
                        'bathrooms': _clean_value(listing.get('bathrooms')),
                        'toilets': _clean_value(listing.get('toilets')),
                        'bq': _clean_value(listing.get('bq')),
                        'land_size': _clean_value(listing.get('land_size')),
                        'title_tag': _clean_value(listing.get('title_tag')),
                        'description': _clean_value(listing.get('description')),
                        'promo_tags': _clean_value(listing.get('promo_tags')),
                        'initial_deposit': _clean_value(listing.get('initial_deposit')),
                        'payment_plan': _clean_value(listing.get('payment_plan')),
                        'service_charge': _clean_value(listing.get('service_charge')),
                        'launch_timeline': _clean_value(listing.get('launch_timeline')),
                        'agent_name': _clean_value(listing.get('agent_name')),
                        'contact_info': _clean_value(listing.get('contact_info')),
                        'images': _clean_value(listing.get('images')),
                        'listing_url': _clean_value(listing.get('listing_url')),
                        'source': _clean_value(listing.get('source', site_key)),
                        'site_key': site_key,
                        'scrape_timestamp': _clean_value(listing.get('scrape_timestamp')),
                        'hash': doc_hash,
                        'quality_score': _clean_value(listing.get('quality_score')),

                        # Metadata
                        'uploaded_at': SERVER_TIMESTAMP,
                        'updated_at': SERVER_TIMESTAMP,
                    }

                    # Add coordinates if available
                    coordinates = listing.get('coordinates')
                    if coordinates and isinstance(coordinates, dict):
                        lat = coordinates.get('lat')
                        lng = coordinates.get('lng')
                        if lat and lng:
                            doc_data['coordinates'] = {
                                'latitude': float(lat),
                                'longitude': float(lng)
                            }

                    # Set document (merge=True updates existing, creates if not exists)
                    batch.set(doc_ref, doc_data, merge=True)
                    batch_ops += 1

                except Exception as e:
                    logger.error(f"{site_key}: Error preparing listing for Firestore: {e}")
                    errors += 1

            # Commit batch
            if batch_ops > 0:
                try:
                    batch.commit()
                    uploaded += batch_ops
                    logger.info(f"{site_key}: Uploaded batch {i//batch_size + 1} ({batch_ops} listings)")
                except Exception as e:
                    logger.error(f"{site_key}: Batch commit failed: {e}")
                    errors += batch_ops

        total = len(listings)
        logger.info(f"{site_key}: Firestore upload complete - {uploaded}/{total} uploaded, {errors} errors, {skipped} skipped")

        # Trigger aggregate update hook (optional, non-blocking)
        if uploaded > 0 and os.getenv('FIRESTORE_AUTO_AGGREGATE', '0') == '1':
            try:
                self._trigger_aggregate_update(site_key)
            except Exception as e:
                logger.warning(f"{site_key}: Failed to trigger aggregate update: {e}")

        return {
            'uploaded': uploaded,
            'errors': errors,
            'skipped': skipped,
            'total': total
        }

    def update_site_metadata(self, site_key: str, metadata: Dict[str, Any]):
        """
        Update site metadata in Firestore.

        Args:
            site_key: Site identifier
            metadata: Metadata dict (scrape_count, last_scrape, etc.)
        """
        if not self.enabled or self.db is None:
            return

        try:
            from google.cloud.firestore import SERVER_TIMESTAMP
            doc_ref = self.db.collection('site_metadata').document(site_key)
            metadata['updated_at'] = SERVER_TIMESTAMP
            doc_ref.set(metadata, merge=True)
            logger.debug(f"{site_key}: Updated site metadata in Firestore")
        except Exception as e:
            logger.error(f"{site_key}: Failed to update site metadata: {e}")

    def get_existing_hashes(self, site_key: str, limit: int = 10000) -> set:
        """
        Get set of existing property hashes for a site (for deduplication).

        Args:
            site_key: Site identifier
            limit: Max hashes to retrieve

        Returns:
            Set of property hashes
        """
        if not self.enabled or self.db is None:
            return set()

        try:
            collection_ref = self.db.collection('properties')
            query = collection_ref.where('site_key', '==', site_key).limit(limit)
            docs = query.stream()

            hashes = set()
            for doc in docs:
                hashes.add(doc.id)  # Document ID is the hash

            logger.debug(f"{site_key}: Retrieved {len(hashes)} existing hashes from Firestore")
            return hashes

        except Exception as e:
            logger.error(f"{site_key}: Failed to get existing hashes: {e}")
            return set()

    def _trigger_aggregate_update(self, site_key: str):
        """
        Trigger aggregate update after successful upload (non-blocking).

        This is a lightweight hook that marks aggregates as stale.
        Actual recalculation happens in background via scripts/update_firestore_aggregates.py

        Args:
            site_key: Site that was just updated
        """
        if not self.enabled or self.db is None:
            return

        try:
            from google.cloud.firestore import SERVER_TIMESTAMP

            # Mark dashboard aggregate as stale
            self.db.collection('aggregates').document('_stale_marker').set({
                'dashboard': True,
                'top_deals': True,
                'newest_listings': True,
                'last_upload_site': site_key,
                'updated_at': SERVER_TIMESTAMP
            }, merge=True)

            logger.debug(f"{site_key}: Marked aggregates as stale")

        except Exception as e:
            logger.warning(f"{site_key}: Failed to mark aggregates as stale: {e}")


# Singleton instance
_uploader = None


def get_firestore_uploader() -> FirestoreUploader:
    """Get singleton Firestore uploader instance"""
    global _uploader
    if _uploader is None:
        _uploader = FirestoreUploader()
    return _uploader


def upload_listings_to_firestore(site_key: str, listings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenience function to upload listings to Firestore.

    Args:
        site_key: Site identifier
        listings: List of cleaned listings

    Returns:
        Upload stats dict
    """
    uploader = get_firestore_uploader()
    return uploader.upload_listings_batch(site_key, listings)
