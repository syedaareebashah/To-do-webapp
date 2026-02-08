"""
Setup script for testing the Todo Chatbot backend
"""

import uuid
import secrets

def generate_test_user():
    """
    Generate a test user with a UUID that can be used with the backend
    """
    user_id = str(uuid.uuid4())
    print("Test User Information:")
    print("="*30)
    print(f"User ID: {user_id}")
    print("Note: This is a randomly generated user ID for testing purposes.")
    print("In a real application, you would obtain this through proper signup/signin.")
    print()
    print("How to use this with the backend:")
    print(f"1. Use this user ID in API calls: {user_id}")
    print(f"2. Make requests to: http://localhost:8001/api/{user_id}/chat")
    print("3. Include proper authentication headers")
    print()
    print("Example curl command:")
    print(f'curl -X POST http://localhost:8001/api/{user_id}/chat \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\')
    print('  -d \'{"message": "Add a task to buy groceries"}\'')
    print()
    print("Note: You'll need a valid JWT token for the Authorization header.")
    print("The backend expects a JWT token containing the user_id in the payload.")
    return user_id

if __name__ == "__main__":
    generate_test_user()