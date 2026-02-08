"""
Authentication Middleware for Todo AI Chatbot System

This module implements middleware for user authentication and authorization.
"""

import json
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from datetime import datetime
import os


class AuthMiddleware:
    """
    Middleware class for handling user authentication and authorization.
    """

    def __init__(self):
        """
        Initialize the authentication middleware.
        """
        # Get configuration from environment variables
        self.secret_key = os.getenv("AUTH_SECRET_KEY", "fallback_secret_for_dev")
        self.algorithm = os.getenv("AUTH_ALGORITHM", "HS256")

    async def __call__(self, request: Request, call_next):
        """
        Process the request through the authentication middleware.

        Args:
            request (Request): The incoming request
            call_next: The next function in the middleware chain

        Returns:
            Response: The processed response
        """
        # Extract token from the Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            # For endpoints that require authentication, raise an exception
            # For public endpoints, we could allow the request to continue
            # For this implementation, we'll allow unauthenticated requests to continue
            # and let individual endpoints decide if auth is required
            request.state.user_id = None
            response = await call_next(request)
            return response

        # Check if it's a bearer token
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )

        # Extract the token
        token = auth_header[7:].strip()

        # Attempt to decode the token
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token: no user ID"
                )

            # Store user ID in request state for use by downstream handlers
            request.state.user_id = user_id

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        # Continue with the request
        response = await call_next(request)
        return response


def get_user_id_from_request(request: Request) -> Optional[str]:
    """
    Extract user ID from the request state.

    Args:
        request (Request): The incoming request

    Returns:
        Optional[str]: User ID if available, None otherwise
    """
    return getattr(request.state, 'user_id', None)


def require_authentication(request: Request) -> str:
    """
    Require that the request is authenticated and return the user ID.

    Args:
        request (Request): The incoming request

    Returns:
        str: User ID of the authenticated user

    Raises:
        HTTPException: If the request is not authenticated
    """
    user_id = get_user_id_from_request(request)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return user_id