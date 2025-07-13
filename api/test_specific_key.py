#!/usr/bin/env python3
"""
Test script to verify the specific API key provided by user
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "ms_BvCju2kYMCEdydzDl6rF9mRTGkm4W57zA_G2L1iHRb4"

def test_specific_api_key():
    """Test the specific API key provided by user"""
    print(f"Testing API key: {API_KEY}")
    
    # Test search API
    print("\n1. Testing search API...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    search_data = {
        "query": "artificial intelligence",
        "top_k": 10
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/v1/search/text", 
                           json=search_data, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
        if resp.status_code == 200:
            print("✓ Search API successful")
        else:
            print("✗ Search API failed")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test list API keys to see if this key exists
    print("\n2. Testing list API keys (with user token)...")
    # First login to get user token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        if login_resp.status_code == 200:
            user_token = login_resp.json()['token']
            user_headers = {"Authorization": f"Bearer {user_token}"}
            
            list_resp = requests.get(f"{BASE_URL}/api/v1/api-keys/list", headers=user_headers)
            print(f"List API keys status: {list_resp.status_code}")
            if list_resp.status_code == 200:
                keys = list_resp.json()
                print(f"Found {keys.get('total', 0)} API keys")
                for key in keys.get('api_keys', []):
                    print(f"  - {key.get('name')}: {key.get('key', '')[:20]}...")
            else:
                print(f"List API keys failed: {list_resp.text}")
        else:
            print(f"Login failed: {login_resp.status_code}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_specific_api_key() 