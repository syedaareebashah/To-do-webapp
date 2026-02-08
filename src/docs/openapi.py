"""
OpenAPI Documentation for the Todo AI Chatbot System.

This module provides comprehensive API documentation with all endpoints,
request/response formats, and usage examples.
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any


def custom_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Generate a custom OpenAPI schema for the Todo AI Chatbot System.

    Args:
        app (FastAPI): The FastAPI application instance

    Returns:
        Dict[str, Any]: The OpenAPI schema dictionary
    """
    if app.openapi_schema:
        return app.openapi_schema

    # Generate the basic OpenAPI schema
    openapi_schema = get_openapi(
        title="Todo AI Chatbot System API",
        version="2.0.0",
        description="""
        # Todo AI Chatbot System API Documentation

        This API provides a comprehensive interface for managing todo tasks through an AI-powered chat interface.

        ## Core Features

        - **AI-Powered Task Management**: Interact with an intelligent agent to create, update, and manage tasks
        - **Stateless Architecture**: All conversation history and task state stored in database
        - **User Isolation**: Secure user data isolation with user_id scoping
        - **MCP Integration**: Standardized tools for AI agent task operations

        ## Authentication

        All endpoints require proper authentication. User identity is established through the user_id in the URL path.

        ## API Principles

        - **Stateless Operations**: Server holds zero runtime state between requests
        - **Consistent Responses**: Same inputs produce same outputs consistently
        - **Reliable Data Integrity**: All operations are atomic and maintain data consistency
        """,
        routes=app.routes,
    )

    # Customize the schema with detailed information
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    # Add custom paths with detailed documentation
    openapi_schema["paths"] = {
        "/api/{user_id}/chat": {
            "post": {
                "summary": "AI Chat Endpoint",
                "description": """
                The primary endpoint for interacting with the AI chatbot. This endpoint handles all conversation
                and task management operations through the AI agent with MCP tools.

                ## Request Processing Flow

                1. **Authentication**: Validates user_id from the path parameter
                2. **Conversation Loading**: Fetches existing conversation history from database
                3. **Message Storage**: Stores the incoming user message in the database
                4. **AI Processing**: Executes the AI agent with available MCP tools
                5. **Response Storage**: Stores the AI's response in the database
                6. **Response**: Returns the AI response and any tool call metadata

                ## MCP Tools Available to AI Agent

                The AI agent has access to the following standardized tools:

                - `add_task`: Create new tasks for the user
                - `list_tasks`: Retrieve user's tasks with filtering options
                - `complete_task`: Mark tasks as completed
                - `delete_task`: Remove tasks
                - `update_task`: Modify task properties

                ## Statelessness Guarantee

                This endpoint is completely stateless - it fetches all necessary conversation
                context from the database for each request, ensuring reliability and consistency.
                """,
                "operationId": "chat_post_api__user_id__chat_post",
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for the user"
                        },
                        "description": "The ID of the user making the request. Used for authentication and data isolation."
                    }
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ChatRequest"
                            },
                            "examples": {
                                "simple_message": {
                                    "summary": "Simple task creation request",
                                    "value": {
                                        "message": "I need to buy groceries tomorrow"
                                    }
                                },
                                "with_conversation_id": {
                                    "summary": "Continuation of existing conversation",
                                    "value": {
                                        "message": "Can you update that to next week?",
                                        "conversation_id": "abc123-def456-ghi789"
                                    }
                                }
                            }
                        }
                    },
                    "required": True
                },
                "responses": {
                    "200": {
                        "description": "Successful response from the AI chatbot",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ChatResponse"
                                },
                                "examples": {
                                    "task_created": {
                                        "summary": "Response after creating a task",
                                        "value": {
                                            "response": "I've created a task for you: 'Buy groceries tomorrow'.",
                                            "conversation_id": "xyz789-uvw012-rst345",
                                            "tool_calls": [
                                                {
                                                    "tool_name": "add_task",
                                                    "parameters": {
                                                        "user_id": "user123",
                                                        "content": "Buy groceries tomorrow",
                                                        "due_date": "2023-12-25T00:00:00Z",
                                                        "priority": "medium"
                                                    },
                                                    "result": {
                                                        "success": True,
                                                        "task_id": "task456",
                                                        "message": "Task 'Buy groceries tomorrow' created successfully"
                                                    }
                                                }
                                            ]
                                        }
                                    },
                                    "tasks_listed": {
                                        "summary": "Response after listing tasks",
                                        "value": {
                                            "response": "Here are your upcoming tasks...",
                                            "conversation_id": "xyz789-uvw012-rst345",
                                            "tool_calls": [
                                                {
                                                    "tool_name": "list_tasks",
                                                    "parameters": {
                                                        "user_id": "user123",
                                                        "filter_type": "pending"
                                                    },
                                                    "result": {
                                                        "success": True,
                                                        "tasks": [
                                                            {
                                                                "id": "task1",
                                                                "content": "Buy groceries",
                                                                "status": "pending",
                                                                "due_date": "2023-12-25T00:00:00Z",
                                                                "priority": "medium",
                                                                "created_at": "2023-12-20T10:30:00Z"
                                                            }
                                                        ],
                                                        "total_count": 1
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request - Invalid input parameters",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized - Invalid or missing authentication",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    },
                    "500": {
                        "description": "Internal Server Error - Unexpected server error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        }
                    }
                },
                "tags": ["Chat", "AI", "Tasks"]
            }
        },
        "/health": {
            "get": {
                "summary": "Health Check",
                "description": "Simple health check endpoint to verify the system is operational.",
                "operationId": "health_get_health_get",
                "responses": {
                    "200": {
                        "description": "System is healthy and operational",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "example": "healthy"
                                        },
                                        "timestamp": {
                                            "type": "string",
                                            "format": "date-time",
                                            "example": "2023-12-01T10:30:00Z"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "tags": ["System"]
            }
        }
    }

    # Define schemas for request/response bodies
    openapi_schema["components"] = {
        "schemas": {
            "ChatRequest": {
                "title": "ChatRequest",
                "required": ["message"],
                "type": "object",
                "properties": {
                    "message": {
                        "title": "Message",
                        "type": "string",
                        "description": "The user's message to the AI chatbot",
                        "example": "I need to schedule a meeting with John next Tuesday"
                    },
                    "conversation_id": {
                        "title": "Conversation Id",
                        "type": "string",
                        "format": "uuid",
                        "description": "Optional ID to continue an existing conversation",
                        "example": "abc123-def456-ghi789"
                    }
                },
                "description": "Request body for sending a message to the AI chatbot"
            },
            "ChatResponse": {
                "title": "ChatResponse",
                "required": ["response", "conversation_id"],
                "type": "object",
                "properties": {
                    "response": {
                        "title": "Response",
                        "type": "string",
                        "description": "The AI chatbot's response to the user's message",
                        "example": "I've created a task for your meeting with John on Tuesday."
                    },
                    "conversation_id": {
                        "title": "Conversation Id",
                        "type": "string",
                        "format": "uuid",
                        "description": "The ID of the conversation, either provided or newly created",
                        "example": "xyz789-uvw012-rst345"
                    },
                    "tool_calls": {
                        "title": "Tool Calls",
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/ToolCall"
                        },
                        "description": "List of MCP tool calls made by the AI agent during processing"
                    }
                },
                "description": "Response from the AI chatbot containing response and metadata"
            },
            "ToolCall": {
                "title": "ToolCall",
                "required": ["tool_name", "parameters", "result"],
                "type": "object",
                "properties": {
                    "tool_name": {
                        "title": "Tool Name",
                        "type": "string",
                        "enum": ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"],
                        "description": "Name of the MCP tool that was called",
                        "example": "add_task"
                    },
                    "parameters": {
                        "title": "Parameters",
                        "type": "object",
                        "description": "Parameters passed to the MCP tool",
                        "example": {
                            "user_id": "user123",
                            "content": "Schedule meeting with John",
                            "due_date": "2023-12-05T10:00:00Z",
                            "priority": "high"
                        }
                    },
                    "result": {
                        "title": "Result",
                        "type": "object",
                        "description": "Result returned by the MCP tool",
                        "example": {
                            "success": True,
                            "task_id": "task456",
                            "message": "Task 'Schedule meeting with John' created successfully"
                        }
                    }
                },
                "description": "Record of an MCP tool call made by the AI agent"
            },
            "ErrorResponse": {
                "title": "ErrorResponse",
                "required": ["detail"],
                "type": "object",
                "properties": {
                    "detail": {
                        "title": "Detail",
                        "type": "string",
                        "description": "Detailed error message",
                        "example": "Invalid input: message cannot be empty"
                    }
                },
                "description": "Standard error response format"
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Example usage function
def setup_api_documentation(app: FastAPI):
    """
    Set up API documentation for the application.

    Args:
        app (FastAPI): The FastAPI application instance
    """
    # Override the openapi method to use our custom schema
    def custom_openapi():
        return custom_openapi_schema(app)

    app.openapi = custom_openapi