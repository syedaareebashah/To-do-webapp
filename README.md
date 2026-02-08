# Todo AI Chatbot System

A stateless backend system with MCP server integration that enables an AI agent to manage todo tasks through standardized MCP tools while persisting all state in a database.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [MCP Tools](#mcp-tools)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Features

- **AI-Powered Task Management**: Natural language interface for creating and managing tasks
- **Stateless Architecture**: No in-memory state between requests, all data persisted in database
- **MCP Integration**: Standardized tools for AI agent task operations
- **User Isolation**: Secure data isolation with user_id scoping
- **Real-time Conversations**: Persistent conversation history with context
- **Task Operations**: Full CRUD operations for tasks with filtering and sorting
- **Error Handling**: Comprehensive error handling and validation
- **Scalable Design**: Designed for horizontal scaling

## Architecture

The system follows a stateless architecture with clear separation of concerns:

```
Client Request
      ↓
FastAPI Router
      ↓
Better Auth Middleware (Validate user_id)
      ↓
Chat Endpoint Handler
      ↓
Database Service Layer
      ↓
SQLModel Async Sessions
      ↓
Neon PostgreSQL
      ↓
MCP Server
      ↓
MCP Tools (add_task, list_tasks, complete_task, delete_task, update_task)
```

### Components

- **FastAPI Backend**: Handles HTTP requests/responses and authentication
- **Chat Endpoint**: Fetches conversation history, stores messages, executes AI agent
- **MCP Server**: Implements Official MCP SDK with standardized tools
- **Database Layer**: SQLModel with Neon PostgreSQL for persistent data
- **Task Services**: Business logic for task operations with user isolation

## Prerequisites

- Python 3.11+
- pip package manager
- Git
- Access to Neon PostgreSQL database
- (Optional) Docker for containerized deployment

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd hackathonnII/Hackathon_II/phase_III
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
NEON_DB_URL=your-neon-db-url-here
```

## Configuration

### Database Configuration

The system uses Neon PostgreSQL with SQLModel. Update the `DATABASE_URL` in your `.env` file to point to your Neon database instance.

### MCP Server Configuration

The MCP server is configured to use the Official MCP SDK. The tools are automatically registered when the server starts.

### Authentication

Better Auth is used for user authentication. The system validates user_id from the request path to ensure proper data isolation.

## Usage

### Running Locally

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### API Endpoints

#### Chat Endpoint

```
POST /api/{user_id}/chat
```

**Description**: Main endpoint for interacting with the AI chatbot.

**Path Parameters**:
- `user_id` (string, required): User identifier for authentication and data isolation

**Request Body**:
```json
{
  "message": "string",
  "conversation_id": "string (optional)"
}
```

**Response**:
```json
{
  "response": "string",
  "conversation_id": "string",
  "tool_calls": [
    {
      "tool_name": "string",
      "parameters": "object",
      "result": "object"
    }
  ]
}
```

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/user123/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to buy groceries"}'
```

### MCP Tools

The AI agent has access to the following MCP tools:

#### add_task
Create a new task for the user.

**Parameters**:
- `user_id` (string): ID of the user creating the task
- `content` (string): Content/description of the task
- `due_date` (string, optional): Due date for the task (ISO format)
- `priority` (string): Priority level (low, medium, high)

#### list_tasks
Retrieve tasks for a user.

**Parameters**:
- `user_id` (string): ID of the user whose tasks to list
- `filter_type` (string): Type of tasks to filter (all, pending, completed, overdue)
- `sort_by` (string): Field to sort by (created_at, due_date, priority)
- `sort_order` (string): Sort order (asc, desc)
- `limit` (integer): Maximum number of tasks to return

#### complete_task
Mark a task as completed.

**Parameters**:
- `user_id` (string): ID of the user who owns the task
- `task_id` (string): ID of the task to complete

#### delete_task
Remove a task.

**Parameters**:
- `user_id` (string): ID of the user who owns the task
- `task_id` (string): ID of the task to delete

#### update_task
Modify a task.

**Parameters**:
- `user_id` (string): ID of the user who owns the task
- `task_id` (string): ID of the task to update
- `updates` (object): Fields to update

## Development

### Project Structure

```
├── src/                    # Source code
│   ├── app/               # FastAPI application
│   ├── database/          # Database connection and models
│   ├── models/            # SQLModel definitions
│   ├── mcp_server/        # MCP server and tools
│   ├── services/          # Business logic
│   └── docs/              # Documentation
├── specs/                 # Feature specifications
├── tests/                 # Test files
├── alembic/               # Database migrations
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
└── README.md             # This file
```

### Adding New Features

1. Create a new branch for your feature
2. Add your implementation following the existing patterns
3. Write tests for your new functionality
4. Update documentation as needed
5. Submit a pull request

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file.py

# Run tests with coverage
pytest --cov=src
```

## Testing

### Unit Tests

Unit tests are located in the `tests/` directory and test individual components.

### Integration Tests

Integration tests verify that different parts of the system work together correctly.

### End-to-End Tests

E2E tests simulate real user interactions with the system.

## Deployment

### Railway Deployment

The application is configured for deployment on Railway with the Procfile:

```
web: uvicorn src.app.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables for Production

- `DATABASE_URL`: Production database URL
- `SECRET_KEY`: Production secret key
- `ALGORITHM`: Token algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Docker Deployment

If using Docker:

```bash
# Build the image
docker build -t todo-chatbot .

# Run the container
docker run -p 8000:8000 todo-chatbot
```

## Troubleshooting

### Common Issues

#### Database Connection Issues
- Verify your `DATABASE_URL` is correct
- Check that your database credentials are valid
- Ensure your database is accessible from your network

#### Authentication Issues
- Confirm the user_id in the request path is valid
- Check that Better Auth is properly configured
- Verify the authentication middleware is working

#### MCP Tool Issues
- Ensure the MCP server is properly initialized
- Check that all required MCP tools are registered
- Verify the database connection for MCP operations

#### Statelessness Issues
- Confirm that conversation history is properly fetched from the database
- Verify that no in-memory state is being used between requests
- Check that all data is persisted to the database

### Logging

The system logs important events and errors. Check the logs for detailed information about issues:

```
# Application logs
tail -f logs/app.log

# Error logs
tail -f logs/error.log
```

### Health Checks

Monitor the health of your deployment with the health check endpoint:

```
GET /health
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the development team.