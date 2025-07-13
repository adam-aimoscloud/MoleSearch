#!/usr/bin/env python3
"""
Test script for pending tasks API
"""

import requests
import json
import time

# API configuration
BASE_URL = "http://localhost:8000"

def test_pending_tasks_api():
    """Test pending tasks API"""
    print("Testing pending tasks API...")
    
    try:
        # Login to get token
        print("0. Logging in...")
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get('token')
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        # First, create a few async tasks
        print("\n1. Creating async tasks...")
        
        # Create single insert task
        single_response = requests.post(
            f"{BASE_URL}/api/v1/data/async_insert",
            json={
                "text": "Test text for pending tasks",
                "image_url": "",
                "video_url": ""
            },
            headers=headers
        )
        
        if single_response.status_code == 200:
            single_task = single_response.json()
            print(f"✅ Created single insert task: {single_task['task_id']}")
        else:
            print(f"❌ Failed to create single insert task: {single_response.status_code}")
            print(single_response.text)
            return
        
        # Create batch insert task
        batch_response = requests.post(
            f"{BASE_URL}/api/v1/data/async_batch_insert",
            json={
                "data_list": [
                    {"text": "Batch test 1", "image_url": "", "video_url": ""},
                    {"text": "Batch test 2", "image_url": "", "video_url": ""}
                ]
            },
            headers=headers
        )
        
        if batch_response.status_code == 200:
            batch_task = batch_response.json()
            print(f"✅ Created batch insert task: {batch_task['task_id']}")
        else:
            print(f"❌ Failed to create batch insert task: {batch_response.status_code}")
            print(batch_response.text)
            return
        
        # Wait a moment for tasks to be created
        time.sleep(2)
        
        # Test pending tasks API
        print("\n2. Testing pending tasks API...")
        pending_response = requests.get(f"{BASE_URL}/api/v1/tasks/pending", headers=headers)
        
        if pending_response.status_code == 200:
            pending_data = pending_response.json()
            print(f"✅ Pending tasks API successful")
            print(f"📊 Total pending tasks: {pending_data.get('total', 0)}")
            
            tasks = pending_data.get('tasks', [])
            for i, task in enumerate(tasks):
                print(f"  Task {i+1}:")
                print(f"    ID: {task.get('task_id', 'N/A')}")
                print(f"    Status: {task.get('status', 'N/A')}")
                print(f"    Progress: {task.get('progress', 0)}%")
                print(f"    Message: {task.get('message', 'N/A')}")
                print(f"    Created: {task.get('created_at', 'N/A')}")
                print()
                
        else:
            print(f"❌ Pending tasks API failed: {pending_response.status_code}")
            print(pending_response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_pending_tasks_api() 