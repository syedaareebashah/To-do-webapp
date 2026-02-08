"""
API Error Handlers for Todo AI Chatbot System

This module implements centralized error handling for API endpoints.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Dict, Any
from src.api.responses.error_response import ErrorResponse
from src.config.logging_config import logger
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions globally.

    Args:
        request (Request): The incoming request
        exc (HTTPException): The HTTP exception that occurred

    Returns:
        JSONResponse: Formatted error response
    """
    logger.error(f"HTTP exception: {exc.detail} for URL: {request.url}")

    error_response = ErrorResponse(
        success=False,
        error_code="HTTP_ERROR",
        message=str(exc.detail),
        details={
            "status_code": exc.status_code,
            "url": str(request.url)
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors globally.

    Args:
        request (Request): The incoming request
        exc (RequestValidationError): The validation error that occurred

    Returns:
        JSONResponse: Formatted error response
    """
    logger.error(f"Validation error: {exc.errors()} for URL: {request.url}")

    error_response = ErrorResponse(
        success=False,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={
            "errors": exc.errors(),
            "url": str(request.url)
        }
    )

    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )


async def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors globally.

    Args:
        request (Request): The incoming request
        exc (ValidationError): The validation error that occurred

    Returns:
        JSONResponse: Formatted error response
    """
    logger.error(f"Pydantic validation error: {exc.errors()} for URL: {request.url}")

    error_response = ErrorResponse(
        success=False,
        error_code="PYDANTIC_VALIDATION_ERROR",
        message="Data validation failed",
        details={
            "errors": exc.errors(),
            "url": str(request.url)
        }
    )

    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle database-related exceptions globally.

    Args:
        request (Request): The incoming request
        exc (SQLAlchemyError): The database exception that occurred

    Returns:
        JSONResponse: Formatted error response
    """
    logger.error(f"Database exception: {str(exc)} for URL: {request.url}")

    error_response = ErrorResponse(
        success=False,
        error_code="DATABASE_ERROR",
        message="A database error occurred. Please try again later.",
        details={
            "error_type": type(exc).__name__,
            "url": str(request.url)
        }
    )

    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


async def mcp_tool_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle exceptions from MCP tool calls.

    Args:
        request (Request): The incoming request
        exc (Exception): The exception from the MCP tool

    Returns:
        JSONResponse: Formatted error response
    """
    logger.error(f"MCP tool exception: {str(exc)} for URL: {request.url}")

    error_response = ErrorResponse(
        success=False,
        error_code="MCP_TOOL_ERROR",
        message="An error occurred while executing the task operation.",
        details={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "url": str(request.url)
        }
    )

    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions globally.

    Args:
        request (Request): The incoming request
        exc (Exception): The exception that occurred

    Returns:
        JSONResponse: Formatted error response
    """
    logger.error(f"General exception: {str(exc)} for URL: {request.url}", exc_info=True)

    error_response = ErrorResponse(
        success=False,
        error_code="INTERNAL_ERROR",
        message="An internal server error occurred. Our team has been notified.",
        details={
            "error_type": type(exc).__name__,
            "url": str(request.url)
        }
    )

    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )


def add_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("All API exception handlers registered successfully")