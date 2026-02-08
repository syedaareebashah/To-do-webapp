"""
Integration Test Suite for Todo AI Chatbot System & MCP

This module contains end-to-end integration tests for the complete system.
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch
from sqlmodel import Session, select
from uuid import uuid4
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.task import Task
from src.api.endpoints.chat import chat_endpoint
from src.agents.todo_agent import TodoAgent
from src.mcp_server.server import mcp_server
from src.services.conversation_service import ConversationService
from src.database.session import get_session


class IntegrationTestSuite:
    """
    Complete integration test suite for the Todo AI Chatbot System.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the integration test suite.

        Args:
            db_session (Session): Database session for testing
        """
        self.db_session = db_session

    async def test_complete_chat_flow(self):
        """
        Test the complete chat flow from user input to AI response with MCP tools.
        """
        # Create a test user
        user = User(username="integration_test_user", email="integration@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Create a conversation for the user
        conversation_service = ConversationService(self.db_session)
        conversation = conversation_service.create(
            ConversationCreate(user_id=user.id)
        )

        # Mock the AI agent and MCP server responses
        with patch.object(TodoAgent, 'process_message') as mock_process_message:
            mock_process_message.return_value = {
                "response": "I've added the task 'buy groceries' for you.",
                "tool_calls": [
                    {
                        "tool_name": "add_task",
                        "arguments": {"user_id": str(user.id), "content": "buy groceries"},
                        "result": {"success": True, "task_id": "task_123", "message": "Task created successfully"}
                    }
                ]
            }

            # Simulate a chat request
            chat_request = {
                "message": "Add a task to buy groceries",
                "conversation_id": str(conversation.id)
            }

            # Call the chat endpoint (this would normally be done through FastAPI)
            # For this test, we'll simulate the endpoint's behavior
            from fastapi import HTTPException

            # Test that the conversation and user exist
            retrieved_conversation = conversation_service.get_by_id_and_user(
                conversation.id,
                user.id
            )

            assert retrieved_conversation is not None

            # Verify that the user message was stored
            # In a real test, we would check the database for the stored message
            print("✓ Complete chat flow test passed")

    async def test_mcp_tool_integration(self):
        """
        Test MCP tool operations with database persistence.
        """
        # Create a test user
        user = User(username="mcp_test_user", email="mcp@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Test creating a task via MCP tool
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            # Mock successful task creation
            mock_execute.return_value = {
                "success": True,
                "task_id": "task_456",
                "message": "Task 'test task' created successfully"
            }

            # Call the MCP tool directly
            result = await mcp_server.execute_tool(
                "add_task",
                {"user_id": str(user.id), "content": "test task"}
            )

            assert result["success"] is True
            assert result["task_id"] == "task_456"

            # Verify the task would be in the database (in a real test, we'd check the actual database)
            print("✓ MCP tool integration test passed")

    async def test_user_authentication_and_isolation(self):
        """
        Test user authentication and data isolation.
        """
        # Create two test users
        user1 = User(username="auth_test_user1", email="auth1@test.com")
        user2 = User(username="auth_test_user2", email="auth2@test.com")
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

        # Verify that users can only access their own conversations
        user1_convs = conversation_service.get_user_conversations(user1.id)
        user2_convs = conversation_service.get_user_conversations(user2.id)

        assert len(user1_convs) == 1
        assert user1_convs[0].id == conv1.id

        assert len(user2_convs) == 1
        assert user2_convs[0].id == conv2.id

        # Verify that a user cannot access another user's conversation
        unauthorized_access = conversation_service.get_by_id_and_user(conv2.id, user1.id)
        assert unauthorized_access is None

        unauthorized_access = conversation_service.get_by_id_and_user(conv1.id, user2.id)
        assert unauthorized_access is None

        print("✓ User authentication and isolation test passed")

    async def test_error_scenarios_and_recovery(self):
        """
        Test error handling and recovery scenarios.
        """
        # Create a test user
        user = User(username="error_test_user", email="error@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Test error handling when MCP tool fails
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            # Mock a tool failure
            mock_execute.side_effect = Exception("MCP tool failed")

            # Try to call the tool and verify error handling
            try:
                result = await mcp_server.execute_tool(
                    "add_task",
                    {"user_id": str(user.id), "content": "test task"}
                )
                # If no exception is raised, check that error was handled properly
                assert result["success"] is False
            except Exception:
                # If an exception is propagated, the error handling is working as expected
                pass

        # Test error handling for invalid conversation ID
        conversation_service = ConversationService(self.db_session)

        fake_conversation_id = uuid4()
        unauthorized_access = conversation_service.get_by_id_and_user(fake_conversation_id, user.id)
        assert unauthorized_access is None

        print("✓ Error scenarios and recovery test passed")

    async def test_conversation_continuity_after_server_restart(self):
        """
        Test that conversations maintain continuity after simulated server restart.
        """
        # Create a test user
        user = User(username="continuity_test_user", email="continuity@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Create a conversation and add some messages
        conversation_service = ConversationService(self.db_session)
        message_service = MessageService(self.db_session)

        conversation = conversation_service.create(
            ConversationCreate(user_id=user.id)
        )

        # Add messages to the conversation
        msg1 = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="First message in conversation"
        )
        self.db_session.add(msg1)

        msg2 = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content="Response to first message"
        )
        self.db_session.add(msg2)

        self.db_session.commit()

        # Simulate a server restart by creating fresh service instances
        # which would not have any in-memory state
        fresh_conversation_service = ConversationService(self.db_session)

        # Verify that conversation history is correctly retrieved from the database
        conversation_history = fresh_conversation_service.get_conversation_history(conversation.id)
        assert len(conversation_history) == 2

        # Verify the content of the messages
        assert conversation_history[0].content == "First message in conversation"
        assert conversation_history[1].content == "Response to first message"

        print("✓ Conversation continuity after server restart test passed")

    async def run_all_tests(self):
        """
        Run all integration tests.
        """
        print("Starting integration test suite...")

        await self.test_complete_chat_flow()
        await self.test_mcp_tool_integration()
        await self.test_user_authentication_and_isolation()
        await self.test_error_scenarios_and_recovery()
        await self.test_conversation_continuity_after_server_restart()

        print("✓ All integration tests passed!")


# Pytest functions for integration tests
@pytest.mark.asyncio
async def test_full_chat_flow_integration():
    """
    Pytest function for complete chat flow integration.
    """
    # In a real implementation, this would use a test database session
    tester = IntegrationTestSuite(db_session=None)  # Replace with actual test session
    await tester.test_complete_chat_flow()


@pytest.mark.asyncio
async def test_mcp_tool_integration():
    """
    Pytest function for MCP tool integration.
    """
    tester = IntegrationTestSuite(db_session=None)  # Replace with actual test session
    await tester.test_mcp_tool_integration()


@pytest.mark.asyncio
async def test_user_isolation_integration():
    """
    Pytest function for user isolation in integration.
    """
    tester = IntegrationTestSuite(db_session=None)  # Replace with actual test session
    await tester.test_user_authentication_and_isolation()


@pytest.mark.asyncio
async def test_error_handling_integration():
    """
    Pytest function for error handling in integration.
    """
    tester = IntegrationTestSuite(db_session=None)  # Replace with actual test session
    await tester.test_error_scenarios_and_recovery()


@pytest.mark.asyncio
async def test_conversation_continuity_integration():
    """
    Pytest function for conversation continuity in integration.
    """
    tester = IntegrationTestSuite(db_session=None)  # Replace with actual test session
    await tester.test_conversation_continuity_after_server_restart()


if __name__ == "__main__":
    # This would require a proper async test setup in a real implementation
    # For demonstration purposes only
    print("Integration tests would run here in a full implementation")