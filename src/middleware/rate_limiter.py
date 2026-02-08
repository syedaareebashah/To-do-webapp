"""
Rate limiting middleware for the Todo AI Chatbot System.

This module implements rate limiting functionality to prevent abuse and ensure fair usage of the API.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import time
import hashlib
from typing import Dict, Optional


class RateLimiter:
    """
    In-memory rate limiter that tracks requests by IP address or user ID.
    """

    def __init__(self, requests: int = 100, window: int = 3600):
        """
        Initialize the rate limiter.

        Args:
            requests (int): Number of requests allowed per window
            window (int): Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.requests_log: Dict[str, list] = defaultdict(list)

    def is_allowed(self, identifier: str) -> tuple[bool, dict]:
        """
        Check if a request from the given identifier is allowed.

        Args:
            identifier (str): Identifier for the client (IP address or user ID)

        Returns:
            tuple[bool, dict]: Tuple of (is_allowed, rate_limit_info)
        """
        now = time.time()
        # Clean up old requests outside the window
        self.requests_log[identifier] = [
            req_time for req_time in self.requests_log[identifier]
            if now - req_time < self.window
        ]

        current_requests = len(self.requests_log[identifier])

        # Check if limit exceeded
        if current_requests >= self.requests:
            # Calculate retry_after
            oldest_request = min(self.requests_log[identifier])
            retry_after = int(oldest_request + self.window - now)
            return False, {
                "limit": self.requests,
                "remaining": 0,
                "reset_time": int(oldest_request + self.window),
                "retry_after": retry_after
            }

        # Add current request
        self.requests_log[identifier].append(now)

        # Calculate remaining requests
        remaining = self.requests - len(self.requests_log[identifier])

        # Calculate reset time
        oldest_request = min(self.requests_log[identifier]) if self.requests_log[identifier] else now
        reset_time = int(oldest_request + self.window)

        return True, {
            "limit": self.requests,
            "remaining": remaining,
            "reset_time": reset_time,
            "retry_after": reset_time - int(now)
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to implement rate limiting on API requests.
    """

    def __init__(self, app: FastAPI, rate_limiter: RateLimiter = None,
                 identifier_func=None, exclude_paths: list = None):
        """
        Initialize the rate limit middleware.

        Args:
            app (FastAPI): The FastAPI application instance
            rate_limiter (RateLimiter): Rate limiter instance
            identifier_func: Function to extract identifier from request
            exclude_paths (list): List of paths to exclude from rate limiting
        """
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.identifier_func = identifier_func or self.default_identifier_func
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/redoc"]

    def default_identifier_func(self, request: Request) -> str:
        """
        Default function to extract identifier from request.
        Uses X-Forwarded-For header if available, otherwise uses client host.

        Args:
            request (Request): The incoming request

        Returns:
            str: Identifier for the client
        """
        # Try to get forwarded-for header first (for when behind proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP if there are multiple
            return forwarded_for.split(",")[0].strip()

        # Otherwise use the client host
        client_host = request.client.host if request.client else "unknown"
        return client_host

    async def dispatch(self, request: Request, call_next):
        """
        Process the request and apply rate limiting.

        Args:
            request (Request): The incoming request
            call_next: The next middleware in the chain

        Returns:
            Response: The response with rate limit headers
        """
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            response = await call_next(request)
            return response

        # Get identifier for this request
        identifier = self.identifier_func(request)

        # Check if request is allowed
        is_allowed, rate_info = self.rate_limiter.is_allowed(identifier)

        if not is_allowed:
            # Return 429 Too Many Requests
            return Response(
                content="Rate limit exceeded",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset_time"]),
                    "Retry-After": str(rate_info["retry_after"])
                }
            )

        # Process the request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset_time"])

        return response


def setup_rate_limiting(app: FastAPI,
                       requests: int = 100,
                       window: int = 3600,
                       exclude_paths: list = None,
                       identifier_func = None):
    """
    Set up rate limiting middleware for the application.

    Args:
        app (FastAPI): The FastAPI application instance
        requests (int): Number of requests allowed per window
        window (int): Time window in seconds
        exclude_paths (list): List of paths to exclude from rate limiting
        identifier_func: Function to extract identifier from request
    """
    rate_limiter = RateLimiter(requests=requests, window=window)
    middleware = RateLimitMiddleware(
        app,
        rate_limiter=rate_limiter,
        identifier_func=identifier_func,
        exclude_paths=exclude_paths or ["/health", "/docs", "/redoc", "/openapi.json"]
    )

    # Replace the app's middleware stack with our rate limiter
    # This is a simplified approach - in production you'd want to properly integrate
    app.middleware_stack = None  # Reset middleware stack
    app.user_middleware.insert(0, middleware)


def create_rate_limited_app() -> FastAPI:
    """
    Create a FastAPI application with rate limiting.

    Returns:
        FastAPI: A rate-limited FastAPI application instance
    """
    app = FastAPI(title="Todo AI Chatbot System API - Rate Limited")

    # Add rate limiting
    setup_rate_limiting(app, requests=100, window=3600)  # 100 requests per hour

    @app.get("/")
    async def root():
        return {"message": "Rate limited API"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


# Predefined rate limiters for different endpoints
class RateLimitProfiles:
    """
    Predefined rate limit profiles for different use cases.
    """

    # Default profile: 100 requests per hour
    DEFAULT = RateLimiter(requests=100, window=3600)

    # Chat endpoint: 50 requests per 15 minutes (to prevent spam)
    CHAT_API = RateLimiter(requests=50, window=900)

    # Auth endpoints: 10 requests per 15 minutes (to prevent brute force)
    AUTH_API = RateLimiter(requests=10, window=900)

    # High-volume endpoints: 1000 requests per hour
    HIGH_VOLUME = RateLimiter(requests=1000, window=3600)


def get_client_ip(request: Request) -> str:
    """
    Extract client IP from request considering proxies.

    Args:
        request (Request): The incoming request

    Returns:
        str: Client IP address
    """
    # Check for forwarded headers in order of preference
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    # Fallback to client host
    return request.client.host if request.client else "unknown"


def get_user_based_identifier(request: Request) -> Optional[str]:
    """
    Extract user-based identifier from request (e.g., user_id from path or token).

    Args:
        request (Request): The incoming request

    Returns:
        Optional[str]: User-based identifier if available
    """
    # Try to extract user_id from path params
    user_id = request.path_params.get('user_id')
    if user_id:
        return f"user:{user_id}"

    # Try to extract from authorization header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # In a real implementation, you'd decode the JWT to get user_id
        # For now, return a hash of the token as identifier
        return f"token:{hashlib.sha256(token.encode()).hexdigest()[:16]}"

    return None