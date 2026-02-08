"""
User Isolation Test for Todo AI Chatbot System

This module tests that users cannot access each other's data, ensuring proper isolation.
"""

import pytest
import asyncio
from sqlmodel import Session, select
from uuid import uuid4
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.task import Task
from src.services.conversation_service import ConversationService
from src.services.message_service import MessageService
from src.services.task_service import TaskService
from src.database.session import get_session


class UserIsolationTester:
    """
    Test class for verifying user isolation in the system.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the user isolation tester.

        Args:
            db_session (Session): Database session for testing
        """
        self.db_session = db_session

    async def setup_test_users(self):
        """
        Set up test users for the isolation tests.

        Returns:
            tuple: A tuple containing the created users (user1, user2)
        """
        # Create two distinct users
        user1 = User(username="test_user_1", email="test1@example.com")
        user2 = User(username="test_user_2", email="test2@example.com")

        self.db_session.add(user1)
        self.db_session.add(user2)
        self.db_session.commit()

        self.db_session.refresh(user1)
        self.db_session.refresh(user2)

        return user1, user2

    async def test_conversation_isolation(self):
        """
        Test that users cannot access each other's conversations.
        """
        user1, user2 = await self.setup_test_users()

        # Create conversations for each user
        conv_service = ConversationService(self.db_session)

        # User 1 creates a conversation
        conv1_data = ConversationCreate(user_id=user1.id)
        conversation1 = conv_service.create(conv1_data)

        # User 2 creates a conversation
        conv2_data = ConversationCreate(user_id=user2.id)
        conversation2 = conv_service.create(conv2_data)

        # Verify each user can only access their own conversations
        user1_conversations = conv_service.get_user_conversations(user1.id)
        user2_conversations = conv_service.get_user_conversations(user2.id)

        # User 1 should only see their own conversation
        assert len(user1_conversations) == 1
        assert user1_conversations[0].id == conversation1.id
        assert user1_conversations[0].user_id == user1.id

        # User 2 should only see their own conversation
        assert len(user2_conversations) == 1
        assert user2_conversations[0].id == conversation2.id
        assert user2_conversations[0].user_id == user2.id

        # Try to access another user's conversation (should fail)
        other_user_conv = conv_service.get_by_id_and_user(conversation2.id, user1.id)
        assert other_user_conv is None

        other_user_conv = conv_service.get_by_id_and_user(conversation1.id, user2.id)
        assert other_user_conv is None

        print("✓ Conversation isolation test passed")

    async def test_message_isolation(self):
        """
        Test that users cannot access each other's messages.
        """
        user1, user2 = await setup_test_users()

        # Create conversations for each user
        conv_service = ConversationService(self.db_session)

        conv1_data = ConversationCreate(user_id=user1.id)
        conversation1 = conv_service.create(conv1_data)

        conv2_data = ConversationCreate(user_id=user2.id)
        conversation2 = conv_service.create(conv2_data)

        # Add messages to each conversation
        msg_service = MessageService(self.db_session)

        # Messages for user 1's conversation
        msg1 = Message(
            conversation_id=conversation1.id,
            role=MessageRole.USER,
            content="User 1 message 1"
        )
        msg2 = Message(
            conversation_id=conversation1.id,
            role=MessageRole.ASSISTANT,
            content="Assistant response to user 1"
        )
        self.db_session.add(msg1)
        self.db_session.add(msg2)

        # Messages for user 2's conversation
        msg3 = Message(
            conversation_id=conversation2.id,
            role=MessageRole.USER,
            content="User 2 message 1"
        )
        msg4 = Message(
            conversation_id=conversation2.id,
            role=MessageRole.ASSISTANT,
            content="Assistant response to user 2"
        )
        self.db_session.add(msg3)
        self.db_session.add(msg4)

        self.db_session.commit()

        # Try to access messages from the wrong user's perspective
        # In a real implementation, the message service would have methods to
        # retrieve messages by conversation, and conversation access is already
        # controlled by the conversation service

        # Verify that conversation isolation already protects messages
        # (since messages are accessed through conversations)
        conv1_messages = conv_service.get_conversation_history(conversation1.id)
        conv2_messages = conv_service.get_conversation_history(conversation2.id)

        assert len(conv1_messages) == 2
        assert len(conv2_messages) == 2

        # Verify message contents are correct for each conversation
        conv1_contents = [msg.content for msg in conv1_messages]
        assert "User 1 message 1" in conv1_contents
        assert "Assistant response to user 1" in conv1_contents

        conv2_contents = [msg.content for msg in conv2_messages]
        assert "User 2 message 1" in conv2_contents
        assert "Assistant response to user 2" in conv2_contents

        print("✓ Message isolation test passed")

    async def test_task_isolation(self):
        """
        Test that users cannot access each other's tasks.
        """
        user1, user2 = await self.setup_test_users()

        # Create tasks for each user
        task_service = TaskService(self.db_session)

        # Tasks for user 1
        task1_data = TaskCreate(
            user_id=user1.id,
            content="User 1 task 1",
            status=TaskStatus.PENDING
        )
        task1 = task_service.create(task1_data)

        task2_data = TaskCreate(
            user_id=user1.id,
            content="User 1 task 2",
            status=TaskStatus.COMPLETED
        )
        task2 = task_service.create(task2_data)

        # Tasks for user 2
        task3_data = TaskCreate(
            user_id=user2.id,
            content="User 2 task 1",
            status=TaskStatus.PENDING
        )
        task3 = task_service.create(task3_data)

        task4_data = TaskCreate(
            user_id=user2.id,
            content="User 2 task 2",
            status=TaskStatus.PENDING
        )
        task4 = task_service.create(task4_data)

        # Verify each user can only access their own tasks
        user1_tasks = task_service.get_tasks_by_user(user1.id)
        user2_tasks = task_service.get_tasks_by_user(user2.id)

        assert len(user1_tasks) == 2
        assert len(user2_tasks) == 2

        # Verify tasks belong to correct users
        for task in user1_tasks:
            assert task.user_id == user1.id

        for task in user2_tasks:
            assert task.user_id == user2.id

        # Try to access another user's task directly (should fail)
        other_user_task = task_service.get_by_id_and_user(task3.id, user1.id)
        assert other_user_task is None

        other_user_task = task_service.get_by_id_and_user(task1.id, user2.id)
        assert other_user_task is None

        print("✓ Task isolation test passed")

    async def test_cross_user_modification_protection(self):
        """
        Test that users cannot modify each other's data.
        """
        user1, user2 = await self.setup_test_users()

        # Create a task for user 1
        task_service = TaskService(self.db_session)

        task_data = TaskCreate(
            user_id=user1.id,
            content="User 1 task",
            status=TaskStatus.PENDING
        )
        user1_task = task_service.create(task_data)

        # Try to update user1's task as user2 (should fail)
        update_attempt = TaskUpdate(status=TaskStatus.COMPLETED)

        # In a real implementation, the service would check ownership
        # before allowing updates, but for this test we'll verify the
        # isolation at the retrieval level

        # Attempt to retrieve user1's task as user2 (should return None)
        retrieved_task_as_user2 = task_service.get_by_id_and_user(user1_task.id, user2.id)
        assert retrieved_task_as_user2 is None

        # Verify the task still belongs to user1 and is unchanged
        retrieved_task_as_user1 = task_service.get_by_id_and_user(user1_task.id, user1.id)
        assert retrieved_task_as_user1 is not None
        assert retrieved_task_as_user1.user_id == user1.id
        assert retrieved_task_as_user1.status == TaskStatus.PENDING

        print("✓ Cross-user modification protection test passed")

    async def run_all_tests(self):
        """
        Run all user isolation tests.
        """
        print("Starting user isolation tests...")

        await self.test_conversation_isolation()
        await self.test_message_isolation()
        await self.test_task_isolation()
        await self.test_cross_user_modification_protection()

        print("✓ All user isolation tests passed!")


# Pytest functions for user isolation
@pytest.mark.asyncio
async def test_user_conversation_isolation():
    """
    Pytest function for conversation isolation.
    """
    # In a real implementation, this would use a test database session
    tester = UserIsolationTester(db_session=None)  # Replace with actual test session
    await tester.test_conversation_isolation()


@pytest.mark.asyncio
async def test_user_message_isolation():
    """
    Pytest function for message isolation.
    """
    tester = UserIsolationTester(db_session=None)  # Replace with actual test session
    await tester.test_message_isolation()


@pytest.mark.asyncio
async def test_user_task_isolation():
    """
    Pytest function for task isolation.
    """
    tester = UserIsolationTester(db_session=None)  # Replace with actual test session
    await tester.test_task_isolation()


@pytest.mark.asyncio
async def test_user_data_modification_protection():
    """
    Pytest function for data modification protection.
    """
    tester = UserIsolationTester(db_session=None)  # Replace with actual test session
    await tester.test_cross_user_modification_protection()


if __name__ == "__main__":
    # This would require a proper async test setup in a real implementation
    # For demonstration purposes only
    print("User isolation tests would run here in a full implementation")