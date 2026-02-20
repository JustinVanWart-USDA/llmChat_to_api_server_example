#!/usr/bin/env python
"""Quick test of the Chat Website API Wrapper"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("Testing Chat Website API Wrapper")
print("=" * 60)

# Test 1: Health check
print("\n[1/3] Health Check...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"✅ Health: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"❌ Health check failed: {e}")
    exit(1)

# Test 2: Models
print("\n[2/3] Models Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/v1/models", timeout=5)
    print(f"✅ Models: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"❌ Models failed: {e}")
    exit(1)

# Test 3: Chat with correct payload
print("\n[3/3] Chat Endpoint (with correct GovChat payload)...")
print("Sending request to GovChat...")
print("⏳ This will take 30-120 seconds...")

payload = {
    "model": {
        "id": "gpt-3.5-turbo",
        "name": "GPT-3.5",
        "maxLength": 12000,
        "tokenLimit": 4000
    },
    "messages": [
        {
            "role": "user",
            "content": "Hello! Test message. Please respond with 'Server is working!'"
        }
    ],
    "prompt": "You are Gov Chat an AI Assistant using Azure OpenAI. Follow the user's instructions carefully. Respond using markdown.",
    "temperature": 1,
    "key": ""
}

try:
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        json=payload,
        timeout=120
    )
    elapsed = time.time() - start
    
    print(f"Response received in {elapsed:.1f}s")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Chat successful!")
        print("\nResponse:")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("⏱️  Request timed out - GovChat may be slow or unreachable")
except Exception as e:
    print(f"❌ Chat failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
