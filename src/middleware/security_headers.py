"""
Security headers middleware for the Todo AI Chatbot System.

This module implements security headers and CORS configuration to enhance the security of the application.
"""

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.cors import CORSMiddleware
from typing import List
import time


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Add security headers to the response.

        Args:
            request (Request): The incoming request
            call_next: The next middleware in the chain

        Returns:
            Response: The response with security headers
        """
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Prevent MIME-type sniffing
        response.headers.setdefault("Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )

        return response


def setup_cors_middleware(app: FastAPI,
                         allow_origins: List[str] = None,
                         allow_credentials: bool = True,
                         allow_methods: List[str] = ["*"],
                         allow_headers: List[str] = ["*"]):
    """
    Set up CORS middleware for the application.

    Args:
        app (FastAPI): The FastAPI application instance
        allow_origins (List[str]): List of allowed origins
        allow_credentials (bool): Whether to allow credentials
        allow_methods (List[str]): List of allowed HTTP methods
        allow_headers (List[str]): List of allowed headers
    """
    if allow_origins is None:
        # Default to allowing localhost and common development origins
        allow_origins = [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "https://localhost",
            "https://127.0.0.1"
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        # Additional security settings
        allow_origin_regex=r"https://.*\.railway\.app",  # Allow railway deployments
        expose_headers=["Access-Control-Allow-Origin"]
    )


def setup_security_middleware(app: FastAPI):
    """
    Set up all security-related middleware for the application.

    Args:
        app (FastAPI): The FastAPI application instance
    """
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)


def add_security_to_app(app: FastAPI,
                       cors_origins: List[str] = None,
                       cors_credentials: bool = True,
                       cors_methods: List[str] = ["*"],
                       cors_headers: List[str] = ["*"]):
    """
    Convenience function to add all security configurations to the app.

    Args:
        app (FastAPI): The FastAPI application instance
        cors_origins (List[str]): List of allowed CORS origins
        cors_credentials (bool): Whether to allow credentials
        cors_methods (List[str]): List of allowed HTTP methods
        cors_headers (List[str]): List of allowed headers
    """
    setup_cors_middleware(
        app,
        allow_origins=cors_origins,
        allow_credentials=cors_credentials,
        allow_methods=cors_methods,
        allow_headers=cors_headers
    )

    setup_security_middleware(app)


# Example usage function
def create_secure_app() -> FastAPI:
    """
    Create a FastAPI application with security configurations.

    Returns:
        FastAPI: A secured FastAPI application instance
    """
    app = FastAPI(
        title="Todo AI Chatbot System API",
        description="Secure API for AI-powered task management",
        version="2.0.0"
    )

    # Add security configurations
    add_security_to_app(app)

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": time.time()
        }

    return app