"""
Test script to verify the chat endpoint works with task operations
"""

import requests
import json
import uuid

# Base URL for the API
BASE_URL = "http://localhost:8001"

# Create a test user ID
test_user_id = str(uuid.uuid4())
print(f"Using test user ID: {test_user_id}")

# Test adding a task through the chat endpoint
print("\n1. Testing chat endpoint to add a task...")
chat_data = {
    "message": "Add a task to buy groceries"
}

response = requests.post(f"{BASE_URL}/api/{test_user_id}/chat", json=chat_data)
print(f"Response status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test listing tasks through the chat endpoint
print("\n2. Testing chat endpoint to list tasks...")
chat_data = {
    "message": "What tasks do I have?"
}

response = requests.post(f"{BASE_URL}/api/{test_user_id}/chat", json=chat_data)
print(f"Response status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test completing a task through the chat endpoint
print("\n3. Testing chat endpoint to complete a task...")
chat_data = {
    "message": "Complete the task to buy groceries"
}

response = requests.post(f"{BASE_URL}/api/{test_user_id}/chat", json=chat_data)
print(f"Response status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test listing tasks again to see the completed task
print("\n4. Testing chat endpoint to list tasks again...")
chat_data = {
    "message": "What tasks do I have now?"
}

response = requests.post(f"{BASE_URL}/api/{test_user_id}/chat", json=chat_data)
print(f"Response status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")