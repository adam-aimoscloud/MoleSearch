#!/usr/bin/env python3
"""
Real API test runner script
This script will enable real API tests, calling the actual Aliyun DashScope API service
"""

import os
import sys
import subprocess

def main():
    print("🔥 MMExtractor Real API Test")
    print("=" * 60)
    print("⚠️  Note: This test will call the real API service, which may incur costs")
    print("⚠️  Please ensure your API key is configured correctly and has sufficient balance")
    print("=" * 60)
    
    # Set environment variable
    os.environ['ENABLE_REAL_API_TESTS'] = 'true'
    
    # Run tests
    print("\n🚀 Start running real API tests...")
    print("=" * 60)
    
    try:
        # Only run real API test class
        result = subprocess.run([
            sys.executable, '-m', 'unittest', 
            'mm_extractor_test.TestMMExtractorRealAPI',
            '-v'
        ], cwd=os.path.dirname(__file__), capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ All real API tests passed!")
        else:
            print(f"\n❌ Test failed, exit code: {result.returncode}")
            
    except Exception as e:
        print(f"\n❌ Error occurred while running tests: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Test completed")

if __name__ == '__main__':
    main() 