# API Contracts: Todo AI Chatbot System & MCP

## Overview
This document defines the API contracts for the Todo AI Chatbot system, including the stateless chat endpoint and MCP tool contracts.

## API Endpoints

### Chat Endpoint
**Endpoint:** `POST /api/{user_id}/chat`

#### Request Format
```
{
  "message": "string",
  "conversation_id": "string (optional)"
}
```

#### Response Format
```
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

#### Error Responses
- `401 Unauthorized`: When authentication fails
- `403 Forbidden`: When user tries to access another user's data
- `422 Unprocessable Entity`: When request validation fails
- `500 Internal Server Error`: When an unexpected error occurs

## MCP Tool Contracts

### add_task Contract

#### Description
Creates a new task in the task management system.

#### Request Format
```
{
  "user_id": "string",
  "content": "string",
  "due_date": "string (optional, ISO 8601 format)",
  "priority": "string (optional, low|medium|high)",
  "tags": "array<string> (optional)"
}
```

#### Response Format
```
{
  "success": "boolean",
  "task_id": "string (unique identifier)",
  "message": "string (confirmation message)",
  "created_at": "string (ISO 8601 timestamp)"
}
```

#### Error Responses
- `INVALID_INPUT`: When required fields are missing or invalid
- `TASK_CREATION_FAILED`: When the system cannot create the task

### list_tasks Contract

#### Description
Retrieves a list of tasks based on specified filters.

#### Request Format
```
{
  "user_id": "string",
  "filter": "string (optional, all|pending|completed|overdue)",
  "sort_by": "string (optional, created_at|due_date|priority)",
  "sort_order": "string (optional, asc|desc)",
  "limit": "integer (optional, default 50, max 100)"
}
```

#### Response Format
```
{
  "success": "boolean",
  "tasks": [
    {
      "id": "string",
      "content": "string",
      "status": "string (pending|completed)",
      "due_date": "string (ISO 8601 format)",
      "priority": "string (low|medium|high)",
      "created_at": "string (ISO 8601 timestamp)",
      "completed_at": "string (ISO 8601 timestamp, optional)"
    }
  ],
  "total_count": "integer",
  "message": "string (optional status message)"
}
```

#### Error Responses
- `INVALID_FILTER`: When filter parameter is not recognized
- `LIST_RETRIEVAL_FAILED`: When the system cannot retrieve tasks

### complete_task Contract

#### Description
Marks a task as completed in the task management system.

#### Request Format
```
{
  "user_id": "string",
  "task_id": "string"
}
```

#### Response Format
```
{
  "success": "boolean",
  "task_id": "string",
  "message": "string (confirmation message)",
  "completed_at": "string (ISO 8601 timestamp)"
}
```

#### Error Responses
- `TASK_NOT_FOUND`: When the specified task does not exist
- `TASK_COMPLETION_FAILED`: When the system cannot mark the task as completed

### delete_task Contract

#### Description
Removes a task from the task management system.

#### Request Format
```
{
  "user_id": "string",
  "task_id": "string"
}
```

#### Response Format
```
{
  "success": "boolean",
  "task_id": "string",
  "message": "string (confirmation message)"
}
```

#### Error Responses
- `TASK_NOT_FOUND`: When the specified task does not exist
- `TASK_DELETION_FAILED`: When the system cannot delete the task

### update_task Contract

#### Description
Updates the properties of an existing task in the task management system.

#### Request Format
```
{
  "user_id": "string",
  "task_id": "string",
  "updates": {
    "content": "string (optional)",
    "due_date": "string (optional, ISO 8601 format)",
    "priority": "string (optional, low|medium|high)",
    "status": "string (optional, pending|completed)"
  }
}
```

#### Response Format
```
{
  "success": "boolean",
  "task_id": "string",
  "updated_fields": "array<string>",
  "message": "string (confirmation message)",
  "updated_at": "string (ISO 8601 timestamp)"
}
```

#### Error Responses
- `TASK_NOT_FOUND`: When the specified task does not exist
- `INVALID_INPUT`: When update parameters are invalid
- `TASK_UPDATE_FAILED`: When the system cannot update the task

## Authentication Contract

### Better Auth Integration
All endpoints require authentication via Better Auth.

#### Expected Headers
- `Authorization: Bearer <jwt_token>`
- `Content-Type: application/json`

#### Authentication Flow
1. Request arrives with Authorization header
2. Better Auth middleware validates JWT token
3. User identity is extracted and verified
4. Request proceeds if authentication is successful
5. 401 Unauthorized is returned if authentication fails

## Database Contract

### User Isolation
All database queries must be scoped by user_id to ensure proper data isolation.

#### Validation Rules
- All task queries must filter by user_id
- All conversation queries must filter by user_id
- All message queries must filter by conversation_id linked to user_id
- No user should be able to access another user's data

## Error Handling Contract

### Standard Error Format
```
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Descriptive error message",
  "details": "Additional details about the error (optional)"
}
```

### Common Error Codes
- `UNAUTHORIZED`: Authentication failed
- `FORBIDDEN`: User lacks permission for requested operation
- `NOT_FOUND`: Requested resource does not exist
- `INVALID_INPUT`: Request validation failed
- `INTERNAL_ERROR`: Unexpected system error occurred
- `SERVICE_UNAVAILABLE`: External service is temporarily unavailable