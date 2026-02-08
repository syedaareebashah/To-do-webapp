"""
Main FastAPI application for the Todo AI Chatbot System & MCP Server.

This module sets up the FastAPI application with all necessary configurations,
middleware, and API routes.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.api.endpoints.chat import router as chat_router
from src.api.endpoints.health import router as health_router
from src.api.endpoints.auth import router as auth_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="Todo AI Chatbot API",
        description="Stateless backend system and MCP server for managing todo tasks",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(chat_router, tags=["chat"])
    app.include_router(health_router, tags=["health"])
    app.include_router(auth_router, tags=["auth"])

    return app


app = create_app()


@app.get("/")
async def root():
    """
    Root endpoint for the API.

    Returns:
        dict: Welcome message and API status
    """
    return {
        "message": "Welcome to Todo AI Chatbot API",
        "status": "running",
        "version": "1.0.0"
    }