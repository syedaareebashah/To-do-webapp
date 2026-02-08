"""
Settings configuration for the Todo AI Chatbot System
"""

import os
from datetime import timedelta


# Get secret key from environment - prioritize SECRET_KEY, fallback to BETTER_AUTH_SECRET
SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("BETTER_AUTH_SECRET", "fallback_secret_key_for_development"))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))