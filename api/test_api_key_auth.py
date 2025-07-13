#!/usr/bin/env python3
"""
Test script to verify API key authentication works with search API
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"

def test_api_key_auth():
    """Test API key authentication with search API"""
    print("Testing API key authentication...")
    
    # Step 1: Login to get user token
    print("\n1. Logging in to get user token...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} - {resp.text}")
        return False
    
    login_result = resp.json()
    user_token = login_result['token']
    print(f"✓ Login successful, got user token")
    
    # Step 2: Create API key
    print("\n2. Creating API key...")
    auth_headers = {"Authorization": f"Bearer {user_token}"}
    
    create_key_data = {
        "name": "Test API Key",
        "expires_in_days": 30,
        "permissions": ["search", "insert"]
    }
    
    resp = requests.post(f"{BASE_URL}/api/v1/api-keys/create", 
                        json=create_key_data, headers=auth_headers)
    if resp.status_code != 200:
        print(f"Create API key failed: {resp.status_code} - {resp.text}")
        return False
    
    create_result = resp.json()
    api_key = create_result['api_key']['key']
    print(f"✓ API key created: {api_key[:20]}...")
    
    # Step 3: Test search API with API key
    print("\n3. Testing search API with API key...")
    api_key_headers = {"Authorization": f"Bearer {api_key}"}
    
    search_data = {
        "query": "test",
        "top_k": 10
    }
    
    resp = requests.post(f"{BASE_URL}/api/v1/search/text", 
                        json=search_data, headers=api_key_headers)
    if resp.status_code != 200:
        print(f"Search with API key failed: {resp.status_code} - {resp.text}")
        return False
    
    search_result = resp.json()
    print(f"✓ Search with API key successful: {len(search_result.get('results', []))} results")
    
    # Step 4: Test async insert with API key
    print("\n4. Testing async insert with API key...")
    
    insert_data = {
        "text": "Test file inserted via API key",
        "image_url": None,
        "video_url": None
    }
    
    resp = requests.post(f"{BASE_URL}/api/v1/data/async_insert", 
                        json=insert_data, headers=api_key_headers)
    if resp.status_code != 200:
        print(f"Async insert with API key failed: {resp.status_code} - {resp.text}")
        return False
    
    insert_result = resp.json()
    print(f"✓ Async insert with API key successful: task_id = {insert_result.get('task_id')}")
    
    # Step 5: Clean up - delete API key
    print("\n5. Cleaning up - deleting API key...")
    key_id = create_result['api_key']['key_id']
    resp = requests.delete(f"{BASE_URL}/api/v1/api-keys/{key_id}", headers=auth_headers)
    if resp.status_code != 200:
        print(f"Delete API key failed: {resp.status_code} - {resp.text}")
        return False
    
    print(f"✓ API key deleted successfully")
    
    print("\n🎉 All tests passed! API key authentication is working correctly.")
    return True

if __name__ == "__main__":
    try:
        success = test_api_key_auth()
        if not success:
            print("\n❌ Some tests failed!")
            exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        exit(1) 