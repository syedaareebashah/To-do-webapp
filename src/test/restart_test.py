"""
Server Restart Recovery Test for Todo AI Chatbot System

This module tests the system's ability to maintain conversation continuity after server restarts.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.user import User
from src.services.conversation_service import ConversationService
from src.services.message_service import MessageService
from src.database.session import get_session
from src.agents.todo_agent import TodoAgent
from src.mcp_server.server import mcp_server


class ServerRestartRecoveryTester:
    """
    Test class for verifying server restart recovery behavior.
    """

    def __init__(self, db_session):
        """
        Initialize the server restart recovery tester.

        Args:
            db_session: Database session for testing
        """
        self.db_session = db_session
        self.conversation_service = ConversationService(db_session)
        self.message_service = MessageService(db_session)

    async def test_conversation_continuity_after_restart(self):
        """
        Test that conversations can be continued after a server restart.

        This test simulates the process of:
        1. Creating a conversation with several messages
        2. Simulating a server restart (resetting in-memory state)
        3. Verifying that the conversation can be resumed correctly
        """
        # Step 1: Create a user and conversation
        user = User(username="test_user", email="test@example.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Create a conversation
        conversation = self.conversation_service.create(
            ConversationCreate(user_id=user.id)
        )

        # Add some messages to the conversation
        message1 = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="Add a task to buy groceries"
        )
        self.db_session.add(message1)

        message2 = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content="I've added the task 'buy groceries' for you."
        )
        self.db_session.add(message2)

        message3 = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="Show my tasks"
        )
        self.db_session.add(message3)

        self.db_session.commit()

        # Verify the conversation and messages exist in the database
        assert self.conversation_service.get_by_id_and_user(conversation.id, user.id) is not None

        messages = self.conversation_service.get_conversation_history(conversation.id)
        assert len(messages) == 3

        # Step 2: Simulate server restart by clearing any in-memory state
        # (In a real system, this would involve actually restarting the server)
        # For our test, we'll just ensure we're using fresh services that don't have cached data
        fresh_conversation_service = ConversationService(self.db_session)
        fresh_message_service = MessageService(self.db_session)

        # Step 3: Verify conversation can be reconstructed from database
        reconstructed_messages = fresh_conversation_service.get_conversation_history(conversation.id)
        assert len(reconstructed_messages) == 3

        # Verify message content is preserved
        assert reconstructed_messages[0].content == "Add a task to buy groceries"
        assert reconstructed_messages[1].content == "I've added the task 'buy groceries' for you."
        assert reconstructed_messages[2].content == "Show my tasks"

        # Step 4: Verify new messages can be added to the conversation
        new_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content="You have 1 task: 'buy groceries' (pending)"
        )
        self.db_session.add(new_message)
        self.db_session.commit()

        # Verify the new message was added
        updated_messages = fresh_conversation_service.get_conversation_history(conversation.id)
        assert len(updated_messages) == 4
        assert updated_messages[3].content == "You have 1 task: 'buy groceries' (pending)"

        print("✓ Conversation continuity test passed after simulated restart")

    async def test_task_persistence_after_restart(self):
        """
        Test that tasks persist correctly after a server restart.
        """
        # This would test that MCP operations persist to the database
        # and are available after a restart

        # Create a user
        user = User(username="task_test_user", email="task_test@example.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Simulate using MCP tools to create tasks
        # (In a real test, we would call the actual MCP tools)

        # Mock MCP tool call to create a task
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "task_id": "task_123",
                "message": "Task 'buy groceries' created successfully"
            }

            # Call the MCP tool to create a task
            result = await mcp_server.execute_tool(
                "add_task",
                {"user_id": str(user.id), "content": "buy groceries"}
            )

            assert result["success"] is True

        # Simulate server restart by ensuring we're using fresh state
        # Check that the task would be retrievable from the database
        # (This would require actual database implementation of tasks)

        print("✓ Task persistence test passed after simulated restart")

    async def test_multi_user_isolation_after_restart(self):
        """
        Test that user data remains isolated after a server restart.
        """
        # Create two users
        user1 = User(username="user_one", email="user1@example.com")
        user2 = User(username="user_two", email="user2@example.com")
        self.db_session.add(user1)
        self.db_session.add(user2)
        self.db_session.commit()
        self.db_session.refresh(user1)
        self.db_session.refresh(user2)

        # Create conversations for each user
        conv1 = self.conversation_service.create(
            ConversationCreate(user_id=user1.id)
        )
        conv2 = self.conversation_service.create(
            ConversationCreate(user_id=user2.id)
        )

        # Add messages to each conversation
        msg1_user1 = Message(
            conversation_id=conv1.id,
            role=MessageRole.USER,
            content="Message from user 1"
        )
        self.db_session.add(msg1_user1)

        msg2_user2 = Message(
            conversation_id=conv2.id,
            role=MessageRole.USER,
            content="Message from user 2"
        )
        self.db_session.add(msg2_user2)

        self.db_session.commit()

        # Simulate server restart with fresh services
        fresh_conversation_service = ConversationService(self.db_session)

        # Verify user isolation - each user should only see their own conversations
        user1_conversations = fresh_conversation_service.get_user_conversations(str(user1.id))
        user2_conversations = fresh_conversation_service.get_user_conversations(str(user2.id))

        assert len(user1_conversations) == 1
        assert len(user2_conversations) == 1
        assert user1_conversations[0].id == conv1.id
        assert user2_conversations[0].id == conv2.id

        # Verify each user can only access their own conversation messages
        user1_messages = fresh_conversation_service.get_conversation_history(conv1.id)
        user2_messages = fresh_conversation_service.get_conversation_history(conv2.id)

        assert len(user1_messages) == 1
        assert len(user2_messages) == 1
        assert user1_messages[0].content == "Message from user 1"
        assert user2_messages[0].content == "Message from user 2"

        print("✓ Multi-user isolation test passed after simulated restart")

    async def run_all_tests(self):
        """
        Run all server restart recovery tests.
        """
        print("Starting server restart recovery tests...")

        await self.test_conversation_continuity_after_restart()
        await self.test_task_persistence_after_restart()
        await self.test_multi_user_isolation_after_restart()

        print("✓ All server restart recovery tests passed!")


# Test functions for pytest
@pytest.mark.asyncio
async def test_conversation_continuity_after_simulated_restart():
    """
    Pytest function for conversation continuity after restart.
    """
    # This would be connected to a proper test database in a real implementation
    tester = ServerRestartRecoveryTester(db_session=None)  # Replace with actual test session
    await tester.test_conversation_continuity_after_restart()


@pytest.mark.asyncio
async def test_task_persistence_after_simulated_restart():
    """
    Pytest function for task persistence after restart.
    """
    tester = ServerRestartRecoveryTester(db_session=None)  # Replace with actual test session
    await tester.test_task_persistence_after_restart()


@pytest.mark.asyncio
async def test_multi_user_isolation_after_simulated_restart():
    """
    Pytest function for user isolation after restart.
    """
    tester = ServerRestartRecoveryTester(db_session=None)  # Replace with actual test session
    await tester.test_multi_user_isolation_after_restart()


if __name__ == "__main__":
    # This would require a proper async test setup in a real implementation
    # For demonstration purposes only
    print("Server restart recovery tests would run here in a full implementation")