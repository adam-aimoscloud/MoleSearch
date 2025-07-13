#!/usr/bin/env python3
"""
Test script to simulate the exact curl command used by user
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "ms_BvCju2kYMCEdydzDl6rF9mRTGkm4W57zA_G2L1iHRb4"

def test_curl_simulation():
    """Simulate the exact curl command"""
    print("Simulating curl command...")
    
    # Simulate the exact curl command from user
    url = f"{BASE_URL}/api/v1/search/text"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "query": "artificial intelligence",
        "top_k": 10
    }
    
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    
    try:
        resp = requests.post(url, json=data, headers=headers)
        print(f"\nStatus Code: {resp.status_code}")
        print(f"Response Headers: {dict(resp.headers)}")
        print(f"Response Body: {resp.text}")
        
        if resp.status_code == 200:
            print("✓ SUCCESS: API key works!")
        else:
            print("✗ FAILED: API key doesn't work")
            
    except Exception as e:
        print(f"Exception: {e}")

def test_different_formats():
    """Test different header formats"""
    print("\n" + "="*50)
    print("Testing different header formats...")
    
    url = f"{BASE_URL}/api/v1/search/text"
    data = {"query": "artificial intelligence", "top_k": 10}
    
    # Test 1: Standard format
    print("\n1. Standard format:")
    headers1 = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    resp1 = requests.post(url, json=data, headers=headers1)
    print(f"Status: {resp1.status_code}")
    
    # Test 2: Lowercase authorization
    print("\n2. Lowercase authorization:")
    headers2 = {
        "content-type": "application/json",
        "authorization": f"Bearer {API_KEY}"
    }
    resp2 = requests.post(url, json=data, headers=headers2)
    print(f"Status: {resp2.status_code}")
    
    # Test 3: No content-type
    print("\n3. No content-type:")
    headers3 = {
        "Authorization": f"Bearer {API_KEY}"
    }
    resp3 = requests.post(url, json=data, headers=headers3)
    print(f"Status: {resp3.status_code}")
    
    # Test 4: Different Bearer format
    print("\n4. Different Bearer format:")
    headers4 = {
        "Content-Type": "application/json",
        "Authorization": f"bearer {API_KEY}"
    }
    resp4 = requests.post(url, json=data, headers=headers4)
    print(f"Status: {resp4.status_code}")

if __name__ == "__main__":
    test_curl_simulation()
    test_different_formats() 