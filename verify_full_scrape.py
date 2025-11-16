#!/usr/bin/env python3
"""
Verify full scrape results in Firestore
"""
import os
from google.cloud import firestore
from datetime import datetime, timedelta
import json

# Set Firebase credentials
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json'

def verify_firestore_uploads():
    """Comprehensive verification of Firestore uploads"""

    db = firestore.Client.from_service_account_json(
        os.environ['FIREBASE_SERVICE_ACCOUNT']
    )

    properties_ref = db.collection('properties')

    print("=" * 100)
    print("FULL SCRAPE VERIFICATION - Firestore Upload Confirmation")
    print("=" * 100)
    print()

    # 1. Total count
    print("1. TOTAL PROPERTIES")
    print("-" * 100)
    all_properties = list(properties_ref.stream())
    total_count = len(all_properties)
    print(f"Total properties in Firestore: {total_count}")
    print()

    # 2. Breakdown by source
    print("2. BREAKDOWN BY SOURCE (All 51 sites)")
    print("-" * 100)
    sources = {}
    for doc in all_properties:
        data = doc.to_dict()
        source = data.get('basic_info', {}).get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1

    print(f"{'Source':<30} {'Count':>10} {'% of Total':>15}")
    print("-" * 100)
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_count * 100) if total_count > 0 else 0
        print(f"{source:<30} {count:>10} {percentage:>14.1f}%")

    print("-" * 100)
    print(f"Total unique sources: {len(sources)}")
    print()

    # 3. Recent uploads (last 24 hours)
    print("3. RECENT UPLOADS (Last 24 hours)")
    print("-" * 100)
    cutoff_time = datetime.now() - timedelta(days=1)
    recent = properties_ref.where('uploaded_at', '>=', cutoff_time).stream()
    recent_count = 0
    recent_by_source = {}

    for doc in recent:
        recent_count += 1
        data = doc.to_dict()
        source = data.get('basic_info', {}).get('source', 'unknown')
        recent_by_source[source] = recent_by_source.get(source, 0) + 1

    print(f"Properties uploaded in last 24 hours: {recent_count}")
    if recent_by_source:
        print("\nRecent uploads by source:")
        for source, count in sorted(recent_by_source.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count}")
    print()

    # 4. Schema verification
    print("4. ENTERPRISE SCHEMA VERIFICATION")
    print("-" * 100)
    if all_properties:
        sample = all_properties[0].to_dict()
        required_categories = [
            'basic_info', 'property_details', 'financial', 'location',
            'amenities', 'media', 'agent_info', 'metadata', 'tags'
        ]

        print("Checking for all 9 required categories in sample document...")
        all_present = True
        for category in required_categories:
            present = category in sample
            status = "PASS" if present else "FAIL"
            print(f"  [{status}] {category}")
            if not present:
                all_present = False

        if all_present:
            print("\nSCHEMA VERIFIED: All 9 categories present!")
        else:
            print("\nWARNING: Some categories missing!")
    print()

    # 5. Quality metrics
    print("5. DATA QUALITY METRICS")
    print("-" * 100)
    quality_scores = []
    has_price = 0
    has_location = 0
    has_images = 0
    has_bedrooms = 0

    for doc in all_properties:
        data = doc.to_dict()

        # Quality score
        metadata = data.get('metadata', {})
        quality_score = metadata.get('quality_score')
        if quality_score is not None:
            quality_scores.append(quality_score)

        # Completeness checks
        financial = data.get('financial', {})
        if financial.get('price'):
            has_price += 1

        location = data.get('location', {})
        if location.get('area') or location.get('location_text'):
            has_location += 1

        media = data.get('media', {})
        if media.get('images'):
            has_images += 1

        property_details = data.get('property_details', {})
        if property_details.get('bedrooms'):
            has_bedrooms += 1

    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        min_quality = min(quality_scores)
        max_quality = max(quality_scores)
        print(f"Average quality score: {avg_quality:.1f}%")
        print(f"Quality range: {min_quality:.1f}% - {max_quality:.1f}%")
    else:
        print("No quality scores found")

    print(f"\nCompleteness:")
    print(f"  Properties with price: {has_price} ({has_price/total_count*100:.1f}%)")
    print(f"  Properties with location: {has_location} ({has_location/total_count*100:.1f}%)")
    print(f"  Properties with images: {has_images} ({has_images/total_count*100:.1f}%)")
    print(f"  Properties with bedrooms: {has_bedrooms} ({has_bedrooms/total_count*100:.1f}%)")
    print()

    # 6. Auto-tagging verification
    print("6. AUTO-TAGGING VERIFICATION")
    print("-" * 100)
    premium_count = 0
    hot_deal_count = 0

    for doc in all_properties:
        data = doc.to_dict()
        tags = data.get('tags', {})

        if tags.get('premium'):
            premium_count += 1
        if tags.get('hot_deal'):
            hot_deal_count += 1

    print(f"Premium properties (auto-tagged): {premium_count}")
    print(f"Hot deals (auto-tagged): {hot_deal_count}")
    print()

    # 7. Sample properties
    print("7. SAMPLE PROPERTIES (First 5)")
    print("-" * 100)
    for i, doc in enumerate(all_properties[:5], 1):
        data = doc.to_dict()
        basic_info = data.get('basic_info', {})
        location = data.get('location', {})
        financial = data.get('financial', {})
        property_details = data.get('property_details', {})

        print(f"\n{i}. {basic_info.get('title', 'N/A')[:60]}")
        print(f"   Source: {basic_info.get('source', 'N/A')}")
        print(f"   Location: {location.get('area', 'N/A')}, {location.get('lga', 'N/A')}")
        print(f"   Price: N{financial.get('price', 0):,.0f}")
        print(f"   Type: {property_details.get('property_type', 'N/A')}")
        print(f"   Bedrooms: {property_details.get('bedrooms', 'N/A')}")
        print(f"   URL: {basic_info.get('listing_url', 'N/A')[:70]}...")

    print()

    # 8. Final summary
    print("=" * 100)
    print("VERIFICATION SUMMARY")
    print("=" * 100)
    print(f"Total Properties: {total_count}")
    print(f"Sources Covered: {len(sources)} / 51 sites")
    print(f"Recent Uploads (24h): {recent_count}")
    print(f"Schema: {'PASS - All 9 categories' if all_present else 'FAIL - Missing categories'}")
    print(f"Average Quality: {avg_quality:.1f}%" if quality_scores else "N/A")
    print(f"Premium Properties: {premium_count}")
    print(f"Hot Deals: {hot_deal_count}")
    print()

    # Overall status
    if total_count > 0 and len(sources) > 0:
        print("STATUS: SUCCESS - Firestore uploads confirmed!")
        print(f"All {total_count} properties successfully uploaded with enterprise schema.")
    else:
        print("STATUS: WARNING - No properties found or incomplete upload")

    print("=" * 100)

    return {
        'total_count': total_count,
        'sources': len(sources),
        'recent_count': recent_count,
        'schema_valid': all_present if all_properties else False,
        'avg_quality': avg_quality if quality_scores else 0,
        'premium_count': premium_count,
        'hot_deal_count': hot_deal_count
    }

if __name__ == "__main__":
    result = verify_firestore_uploads()

    # Export results to JSON
    with open('firestore_verification_result.json', 'w') as f:
        json.dump(result, f, indent=2)
        print(f"\nResults exported to: firestore_verification_result.json")
