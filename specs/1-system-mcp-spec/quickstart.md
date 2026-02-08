# Quickstart Guide: Todo AI Chatbot System & MCP

## Overview
This guide provides a quick introduction to setting up and using the Todo AI Chatbot System with MCP (Model-Context Protocol) server for task management.

## Prerequisites
- Python 3.10+
- FastAPI framework
- Official MCP SDK
- SQLModel ORM
- Neon PostgreSQL database
- Better Auth for user authentication
- Claude Code for AI agent integration

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install fastapi uvicorn sqlmodel httpx python-multipart
# Install MCP SDK according to official documentation
pip install better-auth  # Or whatever the Better Auth package is called
```

### 4. Configure Environment Variables
Create a `.env` file with the following:
```
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/neon_database
BETTER_AUTH_SECRET=your_better_auth_secret_here
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001
```

## Basic Setup

### 1. Initialize Database
```python
from sqlmodel import SQLModel, create_engine
from core.database import engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### 2. Start the MCP Server
```bash
# Start MCP server (typically on a separate port)
uvicorn mcp_server.main:app --host 0.0.0.0 --port 8001
```

### 3. Start the Main API Server
```bash
# Start the main API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Usage Examples

### 1. Send a Chat Message
```bash
curl -X POST "http://localhost:8000/api/user123/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "Add a task to buy groceries",
    "conversation_id": "conv456"
  }'
```

### 2. Create a Task (via MCP tool)
The MCP server handles task creation internally when the AI agent processes requests.

### 3. List User's Tasks (via MCP tool)
The MCP server handles task listing internally when the AI agent processes requests.

## Configuration Options

### FastAPI Settings
```python
# In settings.py
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    better_auth_secret: str = os.getenv("BETTER_AUTH_SECRET")
    mcp_server_host: str = os.getenv("MCP_SERVER_HOST", "localhost")
    mcp_server_port: int = int(os.getenv("MCP_SERVER_PORT", "8001"))
```

### Database Connection Pooling
```python
# In database.py
engine = create_async_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
)
```

## Error Handling

### Common Errors and Solutions

#### Database Connection Issues
- **Cause:** Incorrect DATABASE_URL or database not running
- **Solution:** Verify database connection string and ensure database service is running

#### Authentication Errors
- **Cause:** Invalid JWT token or expired token
- **Solution:** Ensure proper authentication flow is followed and tokens are valid

#### MCP Server Unreachable
- **Cause:** MCP server not running or wrong host/port configuration
- **Solution:** Verify MCP server is running and configuration matches

## Development

### Running in Development Mode
```bash
# Terminal 1: Start MCP server
uvicorn mcp_server.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Start main API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests
```bash
pytest tests/
# Or with coverage
pytest --cov=src tests/
```

### Local Development Server
```bash
# Start both servers locally for development
# MCP server
uvicorn mcp_server.main:app --reload --host 0.0.0.0 --port 8001 &
# Main API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Architecture Components

### FastAPI Backend
- Entry point for all client requests
- Handles authentication via Better Auth
- Single stateless chat endpoint: POST /api/{user_id}/chat
- Manages conversation state reconstruction from database

### MCP Server
- Implements Official MCP SDK
- Exposes task operations as MCP tools:
  - add_task
  - list_tasks
  - complete_task
  - delete_task
  - update_task
- Validates inputs and enforces user isolation
- Persists all state changes to database

### Database Layer
- Uses SQLModel for ORM operations
- Neon PostgreSQL for data persistence
- Proper user scoping with user_id
- Conversation and message history storage

## Production Deployment

### Environment Configuration
```bash
# Use production-grade database URL
DATABASE_URL=postgresql+asyncpg://prod_username:prod_password@neon_host:5432/prod_db

# Secure Better Auth secret
BETTER_AUTH_SECRET=production_secure_secret

# Production server settings
SERVER_HOST=0.0.0.0
SERVER_PORT=80
```

### Containerization Example
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring and Logging

### API Request Logging
The system automatically logs all incoming requests with:
- Request path and method
- User ID (for authorization verification)
- Response status
- Processing time

### MCP Tool Usage Tracking
The system tracks MCP tool usage with:
- Tool name and parameters
- Execution time
- Success/failure status
- User context

## Next Steps
- Review the detailed API documentation
- Explore advanced configuration options
- Set up monitoring and alerting
- Implement custom MCP tools for additional functionality