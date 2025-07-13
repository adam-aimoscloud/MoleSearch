#!/usr/bin/env python3
"""
Generate the correct curl command for testing
"""

API_KEY = "ms_BvCju2kYMCEdydzDl6rF9mRTGkm4W57zA_G2L1iHRb4"

print("=== Correct curl command ===")
print(f"""curl -X POST "http://localhost:8000/api/v1/search/text" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer {API_KEY}" \\
  -d '{{"query": "artificial intelligence", "top_k": 10}}'""")

print("\n=== One-line curl command ===")
print(f"""curl -X POST "http://localhost:8000/api/v1/search/text" -H "Content-Type: application/json" -H "Authorization: Bearer {API_KEY}" -d '{{"query": "artificial intelligence", "top_k": 10}}'""")

print("\n=== Test with different endpoints ===")
print(f"""curl -X POST "http://localhost:8000/api/v1/search/text" -H "Content-Type: application/json" -H "Authorization: Bearer {API_KEY}" -d '{{"query": "test", "top_k": 5}}'""")

print("\n=== Test health endpoint (no auth required) ===")
print("curl -X GET \"http://localhost:8000/api/v1/health\"")

print("\n=== Test with verbose output ===")
print(f"""curl -v -X POST "http://localhost:8000/api/v1/search/text" -H "Content-Type: application/json" -H "Authorization: Bearer {API_KEY}" -d '{{"query": "artificial intelligence", "top_k": 10}}'""") 