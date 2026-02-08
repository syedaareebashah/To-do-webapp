# MCP Tool Contracts for Todo AI Chatbot

## Overview
This document defines the contract for MCP tools that the Todo AI Chatbot agent will interact with. These contracts specify the expected inputs, outputs, and error behaviors for each tool.

## add_task Contract

### Description
Creates a new task in the task management system.

### Request Format
```
{
  "task_content": "string",
  "due_date": "string (optional, ISO 8601 format)",
  "priority": "string (optional, low|medium|high)",
  "tags": "array<string> (optional)"
}
```

### Response Format
```
{
  "success": "boolean",
  "task_id": "string (unique identifier)",
  "message": "string (confirmation message)",
  "created_at": "string (ISO 8601 timestamp)"
}
```

### Error Responses
- `INVALID_INPUT`: When required fields are missing or invalid
- `TASK_CREATION_FAILED`: When the system cannot create the task

## list_tasks Contract

### Description
Retrieves a list of tasks based on specified filters.

### Request Format
```
{
  "filter": "string (optional, all|pending|completed|overdue)",
  "sort_by": "string (optional, created_at|due_date|priority)",
  "sort_order": "string (optional, asc|desc)",
  "limit": "integer (optional, default 50, max 100)"
}
```

### Response Format
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

### Error Responses
- `INVALID_FILTER`: When filter parameter is not recognized
- `LIST_RETRIEVAL_FAILED`: When the system cannot retrieve tasks

## complete_task Contract

### Description
Marks a task as completed in the task management system.

### Request Format
```
{
  "task_id": "string (required)"
}
```

### Response Format
```
{
  "success": "boolean",
  "task_id": "string",
  "message": "string (confirmation message)",
  "completed_at": "string (ISO 8601 timestamp)"
}
```

### Error Responses
- `TASK_NOT_FOUND`: When the specified task does not exist
- `TASK_COMPLETION_FAILED`: When the system cannot mark the task as completed

## delete_task Contract

### Description
Removes a task from the task management system.

### Request Format
```
{
  "task_id": "string (required)"
}
```

### Response Format
```
{
  "success": "boolean",
  "task_id": "string",
  "message": "string (confirmation message)"
}
```

### Error Responses
- `TASK_NOT_FOUND`: When the specified task does not exist
- `TASK_DELETION_FAILED`: When the system cannot delete the task

## update_task Contract

### Description
Updates the properties of an existing task in the task management system.

### Request Format
```
{
  "task_id": "string (required)",
  "updates": {
    "content": "string (optional)",
    "due_date": "string (optional, ISO 8601 format)",
    "priority": "string (optional, low|medium|high)",
    "status": "string (optional, pending|completed)"
  }
}
```

### Response Format
```
{
  "success": "boolean",
  "task_id": "string",
  "updated_fields": "array<string>",
  "message": "string (confirmation message)",
  "updated_at": "string (ISO 8601 timestamp)"
}
```

### Error Responses
- `TASK_NOT_FOUND`: When the specified task does not exist
- `INVALID_INPUT`: When update parameters are invalid
- `TASK_UPDATE_FAILED`: When the system cannot update the task