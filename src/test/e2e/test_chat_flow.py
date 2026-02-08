"""
End-to-End Test for Chat Flow in Todo AI Chatbot System

This module tests the complete chat flow from user input to AI response with MCP tool integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlmodel import Session
from uuid import uuid4
from fastapi.testclient import TestClient

from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.task import Task
from src.app.main import app
from src.database.session import get_session_override
from src.services.conversation_service import ConversationService
from src.services.message_service import MessageService
from src.agents.todo_agent import TodoAgent
from src.mcp_server.server import mcp_server


class ChatFlowE2ETester:
    """
    End-to-End tester for the chat flow functionality.
    """

    def __init__(self, db_session: Session, test_client: TestClient = None):
        """
        Initialize the chat flow E2E tester.

        Args:
            db_session (Session): Database session for testing
            test_client (TestClient, optional): FastAPI test client
        """
        self.db_session = db_session
        self.test_client = test_client or TestClient(app)

    async def test_basic_chat_interaction(self):
        """
        Test basic chat interaction: user message -> AI response.
        """
        # Create a test user
        user = User(username="e2e_test_user", email="e2e@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Mock the AI agent response
        with patch('src.agents.todo_agent.TodoAgent.process_message') as mock_agent_process:
            mock_agent_process.return_value = {
                "response": "Sure, I can help you with that!",
                "tool_calls": []
            }

            # Send a simple message to the chat endpoint
            response = self.test_client.post(
                f"/api/{user.id}/chat",
                json={"message": "Hello, can you help me manage my tasks?"}
            )

            # Verify the response
            assert response.status_code == 200
            response_data = response.json()
            assert "response" in response_data
            assert "conversation_id" in response_data
            assert "tool_calls" in response_data

            # Verify the response content
            assert response_data["response"] == "Sure, I can help you with that!"

            print("✓ Basic chat interaction test passed")

    async def test_task_creation_via_chat(self):
        """
        Test creating a task via the chat interface using MCP tools.
        """
        # Create a test user
        user = User(username="task_e2e_user", email="task_e2e@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Mock the AI agent to trigger MCP tool call for adding a task
        with patch('src.agents.todo_agent.TodoAgent.process_message') as mock_agent_process:
            mock_agent_process.return_value = {
                "response": "I've added the task 'buy groceries' to your list.",
                "tool_calls": [{
                    "tool_name": "add_task",
                    "arguments": {
                        "user_id": str(user.id),
                        "content": "buy groceries",
                        "priority": "medium"
                    },
                    "result": {
                        "success": True,
                        "task_id": "task_123",
                        "message": "Task 'buy groceries' created successfully"
                    }
                }]
            }

            # Send a message that should trigger task creation
            response = self.test_client.post(
                f"/api/{user.id}/chat",
                json={"message": "Add a task to buy groceries"}
            )

            # Verify the response
            assert response.status_code == 200
            response_data = response.json()
            assert "response" in response_data
            assert "tool_calls" in response_data
            assert len(response_data["tool_calls"]) == 1
            assert response_data["tool_calls"][0]["tool_name"] == "add_task"
            assert response_data["tool_calls"][0]["result"]["success"] is True

            print("✓ Task creation via chat test passed")

    async def test_task_listing_via_chat(self):
        """
        Test listing tasks via the chat interface using MCP tools.
        """
        # Create a test user
        user = User(username="list_task_e2e_user", email="list_task_e2e@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Add some tasks to the database for this user
        task1 = Task(
            user_id=user.id,
            content="Buy groceries",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        task2 = Task(
            user_id=user.id,
            content="Call mom",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH
        )
        self.db_session.add(task1)
        self.db_session.add(task2)
        self.db_session.commit()

        # Mock the AI agent to trigger MCP tool call for listing tasks
        with patch('src.agents.todo_agent.TodoAgent.process_message') as mock_agent_process:
            mock_agent_process.return_value = {
                "response": "Here are your tasks: 1. Buy groceries (medium priority), 2. Call mom (high priority).",
                "tool_calls": [{
                    "tool_name": "list_tasks",
                    "arguments": {"user_id": str(user.id)},
                    "result": {
                        "success": True,
                        "tasks": [
                            {"id": "task_1", "content": "Buy groceries", "status": "pending", "priority": "medium"},
                            {"id": "task_2", "content": "Call mom", "status": "pending", "priority": "high"}
                        ],
                        "message": "Retrieved 2 tasks for user"
                    }
                }]
            }

            # Send a message that should trigger task listing
            response = self.test_client.post(
                f"/api/{user.id}/chat",
                json={"message": "What are my tasks?"}
            )

            # Verify the response
            assert response.status_code == 200
            response_data = response.json()
            assert "response" in response_data
            assert "tool_calls" in response_data
            assert len(response_data["tool_calls"]) == 1
            assert response_data["tool_calls"][0]["tool_name"] == "list_tasks"
            assert response_data["tool_calls"][0]["result"]["success"] is True
            assert len(response_data["tool_calls"][0]["result"]["tasks"]) == 2

            print("✓ Task listing via chat test passed")

    async def test_conversation_continuity(self):
        """
        Test that conversation history is properly reconstructed across requests.
        """
        # Create a test user
        user = User(username="continuity_e2e_user", email="continuity_e2e@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Create a conversation and add some messages
        conversation_service = ConversationService(self.db_session)
        conversation = conversation_service.create(
            ConversationCreate(user_id=user.id)
        )

        message_service = MessageService(self.db_session)

        # Add user message
        user_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="I need to create a task to buy groceries"
        )
        self.db_session.add(user_msg)

        # Add assistant response
        assistant_msg = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content="Sure, I can help with that. I've created the task 'buy groceries'."
        )
        self.db_session.add(assistant_msg)

        self.db_session.commit()

        # Mock the AI agent to verify it gets the conversation history
        with patch('src.agents.todo_agent.TodoAgent.process_message') as mock_agent_process:
            # Check that the agent receives the conversation history
            def capture_process_message(message, conversation_history=None):
                # Verify that conversation history is passed and contains previous messages
                assert conversation_history is not None
                assert len(conversation_history) >= 2  # At least the two messages we added

                # Return a mock response
                return {
                    "response": "I remember you wanted to manage tasks. What else can I help you with?",
                    "tool_calls": []
                }

            mock_agent_process.side_effect = capture_process_message

            # Send another message to the same conversation
            response = self.test_client.post(
                f"/api/{user.id}/chat",
                json={
                    "message": "What else can you do?",
                    "conversation_id": str(conversation.id)
                }
            )

            # Verify the response
            assert response.status_code == 200
            response_data = response.json()
            assert "response" in response_data
            assert response_data["conversation_id"] == str(conversation.id)

            print("✓ Conversation continuity test passed")

    async def test_user_isolation_in_chat(self):
        """
        Test that users cannot access each other's conversations or tasks.
        """
        # Create two test users
        user1 = User(username="iso_user_1", email="iso1@test.com")
        user2 = User(username="iso_user_2", email="iso2@test.com")
        self.db_session.add(user1)
        self.db_session.add(user2)
        self.db_session.commit()
        self.db_session.refresh(user1)
        self.db_session.refresh(user2)

        # Create conversations for each user
        conversation_service = ConversationService(self.db_session)

        conv1 = conversation_service.create(
            ConversationCreate(user_id=user1.id)
        )
        conv2 = conversation_service.create(
            ConversationCreate(user_id=user2.id)
        )

        # Mock the agent to return different responses based on user
        with patch('src.agents.todo_agent.TodoAgent.process_message') as mock_agent_process:
            mock_agent_process.return_value = {
                "response": "Your message has been received.",
                "tool_calls": []
            }

            # User 1 accesses their own conversation (should work)
            response1 = self.test_client.post(
                f"/api/{user1.id}/chat",
                json={
                    "message": "Hello, this is user 1",
                    "conversation_id": str(conv1.id)
                }
            )
            assert response1.status_code == 200

            # User 2 tries to access user 1's conversation (should fail or create new)
            response2 = self.test_client.post(
                f"/api/{user2.id}/chat",
                json={
                    "message": "Trying to access user 1's conversation",
                    "conversation_id": str(conv1.id)  # User 2 trying to access user 1's conversation
                }
            )

            # The system should either reject this or create a new conversation for user 2
            # In our implementation, it should create a new conversation
            assert response2.status_code == 200
            response_data = response2.json()
            # The conversation_id in response should be different from conv1.id if properly isolated
            assert response_data["conversation_id"] != str(conv1.id)

            print("✓ User isolation in chat test passed")

    async def run_all_tests(self):
        """
        Run all end-to-end chat flow tests.
        """
        print("Starting end-to-end chat flow tests...")

        await self.test_basic_chat_interaction()
        await self.test_task_creation_via_chat()
        await self.test_task_listing_via_chat()
        await self.test_conversation_continuity()
        await self.test_user_isolation_in_chat()

        print("✓ All end-to-end chat flow tests passed!")


# Pytest functions for E2E tests
@pytest.mark.asyncio
async def test_e2e_basic_chat_interaction():
    """
    Pytest function for basic chat interaction.
    """
    tester = ChatFlowE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_basic_chat_interaction()


@pytest.mark.asyncio
async def test_e2e_task_creation():
    """
    Pytest function for task creation via chat.
    """
    tester = ChatFlowE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_task_creation_via_chat()


@pytest.mark.asyncio
async def test_e2e_task_listing():
    """
    Pytest function for task listing via chat.
    """
    tester = ChatFlowE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_task_listing_via_chat()


@pytest.mark.asyncio
async def test_e2e_conversation_continuity():
    """
    Pytest function for conversation continuity.
    """
    tester = ChatFlowE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_conversation_continuity()


@pytest.mark.asyncio
async def test_e2e_user_isolation():
    """
    Pytest function for user isolation.
    """
    tester = ChatFlowE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_user_isolation_in_chat()


if __name__ == "__main__":
    # This would require a proper async test setup in a real implementation
    # For demonstration purposes only
    print("E2E tests would run here in a full implementation")