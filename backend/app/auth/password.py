from passlib.context import CryptContext
import re
from typing import Tuple

# Configure password hashing context with bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # 12 rounds for strong security
)

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt with 12 rounds.
    Truncate to 72 characters to avoid bcrypt limit.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    # Ensure max 72 chars for bcrypt
    password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash using constant-time comparison.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets complexity requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number

    Args:
        password: Password to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    return True, ""
