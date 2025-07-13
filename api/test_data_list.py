#!/usr/bin/env python3
"""
Test script for data list API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "MoleSearch Test Client"
}

# Test credentials
TEST_CREDENTIALS = {"username": "admin", "password": "admin123"}

def get_token():
    """Login and get token for authentication"""
    try:
        resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json=TEST_CREDENTIALS, headers=HEADERS)
        if resp.status_code == 200:
            token = resp.json().get("token")
            print(f"✅ Got token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {resp.status_code}")
            print(resp.text)
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def get_auth_headers(token):
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    return headers

def test_data_list(auth_headers):
    """Test data list API"""
    print("Testing data list API...")
    
    try:
        # Test data list endpoint
        response = requests.post(
            f"{BASE_URL}/api/v1/data/list",
            json={"page": 1, "page_size": 10},
            headers=auth_headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Data list API successful")
            print(f"📊 Total items: {result.get('total', 0)}")
            print(f"📋 Items in response: {len(result.get('items', []))}")
            
            # Print first few items
            items = result.get('items', [])
            for i, item in enumerate(items[:3]):
                print(f"  Item {i+1}:")
                print(f"    ID: {item.get('id', 'N/A')}")
                print(f"    Text: {item.get('text', 'N/A')[:50]}...")
                print(f"    Image URL: {item.get('image_url', 'N/A')}")
                print(f"    Video URL: {item.get('video_url', 'N/A')}")
                print()
                
        else:
            print(f"❌ Data list API failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test function"""
    print("🧪 MoleSearch Data List API Test")
    print("=" * 50)
    
    # Test health check first
    try:
        response = requests.get(f"{BASE_URL}/health", headers=HEADERS)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        return
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Cannot run tests without token!")
        return
    auth_headers = get_auth_headers(token)
    
    # Run tests
    test_data_list(auth_headers)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main() 