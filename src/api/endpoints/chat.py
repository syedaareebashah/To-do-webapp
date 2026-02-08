"""
Chat API endpoint for the Todo AI Chatbot System.

This module implements the stateless chat endpoint that reconstructs conversation
state from the database and integrates with the AI agent and MCP tools.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from uuid import UUID

from src.models.message import MessageCreate
from src.models.conversation import ConversationCreate
from src.services.conversation_service import ConversationService
from src.services.message_service import MessageService
from src.services.task_service import TaskService
from src.database.session import get_session
from src.agents.todo_agent import TodoAgent
from src.mcp_server.server import mcp_server
from src.api.dependencies import get_current_user


router = APIRouter()


@router.post("/api/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    message_data: MessageCreate,
    conversation_id: str = None,
    db=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Stateless chat endpoint that reconstructs conversation state from the database
    and processes the user's message with the AI agent and MCP tools.

    Args:
        user_id (str): ID of the user sending the message
        message_data (MessageCreate): The user's message content
        conversation_id (str, optional): ID of the conversation (creates new if not provided)
        db: Database session dependency
        current_user: Authenticated user dependency

    Returns:
        Dict: Response containing assistant's reply and any tool calls made
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Access forbidden: Cannot access another user's conversation")

    # Initialize services
    conversation_service = ConversationService(db)
    message_service = MessageService(db)
    task_service = TaskService(db)

    # Get or create conversation
    if conversation_id:
        # Verify that the conversation belongs to the user
        conversation = conversation_service.get_by_id_and_user(
            conversation_id=UUID(conversation_id),
            user_id=user_id
        )
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create a new conversation
        conversation_data = ConversationCreate(user_id=user_id)
        conversation = conversation_service.create(obj_in=conversation_data)
        conversation_id = str(conversation.id)

    # Store the user's message
    message_data.conversation_id = conversation.id
    user_message = message_service.create(obj_in=message_data)

    # Reconstruct the conversation history from the database
    # Get all messages in the conversation ordered by timestamp
    all_messages = message_service.get_messages_by_conversation(
        conversation_id=conversation.id,
        limit=50  # Get last 50 messages
    )

    # Format messages for the AI agent (role, content pairs)
    formatted_history = []
    for msg in all_messages:
        formatted_history.append({
            "role": msg.role,
            "content": msg.content
        })

    # Initialize the AI agent with MCP tools
    agent = TodoAgent(mcp_server=mcp_server, user_id=user_id)

    # Process the message with the agent
    try:
        response_data = await agent.process_message(
            message=message_data.content,
            conversation_history=formatted_history
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

    # Extract the agent's response and any tool calls
    agent_response = response_data.get("response", "")
    tool_calls = response_data.get("tool_calls", [])

    # Store the assistant's response in the database
    assistant_message_data = MessageCreate(
        role="assistant",
        content=agent_response,
        conversation_id=conversation.id
    )
    assistant_message = message_service.create(obj_in=assistant_message_data)

    # Process any tool calls that were made
    tool_call_results = []
    if tool_calls:
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("arguments", {})

            # Execute the tool call and store the result
            try:
                # Add user_id to the tool arguments to ensure proper user isolation
                tool_args["user_id"] = user_id

                result = await mcp_server.execute_tool(tool_name, tool_args)
                tool_call_results.append({
                    "tool_name": tool_name,
                    "arguments": tool_args,
                    "result": result
                })
            except Exception as e:
                tool_call_results.append({
                    "tool_name": tool_name,
                    "arguments": tool_args,
                    "result": {"error": str(e)}
                })

    # Return the response with conversation ID and tool call information
    return {
        "conversation_id": conversation_id,
        "response": agent_response,
        "tool_calls": tool_call_results,
        "message_id": str(assistant_message.id)
    }