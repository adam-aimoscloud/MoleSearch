import requests
import time
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (MoleSearch Test Client)"
}

# Test credentials
TEST_CREDENTIALS = {"username": "admin", "password": "admin123"}

# Test data
TEST_DATA = {
    "text": "This is a test document about artificial intelligence and machine learning.",
    "image_url": None,
    "video_url": None
}

BATCH_TEST_DATA = [
    {
        "text": "First test document about AI technology",
        "image_url": None,
        "video_url": None
    },
    {
        "text": "Second test document about machine learning",
        "image_url": None,
        "video_url": None
    },
    {
        "text": "Third test document about deep learning",
        "image_url": None,
        "video_url": None
    }
]

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

def test_async_single_insert(auth_headers):
    """Test async single data insertion"""
    print("Testing async single data insertion...")
    
    try:
        # Create async insertion task
        response = requests.post(
            f"{BASE_URL}/api/v1/data/async_insert",
            json=TEST_DATA,
            headers=auth_headers
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"✅ Task created successfully: {task_id}")
            
            # Monitor task status
            monitor_task_status(task_id, auth_headers)
        else:
            print(f"❌ Failed to create task: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_async_batch_insert(auth_headers):
    """Test async batch data insertion"""
    print("\nTesting async batch data insertion...")
    
    try:
        # Create async batch insertion task
        response = requests.post(
            f"{BASE_URL}/api/v1/data/async_batch_insert",
            json={"data_list": BATCH_TEST_DATA},
            headers=auth_headers
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"✅ Batch task created successfully: {task_id}")
            
            # Monitor task status
            monitor_task_status(task_id, auth_headers)
        else:
            print(f"❌ Failed to create batch task: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

def monitor_task_status(task_id: str, auth_headers, max_wait_time: int = 300):
    """Monitor task status until completion or timeout"""
    print(f"Monitoring task {task_id}...")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}/status", headers=auth_headers)
            
            if response.status_code == 200:
                result = response.json()
                task_status = result['task_status']
                
                status = task_status['status']
                progress = task_status['progress']
                message = task_status['message']
                
                print(f"📊 Status: {status}, Progress: {progress:.1f}%, Message: {message}")
                
                if status in ['completed', 'failed']:
                    if status == 'completed':
                        print("✅ Task completed successfully!")
                        if task_status.get('result'):
                            print(f"📋 Result: {json.dumps(task_status['result'], indent=2)}")
                    else:
                        print("❌ Task failed!")
                    return
                
                # Wait before next check
                time.sleep(5)
            else:
                print(f"❌ Failed to get task status: {response.status_code}")
                return
                
        except Exception as e:
            print(f"❌ Error monitoring task: {e}")
            return
    
    print("⏰ Task monitoring timeout")

def test_sync_vs_async(auth_headers):
    """Compare sync vs async insertion performance"""
    print("\nComparing sync vs async insertion...")
    
    # Test sync insertion
    print("Testing sync insertion...")
    sync_start = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/data/insert",
            json=TEST_DATA,
            headers=auth_headers
        )
        
        sync_time = time.time() - sync_start
        
        if response.status_code == 200:
            print(f"✅ Sync insertion completed in {sync_time:.2f} seconds")
        else:
            print(f"❌ Sync insertion failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Sync insertion error: {e}")
    
    # Test async insertion
    print("Testing async insertion...")
    async_start = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/data/async_insert",
            json=TEST_DATA,
            headers=auth_headers
        )
        
        async_time = time.time() - async_start
        
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"✅ Async task created in {async_time:.2f} seconds")
            print(f"📋 Task ID: {task_id}")
            
            # Quick status check
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}/status", headers=auth_headers)
            if status_response.status_code == 200:
                status_result = status_response.json()
                status = status_result['task_status']['status']
                print(f"📊 Initial status: {status}")
                
        else:
            print(f"❌ Async insertion failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Async insertion error: {e}")

def main():
    """Main test function"""
    print("🧪 MoleSearch Async Insertion Test")
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
    test_sync_vs_async(auth_headers)
    test_async_single_insert(auth_headers)
    test_async_batch_insert(auth_headers)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()
