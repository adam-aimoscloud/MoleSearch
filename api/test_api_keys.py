#!/usr/bin/env python3
"""
Test script for API Key management
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

def test_api_key_management():
    """Test API key management functionality"""
    print("Testing API Key Management...")
    
    # Get authentication token
    token = get_token()
    if not token:
        return
    
    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    
    try:
        # 1. List API keys (should be empty initially)
        print("\n1. Listing API keys...")
        resp = requests.get(f"{BASE_URL}/api/v1/api-keys/list", headers=auth_headers)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ List API keys successful")
            print(f"📊 Total API keys: {data.get('total', 0)}")
            
            if data.get('api_keys'):
                for key in data['api_keys']:
                    print(f"  - {key['name']}: {key['key'][:8]}...")
        else:
            print(f"❌ List API keys failed: {resp.status_code}")
            print(resp.text)
            return
        
        # 2. Create a new API key
        print("\n2. Creating API key...")
        create_data = {
            "name": "Test API Key",
            "expires_in_days": 30,
            "permissions": ["search", "data"]
        }
        
        resp = requests.post(f"{BASE_URL}/api/v1/api-keys/create", 
                           json=create_data, headers=auth_headers)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Create API key successful")
            print(f"📝 Key name: {data['api_key']['name']}")
            print(f"🔑 Key value: {data['api_key']['key']}")
            print(f"📅 Expires: {data['api_key']['expires_at']}")
            
            api_key = data['api_key']['key']
        else:
            print(f"❌ Create API key failed: {resp.status_code}")
            print(resp.text)
            return
        
        # 3. List API keys again (should have one now)
        print("\n3. Listing API keys again...")
        resp = requests.get(f"{BASE_URL}/api/v1/api-keys/list", headers=auth_headers)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ List API keys successful")
            print(f"📊 Total API keys: {data.get('total', 0)}")
            
            for key in data.get('api_keys', []):
                print(f"  - {key['name']}: {key['key'][:8]}...")
        else:
            print(f"❌ List API keys failed: {resp.status_code}")
            print(resp.text)
        
        # 4. Test using the API key for authentication
        print("\n4. Testing API key authentication...")
        api_key_headers = {**HEADERS, "Authorization": f"Bearer {api_key}"}
        
        # Try to access a protected endpoint with the API key
        resp = requests.get(f"{BASE_URL}/api/v1/status", headers=api_key_headers)
        
        if resp.status_code == 200:
            print(f"✅ API key authentication successful")
        else:
            print(f"❌ API key authentication failed: {resp.status_code}")
            print(resp.text)
        
        # 5. Test search with API key
        print("\n5. Testing search with API key...")
        search_data = {
            "query": "artificial intelligence",
            "top_k": 5
        }
        
        resp = requests.post(f"{BASE_URL}/api/v1/search/text", 
                           json=search_data, headers=api_key_headers)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Search with API key successful")
            print(f"📊 Found {data.get('total', 0)} results")
        else:
            print(f"❌ Search with API key failed: {resp.status_code}")
            print(resp.text)
        
        # 6. Delete the API key
        print("\n6. Deleting API key...")
        key_id = None
        resp = requests.get(f"{BASE_URL}/api/v1/api-keys/list", headers=auth_headers)
        if resp.status_code == 200:
            data = resp.json()
            for key in data.get('api_keys', []):
                if key['name'] == "Test API Key":
                    key_id = key['key_id']
                    break
        
        if key_id:
            resp = requests.delete(f"{BASE_URL}/api/v1/api-keys/{key_id}", headers=auth_headers)
            if resp.status_code == 200:
                print(f"✅ Delete API key successful")
            else:
                print(f"❌ Delete API key failed: {resp.status_code}")
                print(resp.text)
        else:
            print("❌ Could not find API key to delete")
        
        # 7. List API keys one more time (should be empty again)
        print("\n7. Listing API keys after deletion...")
        resp = requests.get(f"{BASE_URL}/api/v1/api-keys/list", headers=auth_headers)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ List API keys successful")
            print(f"📊 Total API keys: {data.get('total', 0)}")
        else:
            print(f"❌ List API keys failed: {resp.status_code}")
            print(resp.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_key_management() 