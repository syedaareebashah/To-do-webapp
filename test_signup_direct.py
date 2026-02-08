"""
Test the signup function in isolation with unique email
"""

import os
os.environ['DATABASE_URL'] = 'sqlite:///./todo_chatbot.db'
import uuid

from src.api.endpoints.auth import signup
from src.schemas.auth import SignupRequest
from src.database.session import get_session
import asyncio

async def test_signup():
    # Create unique signup data
    unique_email = f"test_{str(uuid.uuid4())[:8]}@example.com"
    signup_data = SignupRequest(email=unique_email, password="SecurePass123!")
    
    # Get a session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Call the signup function
        result = await signup(signup_data=signup_data, session=session)
        print("Signup successful:", result.token is not None)
        print("User created with email:", result.user.email)
    except Exception as e:
        print(f"Signup failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(test_signup())