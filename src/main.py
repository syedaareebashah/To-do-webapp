"""
Todo AI Chatbot System & MCP Server - Main Application Entry Point

This module initializes the FastAPI application, sets up routes, and starts the server.
It also initializes the MCP server alongside the web API.
"""

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.endpoints.chat import router as chat_router
from src.mcp_server.server import mcp_server
from src.database.session import init_db


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="Todo AI Chatbot API",
        description="Stateless backend system and MCP server for AI-powered todo management",
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

    # Include API routes
    app.include_router(chat_router, prefix="/api", tags=["chat"])

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "todo-ai-chatbot"}

    return app


# Create the FastAPI app instance
app = create_app()


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler to initialize database and MCP server.
    """
    print("Initializing database...")
    init_db()

    print("Starting MCP server...")
    # Initialize the MCP server
    mcp_server.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler for cleanup operations.
    """
    print("Shutting down MCP server...")
    # Perform any necessary cleanup for the MCP server
    mcp_server.shutdown()


if __name__ == "__main__":
    # Start both the FastAPI web server and the MCP server
    import threading

    # Start the MCP server in a separate thread
    def start_mcp_server():
        mcp_server.run()

    mcp_thread = threading.Thread(target=start_mcp_server, daemon=True)
    mcp_thread.start()

    # Start the FastAPI web server
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )