#!/usr/bin/env python3
"""
Test different approaches to fetch the Stakefy docs
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def test_with_session():
    """Try fetching with a session and retries"""
    print("Testing with session and retries...")

    # Create session with retries
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # First, try to get any cookies from the base domain
        print("  Step 1: Getting cookies from base domain...")
        response1 = session.get('https://docs.stakefy.io/', headers=headers, timeout=10, allow_redirects=True)
        print(f"  Base page status: {response1.status_code}")
        print(f"  Cookies received: {session.cookies.get_dict()}")

        # Now try the quick-start page
        print("  Step 2: Accessing quick-start page...")
        response2 = session.get('https://docs.stakefy.io/quick-start', headers=headers, timeout=10, allow_redirects=True)
        print(f"  Quick-start status: {response2.status_code}")

        if response2.status_code == 200:
            print(f"  SUCCESS! Page length: {len(response2.text)} chars")
            print(f"  First 200 chars: {response2.text[:200]}")
            return True
        else:
            print(f"  FAILED with status {response2.status_code}")
            return False

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def test_simple():
    """Try simple request"""
    print("\nTesting simple request...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        response = requests.get('https://docs.stakefy.io/quick-start', headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print(f"  SUCCESS! Page length: {len(response.text)} chars")
            return True
        else:
            print(f"  FAILED")
            return False

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


if __name__ == '__main__':
    print("="*60)
    print("Testing different fetch approaches")
    print("="*60)

    test_simple()
    test_with_session()

    print("\n" + "="*60)
    print("Tests complete")
    print("="*60)
