"""
MCP Tool Interface Wrapper for Todo AI Chatbot Agent

This module provides a wrapper around MCP tools for the agent to interact with.
"""

import json
from typing import Dict, Any, Optional
from ..config.logging_config import logger


class MCPTOOLInterface:
    """
    Interface wrapper for MCP tools that the agent interacts with.
    This class simulates the interaction with actual MCP tools.
    """

    def __init__(self):
        """
        Initialize the MCP tool interface.
        """
        # In a real implementation, this would connect to actual MCP tools
        # For simulation purposes, we'll maintain a simple in-memory store
        self._task_store = {}
        self._next_task_id = 1

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP tool with the given parameters.

        Args:
            tool_name (str): Name of the MCP tool to execute
            parameters (Dict[str, Any]): Parameters for the tool

        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        logger.info(f"Executing MCP tool: {tool_name} with parameters: {parameters}")

        try:
            if tool_name == "add_task":
                return self._execute_add_task(parameters)
            elif tool_name == "list_tasks":
                return self._execute_list_tasks(parameters)
            elif tool_name == "complete_task":
                return self._execute_complete_task(parameters)
            elif tool_name == "delete_task":
                return self._execute_delete_task(parameters)
            elif tool_name == "update_task":
                return self._execute_update_task(parameters)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "message": f"Tool {tool_name} is not supported"
                }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute {tool_name}"
            }

    def _execute_add_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the add_task tool.

        Args:
            parameters (Dict[str, Any]): Parameters for adding a task

        Returns:
            Dict[str, Any]: Result of adding the task
        """
        # Validate required parameters
        if "task_content" not in parameters:
            return {
                "success": False,
                "error": "Missing required parameter: task_content",
                "message": "Task content is required to create a task"
            }

        # Generate a new task ID
        task_id = f"task_{self._next_task_id}"
        self._next_task_id += 1

        # Create the task object
        task = {
            "id": task_id,
            "content": parameters["task_content"],
            "status": "pending",
            "created_at": self._get_current_timestamp(),
            "due_date": parameters.get("due_date"),
            "priority": parameters.get("priority", "medium"),
            "tags": parameters.get("tags", [])
        }

        # Store the task
        self._task_store[task_id] = task

        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task '{parameters['task_content']}' added successfully",
            "created_at": task["created_at"]
        }

    def _execute_list_tasks(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the list_tasks tool.

        Args:
            parameters (Dict[str, Any]): Parameters for listing tasks

        Returns:
            Dict[str, Any]: Result of listing tasks
        """
        # Get filter parameters
        filter_type = parameters.get("filter", "all")
        sort_by = parameters.get("sort_by", "created_at")
        sort_order = parameters.get("sort_order", "asc")
        limit = parameters.get("limit", 50)

        # Filter tasks based on the filter type
        filtered_tasks = list(self._task_store.values())

        if filter_type == "pending":
            filtered_tasks = [task for task in filtered_tasks if task["status"] == "pending"]
        elif filter_type == "completed":
            filtered_tasks = [task for task in filtered_tasks if task["status"] == "completed"]
        elif filter_type == "overdue":
            # For simplicity, we'll consider tasks without due dates as not overdue
            # In a real implementation, this would compare with current date
            filtered_tasks = [task for task in filtered_tasks if task.get("due_date") and self._is_overdue(task.get("due_date"))]

        # Sort tasks
        reverse_sort = sort_order == "desc"
        if sort_by == "due_date":
            filtered_tasks.sort(key=lambda t: (t.get("due_date") or ""), reverse=reverse_sort)
        elif sort_by == "priority":
            priority_order = {"high": 3, "medium": 2, "low": 1}
            filtered_tasks.sort(key=lambda t: priority_order.get(t.get("priority", "medium"), 0), reverse=reverse_sort)
        else:  # default to created_at
            filtered_tasks.sort(key=lambda t: t.get("created_at", ""), reverse=reverse_sort)

        # Apply limit
        limited_tasks = filtered_tasks[:limit]

        return {
            "success": True,
            "tasks": limited_tasks,
            "total_count": len(filtered_tasks),
            "message": f"Found {len(limited_tasks)} tasks"
        }

    def _execute_complete_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete_task tool.

        Args:
            parameters (Dict[str, Any]): Parameters for completing a task

        Returns:
            Dict[str, Any]: Result of completing the task
        """
        task_id = parameters.get("task_id")

        if not task_id:
            return {
                "success": False,
                "error": "Missing required parameter: task_id",
                "message": "Task ID is required to complete a task"
            }

        if task_id not in self._task_store:
            return {
                "success": False,
                "error": "TASK_NOT_FOUND",
                "message": f"Task with ID {task_id} not found"
            }

        # Update the task status
        task = self._task_store[task_id]
        task["status"] = "completed"
        task["completed_at"] = self._get_current_timestamp()

        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task {task_id} marked as completed",
            "completed_at": task["completed_at"]
        }

    def _execute_delete_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the delete_task tool.

        Args:
            parameters (Dict[str, Any]): Parameters for deleting a task

        Returns:
            Dict[str, Any]: Result of deleting the task
        """
        task_id = parameters.get("task_id")

        if not task_id:
            return {
                "success": False,
                "error": "Missing required parameter: task_id",
                "message": "Task ID is required to delete a task"
            }

        if task_id not in self._task_store:
            return {
                "success": False,
                "error": "TASK_NOT_FOUND",
                "message": f"Task with ID {task_id} not found"
            }

        # Remove the task
        del self._task_store[task_id]

        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task {task_id} has been deleted"
        }

    def _execute_update_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the update_task tool.

        Args:
            parameters (Dict[str, Any]): Parameters for updating a task

        Returns:
            Dict[str, Any]: Result of updating the task
        """
        task_id = parameters.get("task_id")

        if not task_id:
            return {
                "success": False,
                "error": "Missing required parameter: task_id",
                "message": "Task ID is required to update a task"
            }

        if task_id not in self._task_store:
            return {
                "success": False,
                "error": "TASK_NOT_FOUND",
                "message": f"Task with ID {task_id} not found"
            }

        # Get the updates
        updates = parameters.get("updates", {})

        if not updates:
            return {
                "success": False,
                "error": "No updates provided",
                "message": "No updates were provided for the task"
            }

        # Apply updates to the task
        task = self._task_store[task_id]
        updated_fields = []

        for field, value in updates.items():
            if field in task:
                task[field] = value
                updated_fields.append(field)

        # Update the modified timestamp
        task["updated_at"] = self._get_current_timestamp()

        return {
            "success": True,
            "task_id": task_id,
            "updated_fields": updated_fields,
            "message": f"Task {task_id} has been updated",
            "updated_at": task["updated_at"]
        }

    def _get_current_timestamp(self) -> str:
        """
        Get the current timestamp in ISO format.

        Returns:
            str: Current timestamp in ISO format
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def _is_overdue(self, due_date: str) -> bool:
        """
        Check if a task is overdue.

        Args:
            due_date (str): Due date string

        Returns:
            bool: True if the task is overdue, False otherwise
        """
        # For simplicity, this is a stub implementation
        # In a real implementation, this would compare the due date with current date
        return False

    def get_task_store_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the task store.

        Returns:
            Dict[str, Any]: Statistics about the task store
        """
        stats = {
            "total_tasks": len(self._task_store),
            "pending_tasks": len([t for t in self._task_store.values() if t["status"] == "pending"]),
            "completed_tasks": len([t for t in self._task_store.values() if t["status"] == "completed"])
        }
        return stats

    def reset_task_store(self) -> None:
        """
        Reset the task store for testing purposes.
        """
        self._task_store = {}
        self._next_task_id = 1