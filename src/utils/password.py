"""
Password utilities for the Todo AI Chatbot System
"""

from passlib.context import CryptContext
import re


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password (str): Plain text password to verify
        hashed_password (str): Hashed password to compare against

    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    Hash a plain password.

    Args:
        password (str): Plain text password to hash

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength according to security requirements.

    Args:
        password (str): Password to validate

    Returns:
        tuple[bool, str]: Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"

    return True, ""