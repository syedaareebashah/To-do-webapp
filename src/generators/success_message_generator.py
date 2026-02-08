"""
Success Message Generator for Todo AI Chatbot Agent

This module generates success messages for various operations.
"""

from typing import Dict, Any
from ..models.intent import Intent, IntentType


class SuccessMessageGenerator:
    """
    Generates success messages for different types of operations.
    """

    def __init__(self):
        """
        Initialize the success message generator.
        """
        # Define templates for different success messages
        self.message_templates = {
            IntentType.ADD_TASK: "Added task: '{task_content}'",
            IntentType.LIST_TASKS: "Here are your tasks: {task_list}",
            IntentType.COMPLETE_TASK: "Task {task_id} marked as complete",
            IntentType.DELETE_TASK: "Task {task_id} has been deleted",
            IntentType.UPDATE_TASK: "Task {task_id} has been updated",
            "generic_success": "Operation completed successfully: {operation_type}"
        }

    def generate_add_task_success(self, task_content: str, task_id: str = None) -> str:
        """
        Generate a success message for adding a task.

        Args:
            task_content (str): The content of the added task
            task_id (str, optional): The ID of the added task

        Returns:
            str: The success message
        """
        message = self.message_templates[IntentType.ADD_TASK].format(task_content=task_content)

        if task_id:
            message += f" (ID: {task_id})"

        return message

    def generate_list_tasks_success(self, tasks: list) -> str:
        """
        Generate a success message for listing tasks.

        Args:
            tasks (list): List of task dictionaries

        Returns:
            str: The success message
        """
        if not tasks:
            return "You don't have any tasks."

        # Format the task list for display
        formatted_tasks = []
        for task in tasks:
            task_id = task.get('id', 'unknown')
            content = task.get('content', 'Unnamed task')
            status = task.get('status', 'pending')
            formatted_tasks.append(f"{task_id}. {content} [{status}]")

        task_list = "\n".join(formatted_tasks)
        message = self.message_templates[IntentType.LIST_TASKS].format(task_list=task_list)

        return message

    def generate_complete_task_success(self, task_id: str) -> str:
        """
        Generate a success message for completing a task.

        Args:
            task_id (str): The ID of the completed task

        Returns:
            str: The success message
        """
        message = self.message_templates[IntentType.COMPLETE_TASK].format(task_id=task_id)
        return message

    def generate_delete_task_success(self, task_id: str) -> str:
        """
        Generate a success message for deleting a task.

        Args:
            task_id (str): The ID of the deleted task

        Returns:
            str: The success message
        """
        message = self.message_templates[IntentType.DELETE_TASK].format(task_id=task_id)
        return message

    def generate_update_task_success(self, task_id: str, updated_fields: list = None) -> str:
        """
        Generate a success message for updating a task.

        Args:
            task_id (str): The ID of the updated task
            updated_fields (list, optional): List of fields that were updated

        Returns:
            str: The success message
        """
        message = self.message_templates[IntentType.UPDATE_TASK].format(task_id=task_id)

        if updated_fields:
            fields_str = ", ".join(updated_fields)
            message += f" (updated fields: {fields_str})"

        return message

    def generate_success_message(self, intent: Intent, result: Dict[str, Any]) -> str:
        """
        Generate a success message based on the intent and result.

        Args:
            intent (Intent): The intent that was executed
            result (Dict[str, Any]): The result from the tool execution

        Returns:
            str: The appropriate success message
        """
        intent_type = intent.type

        if intent_type == IntentType.ADD_TASK:
            task_content = intent.parameters.get('task_content', 'unknown task')
            task_id = result.get('task_id', 'unknown')
            return self.generate_add_task_success(task_content, task_id)

        elif intent_type == IntentType.LIST_TASKS:
            tasks = result.get('tasks', [])
            return self.generate_list_tasks_success(tasks)

        elif intent_type == IntentType.COMPLETE_TASK:
            task_id = intent.parameters.get('task_id', result.get('task_id', 'unknown'))
            return self.generate_complete_task_success(task_id)

        elif intent_type == IntentType.DELETE_TASK:
            task_id = intent.parameters.get('task_id', result.get('task_id', 'unknown'))
            return self.generate_delete_task_success(task_id)

        elif intent_type == IntentType.UPDATE_TASK:
            task_id = intent.parameters.get('task_id', result.get('task_id', 'unknown'))
            updated_fields = result.get('updated_fields', [])
            return self.generate_update_task_success(task_id, updated_fields)

        else:
            # For any other intent type, use a generic success message
            return self.message_templates["generic_success"].format(operation_type=intent_type.value.lower())

    def generate_custom_success_message(self, operation_type: str, details: Dict[str, Any] = None) -> str:
        """
        Generate a custom success message with operation type and details.

        Args:
            operation_type (str): The type of operation
            details (Dict[str, Any], optional): Additional details for the message

        Returns:
            str: The custom success message
        """
        if details:
            # Format details into the message
            detail_parts = []
            for key, value in details.items():
                if isinstance(value, (dict, list)):
                    # For complex values, just mention the key
                    detail_parts.append(str(key))
                else:
                    detail_parts.append(f"{key}: {value}")

            details_str = ", ".join(detail_parts)
            return f"{operation_type.capitalize()} completed successfully with {details_str}"
        else:
            return f"{operation_type.capitalize()} completed successfully"