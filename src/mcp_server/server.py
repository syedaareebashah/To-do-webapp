"""
MCP Server implementation for the Todo AI Chatbot System.

This module implements the MCP server using the Official MCP SDK.
"""

from typing import Dict, Any, Optional
import asyncio
from src.models.task import TaskCreate, TaskUpdate
from src.services.task_service import TaskService
from src.database.connection import get_db_session
from src.models.user import User


class MCPServer:
    """
    MCP Server class that manages the MCP tools and their execution.

    This class would typically interface with the Official MCP SDK to register
    and manage the various tools available to the AI agent.
    """

    def __init__(self):
        """
        Initialize the MCP Server with the available tools.
        """
        self.tools = {}
        self.initialized = False

        # Register the available tools
        self._register_tools()

    def _register_tools(self):
        """
        Register the available MCP tools with their respective functions.
        """
        self.tools = {
            "add_task": self.add_task,
            "list_tasks": self.list_tasks,
            "complete_task": self.complete_task,
            "delete_task": self.delete_task,
            "update_task": self.update_task
        }

        self.initialized = True
        print("MCP Server initialized with tools:", list(self.tools.keys()))

    async def add_task(self, user_id: str, content: str, due_date: Optional[str] = None,
                      priority: str = "medium", tags: Optional[list] = None) -> Dict[str, Any]:
        """
        MCP tool to add a new task.

        Args:
            user_id (str): ID of the user creating the task
            content (str): Content/description of the task
            due_date (Optional[str]): Due date for the task (ISO format)
            priority (str): Priority level (low, medium, high)
            tags (Optional[list]): List of tags for the task

        Returns:
            Dict[str, Any]: Result of the operation with task details
        """
        try:
            # Validate inputs
            if not content or not content.strip():
                return {
                    "success": False,
                    "error": "INVALID_INPUT",
                    "message": "Task content is required and cannot be empty"
                }

            # Create task data
            task_data = {
                "user_id": user_id,
                "content": content.strip(),
                "due_date": due_date,
                "priority": priority
            }

            # Use the task service to create the task
            with get_db_session() as session:
                task_service = TaskService(session)
                task_create = TaskCreate(**task_data)
                created_task = task_service.create_task(task_create)

                # Extract the data we need before the session closes
                task_id = str(created_task.id)
                created_at = created_task.created_at.isoformat()

            return {
                "success": True,
                "task_id": task_id,
                "message": f"Task '{content}' created successfully",
                "created_at": created_at
            }

        except Exception as e:
            return {
                "success": False,
                "error": "TASK_CREATION_FAILED",
                "message": f"Failed to create task: {str(e)}"
            }

    async def list_tasks(self, user_id: str, filter_type: str = "all",
                        sort_by: str = "created_at", sort_order: str = "asc",
                        limit: int = 50) -> Dict[str, Any]:
        """
        MCP tool to list tasks for a user.

        Args:
            user_id (str): ID of the user whose tasks to list
            filter_type (str): Type of tasks to filter (all, pending, completed, overdue)
            sort_by (str): Field to sort by (created_at, due_date, priority)
            sort_order (str): Sort order (asc, desc)
            limit (int): Maximum number of tasks to return

        Returns:
            Dict[str, Any]: List of tasks and metadata
        """
        try:
            # Validate inputs
            valid_filters = ["all", "pending", "completed", "overdue"]
            if filter_type not in valid_filters:
                return {
                    "success": False,
                    "error": "INVALID_FILTER",
                    "message": f"Invalid filter type. Valid options: {valid_filters}"
                }

            # Use the task service to get tasks
            with get_db_session() as session:
                task_service = TaskService(session)
                tasks = task_service.get_tasks_by_user(
                    user_id=user_id,
                    status_filter=filter_type if filter_type != "all" else None,
                    limit=limit
                )

                # Format the tasks for return while the session is still active
                formatted_tasks = []
                for task in tasks:
                    formatted_tasks.append({
                        "id": str(task.id),
                        "content": task.content,
                        "status": task.status.value,
                        "due_date": task.due_date.isoformat() if task.due_date else None,
                        "priority": task.priority.value,
                        "created_at": task.created_at.isoformat(),
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None
                    })

            return {
                "success": True,
                "tasks": formatted_tasks,
                "total_count": len(formatted_tasks),
                "message": f"Retrieved {len(formatted_tasks)} tasks for user {user_id}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": "LIST_RETRIEVAL_FAILED",
                "message": f"Failed to retrieve tasks: {str(e)}"
            }

    async def complete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        MCP tool to mark a task as completed.

        Args:
            user_id (str): ID of the user who owns the task
            task_id (str): ID of the task to complete

        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            # Use the task service to update the task
            with get_db_session() as session:
                task_service = TaskService(session)
                updated_task = task_service.update_task_status(
                    task_id=task_id,
                    user_id=user_id,
                    new_status="completed"
                )

                if not updated_task:
                    return {
                        "success": False,
                        "error": "TASK_NOT_FOUND",
                        "message": f"Task with ID {task_id} not found for user {user_id}"
                    }

                # Extract the data we need before the session closes
                completed_at = updated_task.completed_at.isoformat() if updated_task.completed_at else None

            return {
                "success": True,
                "task_id": task_id,
                "message": f"Task {task_id} marked as completed",
                "completed_at": completed_at
            }

        except Exception as e:
            return {
                "success": False,
                "error": "TASK_COMPLETION_FAILED",
                "message": f"Failed to complete task: {str(e)}"
            }

    async def delete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        MCP tool to delete a task.

        Args:
            user_id (str): ID of the user who owns the task
            task_id (str): ID of the task to delete

        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            # Use the task service to delete the task
            with get_db_session() as session:
                task_service = TaskService(session)
                deleted_task = task_service.delete_task(
                    task_id=task_id,
                    user_id=user_id
                )

                if not deleted_task:
                    return {
                        "success": False,
                        "error": "TASK_NOT_FOUND",
                        "message": f"Task with ID {task_id} not found for user {user_id}"
                    }

                # Extract the data we need before the session closes
                deleted_task_id = str(deleted_task.id)

            return {
                "success": True,
                "task_id": deleted_task_id,
                "message": f"Task {deleted_task_id} has been deleted"
            }

        except Exception as e:
            return {
                "success": False,
                "error": "TASK_DELETION_FAILED",
                "message": f"Failed to delete task: {str(e)}"
            }

    async def update_task(self, user_id: str, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        MCP tool to update a task.

        Args:
            user_id (str): ID of the user who owns the task
            task_id (str): ID of the task to update
            updates (Dict[str, Any]): Fields to update

        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            # Validate updates
            allowed_updates = {"content", "due_date", "priority", "status"}
            invalid_fields = set(updates.keys()) - allowed_updates
            if invalid_fields:
                return {
                    "success": False,
                    "error": "INVALID_INPUT",
                    "message": f"Invalid fields in updates: {list(invalid_fields)}"
                }

            # Use the task service to update the task
            with get_db_session() as session:
                task_service = TaskService(session)
                task_update_data = TaskUpdate(**updates)
                updated_task = task_service.partial_update_task(
                    task_id=task_id,
                    user_id=user_id,
                    task_update=task_update_data
                )

                if not updated_task:
                    return {
                        "success": False,
                        "error": "TASK_NOT_FOUND",
                        "message": f"Task with ID {task_id} not found for user {user_id}"
                    }

                # Identify which fields were updated
                updated_fields = []
                for field, value in updates.items():
                    if hasattr(updated_task, field):
                        updated_fields.append(field)

                # Extract the data we need before the session closes
                updated_at = updated_task.updated_at.isoformat() if hasattr(updated_task, 'updated_at') else None

            return {
                "success": True,
                "task_id": task_id,
                "updated_fields": updated_fields,
                "message": f"Task {task_id} has been updated",
                "updated_at": updated_at
            }

        except Exception as e:
            return {
                "success": False,
                "error": "TASK_UPDATE_FAILED",
                "message": f"Failed to update task: {str(e)}"
            }

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool with the given parameters.

        Args:
            tool_name (str): Name of the MCP tool to execute
            parameters (Dict[str, Any]): Parameters for the tool

        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "message": f"Tool {tool_name} is not supported"
            }

        try:
            # Get the appropriate tool function
            tool_func = self.tools[tool_name]

            # Call the tool function with the provided parameters
            result = await tool_func(**parameters)
            return result
        except TypeError as e:
            # Handle case where parameters don't match function signature
            return {
                "success": False,
                "error": "PARAMETER_MISMATCH",
                "message": f"Parameter mismatch for tool {tool_name}: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "TOOL_EXECUTION_FAILED",
                "message": f"Failed to execute {tool_name}: {str(e)}"
            }


# Global MCP server instance
mcp_server = MCPServer()


def get_mcp_server():
    """
    Get the global MCP server instance.

    Returns:
        MCPServer: The MCP server instance
    """
    return mcp_server