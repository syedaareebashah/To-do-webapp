
"""
Todo AI Chatbot Agent - Main Agent Class

This module contains the main TodoChatbotAgent class that processes natural language
requests and maps them to MCP tools for task management.
"""

import os
from typing import Dict, Any, Optional
from src.models.intent import Intent
from src.models.conversation_context import ConversationContext
from src.interfaces.mcp_tool_interface import MCPTOOLInterface
from src.processors.nlp_processor import NLPProcessor
from src.classifiers.intent_classifier import IntentClassifier
from src.mappers.tool_mapper import ToolMapper
from src.formatters.response_formatter import ResponseFormatter
from src.coordinators.tool_chain_coordinator import ToolChainCoordinator


class TodoChatbotAgent:
    """
    Main agent class that processes user input and maps it to MCP tools.
    """

    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize the Todo Chatbot Agent.

        Args:
            confidence_threshold (float): Threshold for intent classification confidence
        """
        self.confidence_threshold = confidence_threshold

        # Initialize components
        self.nlp_processor = NLPProcessor()
        self.intent_classifier = IntentClassifier(threshold=confidence_threshold)
        self.tool_mapper = ToolMapper()
        self.response_formatter = ResponseFormatter()
        self.tool_chain_coordinator = ToolChainCoordinator()
        self.mcp_interface = MCPTOOLInterface()

    def process_input(self, user_input: str, conversation_context: Optional[ConversationContext] = None) -> str:
        """
        Process user input and return a response.

        Args:
            user_input (str): The user's natural language input
            conversation_context (Optional[ConversationContext]): Context from the conversation

        Returns:
            str: The agent's response to the user
        """
        if conversation_context is None:
            conversation_context = ConversationContext()

        # Update conversation context with user input
        conversation_context.add_user_turn(user_input)

        # Process the input to identify intent
        intent = self._identify_intent(user_input, conversation_context)

        # Handle the intent based on confidence level
        if intent.confidence >= self.confidence_threshold:
            # Execute the appropriate tool
            response = self._execute_tool(intent, conversation_context)
        else:
            # Request clarification
            response = self._request_clarification(intent, user_input)

        # Update conversation context with agent response
        conversation_context.add_agent_turn(response)

        return response

    def _execute_tool(self, intent: Intent, conversation_context: ConversationContext) -> str:
        """
        Execute the appropriate tool based on the identified intent.

        Args:
            intent (Intent): The identified intent
            conversation_context (ConversationContext): Context from the conversation

        Returns:
            str: The formatted response to the user
        """
        # Map the intent to an MCP tool
        try:
            tool_mapping = self.tool_mapper.map_intent_to_tool(intent)
        except ValueError as e:
            # Handle mapping errors
            error_response = f"Error mapping intent to tool: {str(e)}"
            return self.response_formatter.format_simple_confirmation(error_response)

        # Execute the tool
        if tool_mapping.requires_tool_chaining():
            result = self.tool_chain_coordinator.execute_chain(tool_mapping, conversation_context)
        else:
            # Prepare parameters for the tool
            tool_params = tool_mapping.parameters

            # Execute the appropriate tool based on the tool name
            if tool_mapping.mcp_tool == "add_task":
                from src.tools.add_task_wrapper import AddTaskWrapper
                wrapper = AddTaskWrapper(self.mcp_interface)
                result = wrapper.execute_with_params(tool_params)
            elif tool_mapping.mcp_tool == "list_tasks":
                from src.tools.list_tasks_wrapper import ListTasksWrapper
                wrapper = ListTasksWrapper(self.mcp_interface)
                result = wrapper.execute_with_params(tool_params)
            elif tool_mapping.mcp_tool == "complete_task":
                from src.tools.complete_task_wrapper import CompleteTaskWrapper
                wrapper = CompleteTaskWrapper(self.mcp_interface)
                result = wrapper.execute_with_params(tool_params)
            elif tool_mapping.mcp_tool == "delete_task":
                from src.tools.delete_task_wrapper import DeleteTaskWrapper
                wrapper = DeleteTaskWrapper(self.mcp_interface)
                result = wrapper.execute_with_params(tool_params)
            elif tool_mapping.mcp_tool == "update_task":
                from src.tools.update_task_wrapper import UpdateTaskWrapper
                wrapper = UpdateTaskWrapper(self.mcp_interface)
                result = wrapper.execute_with_params(tool_params)
            else:
                # Unknown tool
                result = {
                    "success": False,
                    "error": "UNKNOWN_TOOL",
                    "message": f"Unknown tool: {tool_mapping.mcp_tool}"
                }

        # Format the response
        if result.get('success', False):
            response = self.response_formatter.format_success_response(intent, result)
        else:
            response = self.response_formatter.format_error_response(intent, result)

        return response

    def _identify_intent(self, user_input: str, conversation_context: ConversationContext) -> Intent:
        """
        Identify the user's intent from their input.

        Args:
            user_input (str): The user's natural language input
            conversation_context (ConversationContext): Context from the conversation

        Returns:
            Intent: The identified intent with confidence score
        """
        # Process the input with NLP processor
        processed_input = self.nlp_processor.process(user_input)

        # Classify the intent
        intent = self.intent_classifier.classify(processed_input, conversation_context)

        return intent

    def _execute_tool(self, intent: Intent, conversation_context: ConversationContext) -> str:
        """
        Execute the appropriate tool based on the identified intent.

        Args:
            intent (Intent): The identified intent
            conversation_context (ConversationContext): Context from the conversation

        Returns:
            str: The formatted response to the user
        """
        # Map the intent to an MCP tool
        tool_mapping = self.tool_mapper.map_intent_to_tool(intent)

        # Execute the tool
        if tool_mapping.requires_tool_chaining():
            result = self.tool_chain_coordinator.execute_chain(tool_mapping, conversation_context)
        else:
            result = self.mcp_interface.execute_tool(tool_mapping.tool_name, tool_mapping.parameters)

        # Format the response
        response = self.response_formatter.format_success(intent, result)

        return response

    def _request_clarification(self, intent: Intent, user_input: str) -> str:
        """
        Request clarification from the user when intent confidence is low.

        Args:
            intent (Intent): The identified intent with low confidence
            user_input (str): The original user input

        Returns:
            str: The clarification request to the user
        """
        # Format a clarification request
        response = self.response_formatter.format_clarification_request(intent, user_input)

        return response