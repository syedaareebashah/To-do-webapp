"""
Basic Response Formatter for Todo AI Chatbot Agent

This module provides basic formatting for agent responses.
"""

from typing import Dict, Any
from ..models.intent import Intent
from ..generators.success_message_generator import SuccessMessageGenerator


class BasicResponseFormatter:
    """
    Provides basic formatting for agent responses.
    """

    def __init__(self):
        """
        Initialize the basic response formatter.
        """
        self.success_generator = SuccessMessageGenerator()

    def format_response(self, intent: Intent, result: Dict[str, Any]) -> str:
        """
        Format a response based on the intent and result.

        Args:
            intent (Intent): The intent that was executed
            result (Dict[str, Any]): The result from the tool execution

        Returns:
            str: The formatted response
        """
        if result.get('success', False):
            return self.format_success_response(intent, result)
        else:
            return self.format_error_response(intent, result)

    def format_success_response(self, intent: Intent, result: Dict[str, Any]) -> str:
        """
        Format a success response based on the intent and result.

        Args:
            intent (Intent): The intent that was executed
            result (Dict[str, Any]): The result from the tool execution

        Returns:
            str: The formatted success response
        """
        return self.success_generator.generate_success_message(intent, result)

    def format_error_response(self, intent: Intent, result: Dict[str, Any]) -> str:
        """
        Format an error response based on the intent and result.

        Args:
            intent (Intent): The intent that was attempted
            result (Dict[str, Any]): The result from the tool execution

        Returns:
            str: The formatted error response
        """
        error_msg = result.get('message', 'An error occurred')
        error_code = result.get('error', 'GENERAL_ERROR')

        # Customize error message based on the error code
        if error_code == 'TASK_NOT_FOUND':
            return f"I couldn't find that task. Would you like to see your current tasks?"
        elif error_code == 'MISSING_PARAMETER':
            return f"I need more information to complete this action. Please provide the required details."
        elif error_code == 'INVALID_PARAMETER':
            return f"I had trouble understanding your request. Could you please rephrase it?"
        else:
            return f"I'm sorry, I couldn't complete that action. {error_msg}"

    def format_welcome_message(self) -> str:
        """
        Format a welcome message for new conversations.

        Returns:
            str: The welcome message
        """
        return "Hello! I'm your Todo assistant. You can ask me to add, list, complete, update, or delete tasks. How can I help you today?"

    def format_goodbye_message(self) -> str:
        """
        Format a goodbye message for ending conversations.

        Returns:
            str: The goodbye message
        """
        return "Goodbye! Feel free to come back anytime you need help with your tasks."

    def format_help_message(self) -> str:
        """
        Format a help message explaining available commands.

        Returns:
            str: The help message
        """
        help_text = (
            "I can help you manage your tasks. Here are some things you can ask me:\n"
            "- Add a task: 'Add a task to buy groceries' or 'Create a task to call mom'\n"
            "- List tasks: 'Show my tasks' or 'What do I have to do?'\n"
            "- Complete a task: 'Complete task 1' or 'Mark task 2 as done'\n"
            "- Delete a task: 'Delete task 3' or 'Remove task 4'\n"
            "- Update a task: 'Update task 1 to new content' or 'Change priority of task 2 to high'"
        )
        return help_text

    def format_simple_confirmation(self, action: str) -> str:
        """
        Format a simple confirmation message.

        Args:
            action (str): The action that was performed

        Returns:
            str: The confirmation message
        """
        return f"Okay, I've {action}."

    def format_task_summary(self, tasks: list) -> str:
        """
        Format a summary of tasks.

        Args:
            tasks (list): List of task dictionaries

        Returns:
            str: The formatted task summary
        """
        if not tasks:
            return "You don't have any tasks."

        total = len(tasks)
        completed = len([task for task in tasks if task.get('status') == 'completed'])
        pending = total - completed

        summary = f"You have {total} tasks in total: {pending} pending and {completed} completed."

        if pending > 0:
            # Show first few pending tasks
            pending_tasks = [t for t in tasks if t.get('status') == 'pending'][:3]
            if pending_tasks:
                task_list = ", ".join([f"'{t.get('content', 'unnamed')}'" for t in pending_tasks])
                summary += f"\nPending: {task_list}"

                if len(pending_tasks) < pending:
                    summary += f"\n... and {pending - len(pending_tasks)} more pending tasks."

        return summary