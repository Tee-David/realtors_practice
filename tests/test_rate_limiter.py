#!/usr/bin/env python3
"""
Test Rate Limiter with robots.txt Support

Tests the rate limiter's robots.txt parsing and delay enforcement.
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rate_limiter import RateLimiter


def test_initialization():
    """Test rate limiter initialization"""
    limiter = RateLimiter(min_delay=2.0, user_agent="TestBot/1.0")

    assert limiter.min_delay == 2.0
    assert limiter.user_agent == "TestBot/1.0"
    assert limiter.respect_robots == True

    print("[PASS] Rate limiter initialization")


def test_domain_extraction():
    """Test domain extraction from URLs"""
    limiter = RateLimiter()

    assert limiter.get_domain("https://example.com/path") == "example.com"
    assert limiter.get_domain("http://www.site.ng/page?q=1") == "www.site.ng"
    assert limiter.get_domain("https://propertypro.ng/") == "propertypro.ng"

    print("[PASS] Domain extraction")


def test_robots_txt_url():
    """Test robots.txt URL generation"""
    limiter = RateLimiter()

    url = "https://propertypro.ng/property-for-sale"
    robots_url = limiter.get_robots_txt_url(url)

    assert robots_url == "https://propertypro.ng/robots.txt"

    print("[PASS] Robots.txt URL generation")


def test_can_fetch():
    """Test can_fetch (robots.txt compliance)"""
    limiter = RateLimiter()

    # Most sites should allow fetching by default
    url = "https://propertypro.ng/property-for-sale/lagos"
    allowed = limiter.can_fetch(url)

    # Should be True or False (not None)
    assert isinstance(allowed, bool)

    print(f"[PASS] can_fetch check (propertypro.ng: {allowed})")


def test_delay_calculation():
    """Test delay calculation"""
    limiter = RateLimiter(min_delay=1.5)

    # Without crawl delay
    delay = limiter.get_delay_for_domain("example.com")
    assert delay == 1.5

    # With crawl delay (simulated)
    limiter.crawl_delays["test.com"] = 3.0
    delay = limiter.get_delay_for_domain("test.com")
    assert delay == 3.0  # max(1.5, 3.0)

    print("[PASS] Delay calculation")


def test_wait_if_needed():
    """Test wait_if_needed delay enforcement"""
    limiter = RateLimiter(min_delay=0.5)

    domain = "testdomain.com"

    # First request - no wait
    wait_time = limiter.wait_if_needed(domain)
    assert wait_time == 0.0

    # Record request
    limiter.record_request(domain)

    # Immediate second request - should wait
    start = time.time()
    wait_time = limiter.wait_if_needed(domain)
    elapsed = time.time() - start

    # Should have waited ~0.5 seconds
    assert wait_time >= 0.4  # Allow small variance
    assert elapsed >= 0.4

    print(f"[PASS] wait_if_needed (waited {elapsed:.2f}s)")


def test_different_domains():
    """Test that different domains don't block each other"""
    limiter = RateLimiter(min_delay=1.0)

    # Record request to domain1
    limiter.record_request("domain1.com")

    # Immediate request to domain2 should not wait
    start = time.time()
    wait_time = limiter.wait_if_needed("domain2.com")
    elapsed = time.time() - start

    assert wait_time == 0.0
    assert elapsed < 0.1  # Should be nearly instant

    print(f"[PASS] Different domains don't block each other ({elapsed:.3f}s)")


def test_state_tracking():
    """Test request state tracking"""
    limiter = RateLimiter()

    domain1 = "site1.com"
    domain2 = "site2.com"

    # Record requests
    limiter.record_request(domain1)
    limiter.record_request(domain2)

    # Check state
    assert domain1 in limiter.last_request_times
    assert domain2 in limiter.last_request_times
    assert limiter.last_request_times[domain1] > 0
    assert limiter.last_request_times[domain2] > 0

    print("[PASS] Request state tracking")


def test_check_and_wait():
    """Test combined check_and_wait method"""
    limiter = RateLimiter(min_delay=0.3)

    url = "https://example.com/page"
    domain = limiter.get_domain(url)

    # First request
    result = limiter.check_and_wait(url)
    assert isinstance(result, bool)

    # Record it
    limiter.record_request(domain)

    # Second request - should wait
    start = time.time()
    result = limiter.check_and_wait(url)
    elapsed = time.time() - start

    assert elapsed >= 0.25  # Should have waited

    print(f"[PASS] check_and_wait (elapsed: {elapsed:.2f}s)")


def test_stats():
    """Test statistics generation"""
    limiter = RateLimiter()

    # Make some requests
    limiter.record_request("site1.com")
    limiter.record_request("site2.com")
    limiter.crawl_delays["site1.com"] = 2.0

    stats = limiter.get_stats()

    assert 'domains_tracked' in stats
    assert 'robots_txt_loaded' in stats
    assert 'crawl_delays' in stats
    assert 'min_delay' in stats
    assert 'respect_robots' in stats

    assert stats['domains_tracked'] == 2
    assert stats['crawl_delays']['site1.com'] == 2.0

    print("[PASS] Statistics generation")


def test_no_robots_respect():
    """Test rate limiter with robots.txt disabled"""
    limiter = RateLimiter(respect_robots=False)

    # Should allow all URLs
    assert limiter.can_fetch("https://any-site.com/blocked-path") == True
    assert limiter.respect_robots == False

    print("[PASS] Robots.txt respect disabled")


def run_all_tests():
    """Run all rate limiter tests"""
    print("\n" + "="*60)
    print("RATE LIMITER + ROBOTS.TXT TESTS")
    print("="*60 + "\n")

    try:
        test_initialization()
        test_domain_extraction()
        test_robots_txt_url()
        test_can_fetch()
        test_delay_calculation()
        test_wait_if_needed()
        test_different_domains()
        test_state_tracking()
        test_check_and_wait()
        test_stats()
        test_no_robots_respect()

        print("\n" + "="*60)
        print("[PASS] ALL TESTS PASSED (11/11)")
        print("="*60 + "\n")
        return True

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
