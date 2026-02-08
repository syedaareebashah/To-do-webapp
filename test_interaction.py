"""
Simple test to demonstrate how to interact with the chatbot
"""

import requests
import json
import uuid

# Base URL for the API
BASE_URL = "http://localhost:8001"

def test_chatbot_interaction():
    print("Testing chatbot interaction...")
    print("="*50)
    
    # Create a unique user ID for testing
    user_id = str(uuid.uuid4())
    print(f"Using user ID: {user_id}")
    
    # Test conversation ID (create a new one or use None to generate)
    conversation_id = None
    
    # Test messages to add, list, complete, and delete tasks
    test_messages = [
        "Add a task to buy groceries",
        "Add another task to call mom",
        "What tasks do I have?",
        "Complete the task to buy groceries",
        "What tasks do I have now?",
        "Delete the task to call mom"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Sending message: '{message}'")
        
        # Prepare the payload
        payload = {
            "message": message,
            "conversation_id": conversation_id
        }
        
        try:
            # Send the request to the chat endpoint
            # Note: This will fail due to authentication, but shows the expected format
            response = requests.post(f"{BASE_URL}/api/{user_id}/chat", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Response: {result['response']}")
                
                # Update conversation_id for subsequent messages
                conversation_id = result.get('conversation_id', conversation_id)
                
                # Show any tool calls that were executed
                if result.get('tool_calls'):
                    print(f"   Tool calls executed: {len(result['tool_calls'])}")
                    for tool_call in result['tool_calls']:
                        print(f"     - {tool_call['tool_name']}: {tool_call['result'].get('message', '')}")
            else:
                print(f"   Status: {response.status_code}")
                print(f"   Error: {response.json()}")
                
        except requests.exceptions.ConnectionError:
            print(f"   Error: Cannot connect to the server at {BASE_URL}")
            print(f"   Make sure the backend is running with: uvicorn src.app.main:app --host 0.0.0.0 --port 8001")
            break
        except Exception as e:
            print(f"   Error: {str(e)}")

def test_health_check():
    print("\n" + "="*50)
    print("HEALTH CHECK")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("+ Backend is running and healthy")
            print(f"  Health check response: {response.json()}")
        else:
            print(f"- Backend health check failed with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"- Cannot connect to the backend at {BASE_URL}")
        print("  Make sure the backend is running with: uvicorn src.app.main:app --host 0.0.0.0 --port 8001")

def show_how_to_run_backend():
    print("\n" + "="*50)
    print("HOW TO RUN THE BACKEND")
    print("="*50)
    print("1. Make sure you have the required dependencies installed:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Initialize the database:")
    print("   python -c \"from src.database.session import init_db; init_db()\"")
    print()
    print("3. Start the backend server:")
    print("   uvicorn src.app.main:app --host 0.0.0.0 --port 8001 --reload")
    print()
    print("4. Once the backend is running, you can test with your frontend")
    print("   or use API clients like Postman or curl")
    print()
    print("Note: For production use, you'll need to set up proper authentication")

if __name__ == "__main__":
    test_health_check()
    test_chatbot_interaction()
    show_how_to_run_backend()