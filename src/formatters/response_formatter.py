"""
Response Formatter for Todo AI Chatbot Agent

This module formats responses for the agent based on the action taken.
"""

from typing import Dict, Any, Optional
from src.models.intent import Intent
from src.models.response_template import PREDEFINED_TEMPLATES, ActionType


class ResponseFormatter:
    """
    Formats responses for the agent based on the action taken.
    """

    def __init__(self):
        """
        Initialize the response formatter.
        """
        self.templates = PREDEFINED_TEMPLATES

    def format_success(self, intent: Intent, result: Dict[str, Any]) -> str:
        """
        Format a success response based on the intent and result.

        Args:
            intent (Intent): The intent that was executed
            result (Dict[str, Any]): The result from the MCP tool

        Returns:
            str: Formatted success response
        """
        template_key = f"{intent.type.value.lower()}_success"

        if template_key in self.templates:
            template = self.templates[template_key]

            # Prepare template parameters based on intent type and result
            params = self._prepare_success_params(intent, result)

            try:
                return template.format(**params)
            except KeyError:
                # Fallback to a generic success message if template formatting fails
                return f"Action completed successfully: {intent.type.value.lower()}"
        else:
            # Generic fallback
            return f"Action completed: {intent.type.value.lower()}"

    def format_error(self, intent: Intent, error: Exception, error_type: str = "general") -> str:
        """
        Format an error response based on the intent and error.

        Args:
            intent (Intent): The intent that caused the error
            error (Exception): The error that occurred
            error_type (str): Type of error (task_not_found, invalid_parameter, etc.)

        Returns:
            str: Formatted error response
        """
        template_key = f"{error_type.replace(' ', '_')}_error"

        if template_key in self.templates:
            template = self.templates[template_key]

            # Prepare template parameters
            params = {
                "error_details": str(error),
                "action": intent.type.value.lower() if intent else "action"
            }

            try:
                return template.format(**params)
            except KeyError:
                # Fallback to a generic error message
                return f"I'm sorry, I encountered an error: {str(error)}"
        else:
            # Generic error fallback
            return f"I'm sorry, I couldn't complete that action due to an error: {str(error)}"

    def format_clarification_request(self, intent: Intent, user_input: str) -> str:
        """
        Format a clarification request response.

        Args:
            intent (Intent): The low-confidence intent
            user_input (str): The original user input

        Returns:
            str: Formatted clarification request
        """
        template = self.templates["clarification_request"]

        # Determine the appropriate action based on the likely intent
        if intent.type.value == "AMBIGUOUS":
            action = "handle"
        else:
            action = intent.type.value.lower().replace('_', ' ')

        params = {
            "aspect": "your request",
            "action": action
        }

        try:
            return template.format(**params)
        except KeyError:
            # Fallback to a generic clarification request
            return "Could you clarify your request? I'm not sure what you'd like me to do."

    def _prepare_success_params(self, intent: Intent, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare parameters for success template formatting.

        Args:
            intent (Intent): The executed intent
            result (Dict[str, Any]): The result from the MCP tool

        Returns:
            Dict[str, Any]: Parameters for template formatting
        """
        params = {}

        if intent.type.value == "ADD_TASK":
            params["task_content"] = intent.parameters.get("task_content", "unknown task")
        elif intent.type.value == "LIST_TASKS":
            # Format the task list for display
            tasks = result.get("tasks", [])
            if tasks:
                task_list = ", ".join([f"'{task.get('content', 'unnamed task')}' ({task.get('id')})"
                                      for task in tasks])
                params["task_list"] = task_list
            else:
                params["task_list"] = "No tasks found"
        elif intent.type.value in ["COMPLETE_TASK", "DELETE_TASK", "UPDATE_TASK"]:
            params["task_id"] = intent.parameters.get("task_id", "unknown")

        # Add any result-specific parameters
        params.update(result)

        return params

    def format_task_list(self, tasks: list) -> str:
        """
        Format a list of tasks for display to the user.

        Args:
            tasks (list): List of task dictionaries

        Returns:
            str: Formatted task list string
        """
        if not tasks:
            return "No tasks found."

        formatted_tasks = []
        for i, task in enumerate(tasks, 1):
            task_id = task.get('id', f'#{i}')
            content = task.get('content', 'Unnamed task')
            status = task.get('status', 'pending')
            formatted_tasks.append(f"{task_id}. {content} [{status}]")

        return "\n".join(formatted_tasks)

    def format_generic_response(self, message: str, action_type: ActionType = ActionType.SUCCESS) -> str:
        """
        Format a generic response with the specified action type.

        Args:
            message (str): The message to format
            action_type (ActionType): The type of action

        Returns:
            str: Formatted response
        """
        if action_type == ActionType.SUCCESS:
            return f"Okay, {message}"
        elif action_type == ActionType.ERROR:
            return f"I'm sorry, {message}"
        elif action_type == ActionType.CLARIFICATION:
            return f"To clarify: {message}"
        else:
            return message