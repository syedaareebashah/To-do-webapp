from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from uuid import UUID
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("BETTER_AUTH_SECRET"))
ALGORITHM = "HS256"
EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "1"))

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

def create_access_token(user_id: UUID, email: str) -> str:
    """
    Generate JWT token with user information.

    Args:
        user_id: User's unique identifier
        email: User's email address

    Returns:
        str: Encoded JWT token
    """
    expire = datetime.utcnow() + timedelta(hours=EXPIRATION_HOURS)
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """
    Verify JWT token and return payload.

    Args:
        token: JWT token to verify

    Returns:
        dict: Token payload

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        if "expired" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
