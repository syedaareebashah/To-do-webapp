"""
Todo Agent for the Todo AI Chatbot System.

This module implements the AI agent that processes user messages and interacts with MCP tools.
"""

import os
from typing import Dict, Any, List
from src.mcp_server.server import mcp_server


class TodoAgent:
    """
    AI agent for the Todo chatbot that processes user messages and uses MCP tools for task operations.
    """

    def __init__(self, mcp_server, user_id: str):
        """
        Initialize the Todo agent.

        Args:
            mcp_server: The MCP server instance for tool execution
            user_id (str): ID of the user this agent is serving
        """
        self.mcp_server = mcp_server
        self.user_id = user_id
        
        # Check for Gemini API key first
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Fallback to Cohere API key if Gemini key is not available
        if not self.gemini_api_key:
            self.cohere_api_key = os.getenv("COHERE_API_KEY")
        else:
            self.cohere_api_key = None
            
        # Fallback to OpenAI API key if neither Gemini nor Cohere keys are available
        if not self.gemini_api_key and not self.cohere_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        else:
            self.openai_api_key = None

        # Initialize Gemini client if API key is available
        self.gemini_client = None
        if self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_client = genai.GenerativeModel(
                    model_name="gemini-pro",
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 2048,
                    },
                    # Define the tools that Gemini can use
                    tools=[
                        {
                            "name": "add_task",
                            "description": "Add a new task to the user's task list",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "The ID of the user"},
                                    "content": {"type": "string", "description": "The content of the task to add"}
                                },
                                "required": ["user_id", "content"]
                            }
                        },
                        {
                            "name": "list_tasks",
                            "description": "List the user's tasks",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "The ID of the user"},
                                    "filter": {"type": "string", "description": "Filter for tasks (e.g., 'all', 'pending', 'completed')"}
                                },
                                "required": ["user_id", "filter"]
                            }
                        },
                        {
                            "name": "complete_task",
                            "description": "Mark a task as completed",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "The ID of the user"},
                                    "task_id": {"type": "string", "description": "The ID of the task to complete"}
                                },
                                "required": ["user_id", "task_id"]
                            }
                        },
                        {
                            "name": "delete_task",
                            "description": "Delete a task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string", "description": "The ID of the user"},
                                    "task_id": {"type": "string", "description": "The ID of the task to delete"}
                                },
                                "required": ["user_id", "task_id"]
                            }
                        }
                    ]
                )
            except ImportError:
                print("Google Generative AI library not installed. Install with: pip install google-generativeai")
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")

        # Initialize Cohere client if API key is available and Gemini is not used
        self.cohere_client = None
        if not self.gemini_client and self.cohere_api_key and self.cohere_api_key.startswith("cohere_"):
            try:
                import cohere
                self.cohere_client = cohere.Client(api_key=self.cohere_api_key)
            except ImportError:
                print("Cohere library not installed. Install with: pip install cohere")
            except Exception as e:
                print(f"Error initializing Cohere client: {e}")

        # Initialize OpenAI client if API key is available and neither Gemini nor Cohere are used
        self.openai_client = None
        if not self.gemini_client and not self.cohere_client and self.openai_api_key and self.openai_api_key.startswith("sk-"):
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_api_key)
            except ImportError:
                print("OpenAI library not installed. Install with: pip install openai")
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")

    async def process_message(self, message: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        Args:
            message (str): The user's message
            conversation_history (List[Dict[str, str]]): History of the conversation (role/content pairs)

        Returns:
            Dict[str, Any]: Response data including agent response and any tool calls made
        """
        # Use Gemini if available, otherwise Cohere, otherwise OpenAI, otherwise fall back to keyword detection
        if self.gemini_client:
            return await self._process_with_gemini(message, conversation_history)
        elif self.cohere_client:
            return await self._process_with_cohere(message, conversation_history)
        elif self.openai_client:
            return await self._process_with_openai(message, conversation_history)
        else:
            # For this implementation, we'll simulate a simple response
            # In a real implementation, this would connect to an LLM service like OpenAI

            # Determine if the user message requires a tool call
            tool_calls = []

            # Simple keyword detection for demo purposes
            message_lower = message.lower()

            if any(word in message_lower for word in ["add", "create", "new", "remember"]):
                # This appears to be a request to add a task
                # Extract task content from the message
                import re

                # Remove common task creation words to extract content
                content = re.sub(r"^(add|create|make|remember|new|task to |need to |want to )", "", message_lower).strip()

                # Create a tool call to add_task
                tool_call = {
                    "name": "add_task",
                    "arguments": {
                        "user_id": self.user_id,
                        "content": content if content else message
                    }
                }
                tool_calls.append(tool_call)

                # Simulate response
                response = f"I'll add '{content if content else message}' to your tasks."

            elif any(word in message_lower for word in ["list", "show", "see", "what"]):
                # This appears to be a request to list tasks
                tool_call = {
                    "name": "list_tasks",
                    "arguments": {
                        "user_id": self.user_id,
                        "filter_type": "pending"  # Default to showing pending tasks
                    }
                }
                tool_calls.append(tool_call)

                # Simulate response
                response = "Let me get your pending tasks for you."

            elif any(word in message_lower for word in ["complete", "done", "finish"]):
                # This appears to be a request to complete a task
                # Extract task ID if mentioned in the message
                import re

                # Look for numbers in the message which might represent task IDs
                numbers = re.findall(r'\d+', message)
                task_id = numbers[0] if numbers else None

                if task_id:
                    tool_call = {
                        "name": "complete_task",
                        "arguments": {
                            "user_id": self.user_id,
                            "task_id": f"task_{task_id}"
                        }
                    }
                    tool_calls.append(tool_call)

                    # Simulate response
                    response = f"I'll mark task {task_id} as completed."
                else:
                    response = "Which task would you like to mark as completed?"

            elif any(word in message_lower for word in ["delete", "remove"]):
                # This appears to be a request to delete a task
                # Extract task ID if mentioned in the message
                import re

                # Look for numbers in the message which might represent task IDs
                numbers = re.findall(r'\d+', message)
                task_id = numbers[0] if numbers else None

                if task_id:
                    tool_call = {
                        "name": "delete_task",
                        "arguments": {
                            "user_id": self.user_id,
                            "task_id": f"task_{task_id}"
                        }
                    }
                    tool_calls.append(tool_call)

                    # Simulate response
                    response = f"I'll delete task {task_id} for you."
                else:
                    response = "Which task would you like to delete?"

            else:
                # For other messages, provide a simple response
                response = f"I understand you said: '{message}'. How can I help you with your tasks?"

            # Simulate processing time
            import asyncio
            await asyncio.sleep(0.1)  # Small delay to simulate processing

            # Execute any tool calls that were identified
            tool_results = []
            for tool_call in tool_calls:
                try:
                    # Execute the tool call via the MCP server
                    result = await self.mcp_server.execute_tool(
                        tool_call["name"],
                        tool_call["arguments"]
                    )

                    tool_results.append({
                        "tool_name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": result
                    })
                except Exception as e:
                    tool_results.append({
                        "tool_name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": {"error": str(e)}
                    })

            # Return the response and any tool call results
            return {
                "response": response,
                "tool_calls": tool_results
            }

    async def _process_with_openai(self, message: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process a message using OpenAI API.

        Args:
            message (str): The user's message
            conversation_history (List[Dict[str, str]]): History of the conversation (role/content pairs)

        Returns:
            Dict[str, Any]: Response data including agent response and any tool calls made
        """
        try:
            # Prepare the messages for OpenAI
            openai_messages = []
            
            # Add conversation history
            for msg in conversation_history:
                openai_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add the current user message
            openai_messages.append({
                "role": "user",
                "content": message
            })

            # Call OpenAI API with function calling capabilities
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can change this to gpt-4 if preferred
                messages=openai_messages,
                temperature=0.7,
                max_tokens=500,
                functions=[
                    {
                        "name": "add_task",
                        "description": "Add a new task to the user's task list",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "The ID of the user"},
                                "content": {"type": "string", "description": "The content of the task to add"}
                            },
                            "required": ["user_id", "content"]
                        }
                    },
                    {
                        "name": "list_tasks",
                        "description": "List the user's tasks",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "The ID of the user"},
                                "filter": {"type": "string", "description": "Filter for tasks (e.g., 'all', 'pending', 'completed')"}
                            },
                            "required": ["user_id", "filter"]
                        }
                    },
                    {
                        "name": "complete_task",
                        "description": "Mark a task as completed",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "The ID of the user"},
                                "task_id": {"type": "string", "description": "The ID of the task to complete"}
                            },
                            "required": ["user_id", "task_id"]
                        }
                    },
                    {
                        "name": "delete_task",
                        "description": "Delete a task",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "string", "description": "The ID of the user"},
                                "task_id": {"type": "string", "description": "The ID of the task to delete"}
                            },
                            "required": ["user_id", "task_id"]
                        }
                    }
                ],
                function_call="auto"  # Let the model decide when to call functions
            )

            # Process the response
            choice = response.choices[0]
            message_response = choice.message
            
            # Check if a function was called
            tool_calls = []
            if message_response.function_call:
                # Process the function call
                function_call = message_response.function_call
                tool_call = {
                    "name": function_call.name,
                    "arguments": eval(function_call.arguments)  # Note: In production, use json.loads safely
                }
                
                # Ensure user_id is set correctly
                tool_call["arguments"]["user_id"] = self.user_id
                
                tool_calls.append(tool_call)
                
                # Generate a response based on the function call
                if function_call.name == "add_task":
                    response_text = f"I'll add '{tool_call['arguments']['content']}' to your tasks."
                elif function_call.name == "list_tasks":
                    response_text = "Let me get your tasks for you."
                elif function_call.name == "complete_task":
                    response_text = f"I'll mark task {tool_call['arguments']['task_id']} as completed."
                elif function_call.name == "delete_task":
                    response_text = f"I'll delete task {tool_call['arguments']['task_id']} for you."
                else:
                    response_text = "I've processed your request."
            else:
                # No function was called, just return the model's response
                response_text = message_response.content or "I've processed your request."
            
            # Execute any tool calls that were identified
            tool_results = []
            for tool_call in tool_calls:
                try:
                    # Execute the tool call via the MCP server
                    result = await self.mcp_server.execute_tool(
                        tool_call["name"],
                        tool_call["arguments"]
                    )

                    tool_results.append({
                        "tool_name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": result
                    })
                except Exception as e:
                    tool_results.append({
                        "tool_name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": {"error": str(e)}
                    })

            # Return the response and any tool call results
            return {
                "response": response_text,
                "tool_calls": tool_results
            }
            
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            # Fall back to keyword detection if OpenAI fails
            return await self.process_message(message, conversation_history)

    async def _process_with_cohere(self, message: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process a message using Cohere API.

        Args:
            message (str): The user's message
            conversation_history (List[Dict[str, str]]): History of the conversation (role/content pairs)

        Returns:
            Dict[str, Any]: Response data including agent response and any tool calls made
        """
        try:
            # Create a more specific prompt that guides Cohere to respond in a structured way
            # We'll include examples of how to format responses for different task operations
            formatted_history = []
            for msg in conversation_history:
                role = msg["role"]
                content = msg["content"]
                formatted_history.append(f"{role.capitalize()}: {content}")
            
            # Create a structured prompt that guides the model
            structured_prompt = f"""
            Conversation History:
            {chr(10).join(formatted_history)}
            
            User Request: {message}
            
            Instructions: As a task management assistant, respond in one of these specific formats based on the user's request:
            
            1. For adding tasks: Respond with "TASK_ADD: [task content]"
            2. For listing tasks: Respond with "TASK_LIST: [filter if specified, otherwise 'all']"
            3. For completing tasks: Respond with "TASK_COMPLETE: [task ID or content]"
            4. For deleting tasks: Respond with "TASK_DELETE: [task ID or content]"
            5. For other queries: Provide a helpful natural language response
            
            Current user ID: {self.user_id}
            """
            
            # Call Cohere API with the structured prompt
            response = self.cohere_client.generate(
                prompt=structured_prompt,
                max_tokens=300,
                temperature=0.7,
                stop_sequences=["\nUser:", "\nAssistant:"]
            )

            # Process the response
            response_text = response.generations[0].text.strip()
            
            # Parse the structured response to identify tool calls
            tool_calls = []
            
            # Look for structured responses
            import re
            
            # Pattern for task addition
            add_match = re.search(r'TASK_ADD:\s*(.+)', response_text, re.IGNORECASE)
            if add_match:
                content = add_match.group(1).strip()
                tool_call = {
                    "name": "add_task",
                    "arguments": {
                        "user_id": self.user_id,
                        "content": content
                    }
                }
                tool_calls.append(tool_call)
            
            # Pattern for task listing
            list_match = re.search(r'TASK_LIST:\s*(.+)', response_text, re.IGNORECASE)
            if list_match:
                filter_param = list_match.group(1).strip()
                tool_call = {
                    "name": "list_tasks",
                    "arguments": {
                        "user_id": self.user_id,
                        "filter_type": filter_param if filter_param else "all"
                    }
                }
                tool_calls.append(tool_call)
            elif "TASK_LIST" in response_text.upper():
                # If TASK_LIST is mentioned but no filter specified
                tool_call = {
                    "name": "list_tasks",
                    "arguments": {
                        "user_id": self.user_id,
                        "filter_type": "all"
                    }
                }
                tool_calls.append(tool_call)
            
            # Pattern for task completion
            complete_match = re.search(r'TASK_COMPLETE:\s*(.+)', response_text, re.IGNORECASE)
            if complete_match:
                task_identifier = complete_match.group(1).strip()
                
                # Check if it's a numeric ID or text content
                if task_identifier.isdigit():
                    tool_call = {
                        "name": "complete_task",
                        "arguments": {
                            "user_id": self.user_id,
                            "task_id": f"task_{task_identifier}"
                        }
                    }
                else:
                    # If it's not a number, treat as content
                    tool_call = {
                        "name": "complete_task",
                        "arguments": {
                            "user_id": self.user_id,
                            "task_content": task_identifier
                        }
                    }
                tool_calls.append(tool_call)
            
            # Pattern for task deletion
            delete_match = re.search(r'TASK_DELETE:\s*(.+)', response_text, re.IGNORECASE)
            if delete_match:
                task_identifier = delete_match.group(1).strip()
                
                # Check if it's a numeric ID or text content
                if task_identifier.isdigit():
                    tool_call = {
                        "name": "delete_task",
                        "arguments": {
                            "user_id": self.user_id,
                            "task_id": f"task_{task_identifier}"
                        }
                    }
                else:
                    # If it's not a number, treat as content
                    tool_call = {
                        "name": "delete_task",
                        "arguments": {
                            "user_id": self.user_id,
                            "task_content": task_identifier
                        }
                    }
                tool_calls.append(tool_call)

            # Execute any tool calls that were identified
            tool_results = []
            for tool_call in tool_calls:
                try:
                    # Execute the tool call via the MCP server
                    result = await self.mcp_server.execute_tool(
                        tool_call["name"],
                        tool_call["arguments"]
                    )

                    tool_results.append({
                        "tool_name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": result
                    })
                except Exception as e:
                    tool_results.append({
                        "tool_name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": {"error": str(e)}
                    })

            # Return the response and any tool call results
            # If we have tool calls, we might want to modify the response text to reflect the action taken
            final_response = response_text
            if tool_calls:
                # If we have tool calls, we can modify the response to be more informative
                # For example, if we're completing a task, we can acknowledge it
                for tool_call in tool_calls:
                    if tool_call["name"] == "complete_task":
                        if "task_content" in tool_call["arguments"]:
                            final_response = f"I've marked the task '{tool_call['arguments']['task_content']}' as completed."
                        elif "task_id" in tool_call["arguments"]:
                            final_response = f"I've marked task {tool_call['arguments']['task_id']} as completed."
                    elif tool_call["name"] == "add_task":
                        final_response = f"I've added '{tool_call['arguments']['content']}' to your tasks."
                    elif tool_call["name"] == "delete_task":
                        if "task_content" in tool_call["arguments"]:
                            final_response = f"I've deleted the task '{tool_call['arguments']['task_content']}'."
                        elif "task_id" in tool_call["arguments"]:
                            final_response = f"I've deleted task {tool_call['arguments']['task_id']}."
                    elif tool_call["name"] == "list_tasks":
                        final_response = "I'm retrieving your tasks now."

            return {
                "response": final_response,
                "tool_calls": tool_results
            }

        except Exception as e:
            print(f"Error calling Cohere API: {e}")
            # Fall back to keyword detection if Cohere fails
            return await self.process_message(message, conversation_history)

    async def _process_with_gemini(self, message: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process a message using Gemini API with function calling.

        Args:
            message (str): The user's message
            conversation_history (List[Dict[str, str]]): History of the conversation (role/content pairs)

        Returns:
            Dict[str, Any]: Response data including agent response and any tool calls made
        """
        try:
            # Prepare the conversation history for Gemini
            gemini_history = []
            
            # Convert conversation history to Gemini format
            for msg in conversation_history:
                role = "model" if msg["role"] == "assistant" else "user"
                gemini_history.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            # Add the current user message
            gemini_history.append({
                "role": "user",
                "parts": [{"text": message}]
            })
            
            # Call Gemini API with function calling enabled
            response = await self.gemini_client.generate_content_async(
                contents=gemini_history,
                # Enable automatic function calling
                tool_config={'function_calling_config': {'mode': 'AUTO'}}
            )
            
            # Process the response
            response_text = ""
            tool_calls = []
            
            # Check if the response contains function calls
            if hasattr(response.candidates[0], 'content') and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text'):
                        response_text += part.text
                    elif hasattr(part, 'function_call'):
                        # Process function call
                        function_call = part.function_call
                        args_dict = {}
                        if function_call.args:
                            args_dict = {key: value for key, value in function_call.args.items()}
                        
                        # Ensure user_id is included
                        args_dict["user_id"] = self.user_id
                        
                        tool_call = {
                            "name": function_call.name,
                            "arguments": args_dict
                        }
                        tool_calls.append(tool_call)
            
            # If no function calls were made but the user seems to want to complete a task by name,
            # try to extract the task name and find it in the database
            if not tool_calls and any(word in message.lower() for word in ["complete", "done", "finish"]):
                import re
                
                # Look for patterns like "complete [task content]", "mark [task content] as done", etc.
                patterns = [
                    r"complete\s+(?:the\s+)?['\"](.+?)['\"]",
                    r"complete\s+(?:the\s+)?(.+?)(?:\s+task|\.|$)",
                    r"mark\s+(?:the\s+)?['\"](.+?)['\"]\s+as\s+(?:completed|done)",
                    r"finish\s+(?:the\s+)?['\"](.+?)['\"]",
                    r"done\s+with\s+(?:the\s+)?['\"](.+?)['\"]"
                ]
                
                task_content = None
                for pattern in patterns:
                    match = re.search(pattern, message, re.IGNORECASE)
                    if match:
                        task_content = match.group(1).strip()
                        break
                
                if task_content:
                    # Try to find the task by content
                    try:
                        # First, list all tasks for the user to find the matching one
                        list_result = await self.mcp_server.execute_tool(
                            "list_tasks",
                            {"user_id": self.user_id, "filter_type": "all"}
                        )
                        
                        if list_result.get("success") and "tasks" in list_result:
                            matching_task = None
                            for task in list_result["tasks"]:
                                if task_content.lower() in task["content"].lower():
                                    matching_task = task
                                    break
                            
                            if matching_task:
                                # Create a tool call to complete the found task
                                tool_call = {
                                    "name": "complete_task",
                                    "arguments": {
                                        "user_id": self.user_id,
                                        "task_id": matching_task["id"]
                                    }
                                }
                                tool_calls.append(tool_call)
                                response_text = f"I've marked the task '{matching_task['content']}' as completed."
                            else:
                                response_text = f"I couldn't find a task containing '{task_content}'. Here are your tasks:"
                        else:
                            response_text = f"I couldn't retrieve your tasks to find '{task_content}'."
                    except Exception as e:
                        response_text = f"Error finding task by name: {str(e)}"
            
            # Execute any tool calls that were identified
            tool_results = []
            for tool_call in tool_calls:
                try:
                    # Execute the tool call via the MCP server
                    result = await self.mcp_server.execute_tool(
                        tool_call["name"],
                        tool_call["arguments"]
                    )

                    tool_results.append({
                        "tool_name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": result
                    })
                except Exception as e:
                    tool_results.append({
                        "tool_name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": {"error": str(e)}
                    })

            # Return the response and any tool call results
            return {
                "response": response_text if response_text else "Action completed successfully.",
                "tool_calls": tool_results
            }

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            # Fall back to keyword detection if Gemini fails
            return await self.process_message(message, conversation_history)

    async def process_with_llm(self, message: str, conversation_history: List[Dict[str, str]], llm_client) -> Dict[str, Any]:
        """
        Process a message using an actual LLM with MCP tools available.

        Args:
            message (str): The user's message
            conversation_history (List[Dict[str, str]]): History of the conversation (role/content pairs)
            llm_client: The LLM client to use for processing

        Returns:
            Dict[str, Any]: Response data including agent response and any tool calls made
        """
        # This would be the implementation for using an actual LLM like OpenAI
        # For now, this is a placeholder that would connect to the LLM service
        pass