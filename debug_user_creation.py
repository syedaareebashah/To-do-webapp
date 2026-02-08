"""
Debug script to test user creation directly
"""

from src.database.session import get_session
from src.models.user import User
from src.utils.password import hash_password
import uuid
from datetime import datetime

def test_user_creation():
    print("Testing user creation directly...")
    
    # Create a new user object
    user_data = {
        "id": uuid.uuid4(),
        "email": "test@example.com",
        "username": "testuser",
        "password_hash": hash_password("SecurePass123!"),
        "created_at": datetime.utcnow()
    }
    
    user = User(**user_data)
    
    print(f"User created: {user.email}")
    
    # Try to save to database
    try:
        with next(get_session()) as session:  # get_session() is a generator
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"User saved successfully with ID: {user.id}")
    except Exception as e:
        print(f"Error saving user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_user_creation()