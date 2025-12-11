#!/usr/bin/env python3
"""
Monitor Firestore uploads in real-time
"""
import os
import time
from datetime import datetime
from google.cloud import firestore

# Set Firebase credentials
os.environ['FIREBASE_SERVICE_ACCOUNT'] = 'realtor-s-practice-firebase-adminsdk-fbsvc-c8563eb2f2.json'

def monitor_firestore(interval=30, duration=None):
    """
    Monitor Firestore collection for new properties

    Args:
        interval: Check every N seconds
        duration: Total monitoring duration in seconds (None = infinite)
    """
    db = firestore.Client.from_service_account_json(
        os.environ['FIREBASE_SERVICE_ACCOUNT']
    )

    properties_ref = db.collection('properties')
    start_time = time.time()
    last_count = 0
    last_check_time = datetime.now()

    print("=" * 80)
    print("FIRESTORE MONITORING - Real-time Property Upload Tracking")
    print("=" * 80)
    print(f"Collection: properties")
    print(f"Check interval: {interval} seconds")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    try:
        while True:
            # Check if duration exceeded
            if duration and (time.time() - start_time) > duration:
                print(f"\nMonitoring duration ({duration}s) reached. Stopping.")
                break

            # Get current count
            current_count = len(list(properties_ref.select([]).stream()))
            current_time = datetime.now()
            elapsed = (current_time - last_check_time).total_seconds()

            # Calculate rate
            new_properties = current_count - last_count
            rate = new_properties / elapsed if elapsed > 0 else 0

            # Display update
            print(f"[{current_time.strftime('%H:%M:%S')}] "
                  f"Total: {current_count} properties "
                  f"(+{new_properties} in last {elapsed:.0f}s, "
                  f"{rate:.2f}/sec)")

            # Show sample of recent properties
            if new_properties > 0:
                recent = properties_ref.order_by(
                    'uploaded_at',
                    direction=firestore.Query.DESCENDING
                ).limit(3).stream()

                print("  Recent uploads:")
                for doc in recent:
                    data = doc.to_dict()
                    basic_info = data.get('basic_info', {})
                    location = data.get('location', {})
                    financial = data.get('financial', {})

                    title = basic_info.get('title', 'N/A')[:50]
                    source = basic_info.get('source', 'N/A')
                    area = location.get('area', 'N/A')
                    price = financial.get('price', 0)

                    print(f"    - {source}: {title}... ({area}, N{price:,.0f})")
                print()

            # Update tracking variables
            last_count = current_count
            last_check_time = current_time

            # Wait for next check
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")

    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    total_count = len(list(properties_ref.select([]).stream()))
    print(f"Total properties in Firestore: {total_count}")

    # Get breakdown by source
    print("\nBreakdown by source:")
    sources = {}
    for doc in properties_ref.stream():
        data = doc.to_dict()
        source = data.get('basic_info', {}).get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1

    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count} properties")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Monitor Firestore uploads in real-time')
    parser.add_argument('--interval', type=int, default=30,
                        help='Check interval in seconds (default: 30)')
    parser.add_argument('--duration', type=int, default=None,
                        help='Monitoring duration in seconds (default: infinite)')

    args = parser.parse_args()

    monitor_firestore(interval=args.interval, duration=args.duration)
