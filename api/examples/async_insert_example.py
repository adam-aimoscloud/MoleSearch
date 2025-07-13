#!/usr/bin/env python3
"""
Example: How to use MoleSearch async data insertion
"""

import requests
import time
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
API_TOKEN = "your_token_here"  # Replace with your actual token

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}


def create_async_insert_task():
    """Create an async single data insertion task"""
    print("Creating async single data insertion task...")
    
    data = {
        "text": "This is a test document about artificial intelligence and machine learning technologies.",
        "image_url": "https://example.com/ai-image.jpg",
        "video_url": "https://example.com/ai-video.mp4"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/data/async_insert",
            json=data,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            estimated_time = result['estimated_time']
            
            print(f"✅ Task created successfully!")
            print(f"📋 Task ID: {task_id}")
            print(f"⏱️  Estimated time: {estimated_time} seconds")
            
            return task_id
        else:
            print(f"❌ Failed to create task: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error creating task: {e}")
        return None


def create_async_batch_insert_task():
    """Create an async batch data insertion task"""
    print("\nCreating async batch data insertion task...")
    
    batch_data = {
        "data_list": [
            {
                "text": "First document about deep learning",
                "image_url": "https://example.com/dl-image1.jpg",
                "video_url": None
            },
            {
                "text": "Second document about neural networks",
                "image_url": None,
                "video_url": "https://example.com/nn-video1.mp4"
            },
            {
                "text": "Third document about computer vision",
                "image_url": "https://example.com/cv-image1.jpg",
                "video_url": "https://example.com/cv-video1.mp4"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/data/async_batch_insert",
            json=batch_data,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            estimated_time = result['estimated_time']
            
            print(f"✅ Batch task created successfully!")
            print(f"📋 Task ID: {task_id}")
            print(f"⏱️  Estimated time: {estimated_time} seconds")
            print(f"📊 Items to process: {len(batch_data['data_list'])}")
            
            return task_id
        else:
            print(f"❌ Failed to create batch task: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error creating batch task: {e}")
        return None


def monitor_task_status(task_id, max_wait_time=300):
    """Monitor task status until completion or timeout"""
    print(f"\nMonitoring task {task_id}...")
    print("=" * 50)
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/tasks/{task_id}/status",
                headers=HEADERS
            )
            
            if response.status_code == 200:
                result = response.json()
                task_status = result['task_status']
                
                status = task_status['status']
                progress = task_status['progress']
                message = task_status['message']
                
                # Create progress bar
                bar_length = 30
                filled_length = int(bar_length * progress / 100)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                print(f"\r📊 Status: {status:12} | Progress: [{bar}] {progress:5.1f}% | {message}")
                
                if status in ['completed', 'failed']:
                    print("\n")
                    if status == 'completed':
                        print("✅ Task completed successfully!")
                        if task_status.get('result'):
                            print("📋 Task result:")
                            print(json.dumps(task_status['result'], indent=2))
                    else:
                        print("❌ Task failed!")
                        print(f"Error: {message}")
                    return True
                
                # Wait before next check
                time.sleep(3)
            else:
                print(f"\n❌ Failed to get task status: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"\n❌ Error monitoring task: {e}")
            return False
    
    print(f"\n⏰ Task monitoring timeout after {max_wait_time} seconds")
    return False


def compare_sync_vs_async():
    """Compare sync vs async insertion performance"""
    print("\n" + "=" * 60)
    print("COMPARING SYNC VS ASYNC INSERTION")
    print("=" * 60)
    
    test_data = {
        "text": "Performance comparison test document",
        "image_url": "https://example.com/test-image.jpg",
        "video_url": "https://example.com/test-video.mp4"
    }
    
    # Test sync insertion
    print("\n🔄 Testing SYNC insertion...")
    sync_start = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/data/insert",
            json=test_data,
            headers=HEADERS
        )
        
        sync_time = time.time() - sync_start
        
        if response.status_code == 200:
            print(f"✅ Sync insertion completed in {sync_time:.2f} seconds")
        else:
            print(f"❌ Sync insertion failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Sync insertion error: {e}")
    
    # Test async insertion
    print("\n⚡ Testing ASYNC insertion...")
    async_start = time.time()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/data/async_insert",
            json=test_data,
            headers=HEADERS
        )
        
        async_time = time.time() - async_start
        
        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"✅ Async task created in {async_time:.2f} seconds")
            print(f"📋 Task ID: {task_id}")
            
            # Quick status check
            time.sleep(2)
            status_response = requests.get(
                f"{API_BASE_URL}/api/v1/tasks/{task_id}/status",
                headers=HEADERS
            )
            if status_response.status_code == 200:
                status_result = status_response.json()
                status = status_result['task_status']['status']
                print(f"📊 Initial status: {status}")
                
        else:
            print(f"❌ Async insertion failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Async insertion error: {e}")


def main():
    """Main function"""
    print("🚀 MoleSearch Async Insertion Example")
    print("=" * 50)
    
    # Check API health
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server is not responding")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        return
    
    # Run examples
    print("\n" + "=" * 50)
    print("EXAMPLE 1: Single Data Insertion")
    print("=" * 50)
    
    task_id = create_async_insert_task()
    if task_id:
        monitor_task_status(task_id)
    
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Batch Data Insertion")
    print("=" * 50)
    
    batch_task_id = create_async_batch_insert_task()
    if batch_task_id:
        monitor_task_status(batch_task_id)
    
    # Performance comparison
    compare_sync_vs_async()
    
    print("\n🎉 All examples completed!")


if __name__ == "__main__":
    main() 