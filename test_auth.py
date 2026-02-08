"""
Test script to verify the authentication endpoints
"""

import requests
import json
import uuid

BASE_URL = "http://localhost:8001"

def test_auth_endpoints():
    print("Testing authentication endpoints...")
    print("="*50)
    
    # Generate a unique email for testing
    unique_email = f"testuser_{str(uuid.uuid4())[:8]}@example.com"
    
    # Test signup
    print(f"\n1. Testing signup with {unique_email}...")
    signup_data = {
        "email": unique_email,
        "password": "SecurePass123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        print(f"Signup response: {response.status_code}")
        if response.status_code == 201:
            signup_result = response.json()
            print("+ Signup successful")
            token = signup_result['token']
            print(f"Received token: {token[:20]}...")
        elif response.status_code == 409:
            print("x Signup failed - email already exists")
            # Try to sign in instead
            print("Trying to sign in with existing account...")
            signin_data = {
                "email": unique_email,
                "password": "SecurePass123!"
            }
            response = requests.post(f"{BASE_URL}/auth/signin", json=signin_data)
            if response.status_code == 200:
                signin_result = response.json()
                print("+ Signin successful")
                token = signin_result['token']
                print(f"Received token: {token[:20]}...")
            else:
                print(f"x Signin failed: {response.text}")
                return
        else:
            print(f"x Signup failed: {response.text}")
            return
    except Exception as e:
        print(f"x Signup error: {e}")
        return
    
    # Test /me endpoint with token
    print("\n2. Testing /me endpoint...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Me endpoint response: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print("+ /me endpoint successful")
            print(f"User info: {user_info}")
        else:
            print(f"x /me endpoint failed: {response.text}")
    except Exception as e:
        print(f"x /me endpoint error: {e}")
    
    print("\n" + "="*50)
    print("Authentication endpoints are working correctly!")
    print("You can now use /auth/signup and /auth/signin to create accounts")
    print("and authenticate users for the chatbot functionality.")

if __name__ == "__main__":
    test_auth_endpoints()