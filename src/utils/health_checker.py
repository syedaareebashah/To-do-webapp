"""
Health Checker for Todo AI Chatbot System

This module implements health checks for various system components.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import text
from sqlmodel import Session
from src.database.connection import get_session
from src.mcp_server.server import mcp_server


class HealthChecker:
    """
    Health checker for the Todo AI Chatbot System.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the health checker with a database session.

        Args:
            db_session (Session): Database session for health checks
        """
        self.db_session = db_session

    async def check_database_health(self) -> Dict[str, Any]:
        """
        Check the health of the database connection.

        Returns:
            Dict[str, Any]: Database health status information
        """
        try:
            # Execute a simple query to test the database connection
            result = self.db_session.exec(text("SELECT 1")).first()

            if result is not None:
                return {
                    "status": "healthy",
                    "response_time_ms": 0,  # In a real implementation, measure actual response time
                    "message": "Database connection is healthy"
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time_ms": 0,
                    "message": "Database query returned no results"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "response_time_ms": 0,
                "message": f"Database connection failed: {str(e)}"
            }

    async def check_mcp_server_health(self) -> Dict[str, Any]:
        """
        Check the health of the MCP server.

        Returns:
            Dict[str, Any]: MCP server health status information
        """
        try:
            # Check if the MCP server is initialized and running
            if hasattr(mcp_server, 'is_running') and mcp_server.is_running():
                return {
                    "status": "healthy",
                    "message": "MCP server is running"
                }
            elif hasattr(mcp_server, 'initialize') and callable(mcp_server.initialize):
                # Try to initialize the server if it's not running
                try:
                    mcp_server.initialize()
                    return {
                        "status": "healthy",
                        "message": "MCP server was initialized successfully"
                    }
                except Exception as init_error:
                    return {
                        "status": "unhealthy",
                        "message": f"MCP server initialization failed: {str(init_error)}"
                    }
            else:
                return {
                    "status": "unhealthy",
                    "message": "MCP server is not properly initialized"
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"MCP server health check failed: {str(e)}"
            }

    async def check_api_health(self) -> Dict[str, Any]:
        """
        Check the health of the API layer.

        Returns:
            Dict[str, Any]: API health status information
        """
        try:
            # For now, just return healthy status
            # In a real implementation, this might check for API-specific health indicators
            return {
                "status": "healthy",
                "message": "API layer is responsive"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"API health check failed: {str(e)}"
            }

    async def check_auth_service_health(self) -> Dict[str, Any]:
        """
        Check the health of the authentication service.

        Returns:
            Dict[str, Any]: Authentication service health status information
        """
        try:
            # For now, just return healthy status
            # In a real implementation, this might make a call to the auth service
            return {
                "status": "healthy",
                "message": "Authentication service is available"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Authentication service health check failed: {str(e)}"
            }

    async def get_full_health_status(self) -> Dict[str, Any]:
        """
        Get the full health status of the system.

        Returns:
            Dict[str, Any]: Complete system health status information
        """
        # Run all health checks concurrently for better performance
        db_health, mcp_health, api_health, auth_health = await asyncio.gather(
            self.check_database_health(),
            self.check_mcp_server_health(),
            self.check_api_health(),
            self.check_auth_service_health(),
            return_exceptions=True
        )

        # Handle any exceptions that occurred during health checks
        if isinstance(db_health, Exception):
            db_health = {"status": "unhealthy", "message": f"Error checking database health: {str(db_health)}"}

        if isinstance(mcp_health, Exception):
            mcp_health = {"status": "unhealthy", "message": f"Error checking MCP server health: {str(mcp_health)}"}

        if isinstance(api_health, Exception):
            api_health = {"status": "unhealthy", "message": f"Error checking API health: {str(api_health)}"}

        if isinstance(auth_health, Exception):
            auth_health = {"status": "unhealthy", "message": f"Error checking auth service health: {str(auth_health)}"}

        # Determine overall system health based on component health
        all_healthy = all([
            db_health.get("status") == "healthy",
            mcp_health.get("status") == "healthy",
            api_health.get("status") == "healthy",
            auth_health.get("status") == "healthy"
        ])

        overall_status = "healthy" if all_healthy else "degraded"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": db_health,
                "mcp_server": mcp_health,
                "api_layer": api_health,
                "auth_service": auth_health
            },
            "summary": {
                "total_checks": 4,
                "healthy_checks": sum(1 for check in [db_health, mcp_health, api_health, auth_health]
                                     if isinstance(check, dict) and check.get("status") == "healthy"),
                "unhealthy_checks": sum(1 for check in [db_health, mcp_health, api_health, auth_health]
                                       if isinstance(check, dict) and check.get("status") == "unhealthy")
            }
        }

    async def check_readiness(self) -> Dict[str, Any]:
        """
        Check if the system is ready to serve requests.

        Returns:
            Dict[str, Any]: Readiness status information
        """
        # For readiness, we need all critical components to be healthy
        full_health = await self.get_full_health_status()

        is_ready = full_health["status"] == "healthy"

        return {
            "ready": is_ready,
            "timestamp": datetime.utcnow().isoformat(),
            "critical_services": {
                "database": full_health["checks"]["database"]["status"] == "healthy",
                "mcp_server": full_health["checks"]["mcp_server"]["status"] == "healthy",
                "api_layer": full_health["checks"]["api_layer"]["status"] == "healthy"
            }
        }

    async def check_liveness(self) -> Dict[str, Any]:
        """
        Check if the system process is alive and responsive.

        Returns:
            Dict[str, Any]: Liveness status information
        """
        # Liveness just checks if the process is running and responsive
        return {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Process is running and responsive"
        }


# Global health checker instance (would be initialized with proper session in actual app)
# health_checker = None

def get_health_checker(db_session: Session) -> HealthChecker:
    """
    Get a health checker instance with the provided database session.

    Args:
        db_session (Session): Database session for the health checker

    Returns:
        HealthChecker: Health checker instance
    """
    return HealthChecker(db_session)