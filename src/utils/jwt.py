"""
JWT utilities for the Todo AI Chatbot System
"""

from datetime import datetime, timedelta
from typing import Union
from jose import jwt
import os
from src.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): Data to encode in the token
        expires_delta (Union[timedelta, None]): Token expiration time delta

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt