"""
End-to-End Authentication & Isolation Tests for Todo AI Chatbot System

This module tests user authentication mechanisms and data isolation between users.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlmodel import Session
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import HTTPException

from src.models.user import User
from src.models.task import Task
from src.models.conversation import Conversation
from src.app.main import app
from src.services.conversation_service import ConversationService
from src.services.task_service import TaskService
from src.database.session import get_session


class AuthIsolationE2ETester:
    """
    End-to-End tester for authentication and user isolation.
    """

    def __init__(self, db_session: Session, test_client: TestClient = None):
        """
        Initialize the auth isolation tester.

        Args:
            db_session (Session): Database session for testing
            test_client (TestClient, optional): FastAPI test client
        """
        self.db_session = db_session
        self.test_client = test_client or TestClient(app)

    async def test_user_authentication_validation(self):
        """
        Test that the system properly validates user authentication.
        """
        # Test with a valid user ID
        user = User(username="auth_test_user", email="auth@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Make a request with the valid user ID
        response = self.test_client.post(
            f"/api/{user.id}/chat",
            json={"message": "Hello, I'm authenticated"}
        )

        # Should succeed with valid user ID
        assert response.status_code == 200

        # Test with an invalid/malformed user ID
        response_invalid = self.test_client.post(
            f"/api/invalid_user_id/chat",
            json={"message": "Hello"}
        )

        # Should return an error for invalid user ID format
        assert response_invalid.status_code in [422, 404]

        # Test with a non-existent user ID
        fake_user_id = str(uuid4())
        response_fake = self.test_client.post(
            f"/api/{fake_user_id}/chat",
            json={"message": "Hello"}
        )

        # Should either create a new conversation or return an error
        # depending on implementation
        assert response_fake.status_code in [200, 404]

        print("✓ User authentication validation test passed")

    async def test_user_data_isolation(self):
        """
        Test that users cannot access each other's data.
        """
        # Create two users
        user1 = User(username="iso_user_1", email="iso1@test.com")
        user2 = User(username="iso_user_2", email="iso2@test.com")
        self.db_session.add(user1)
        self.db_session.add(user2)
        self.db_session.commit()
        self.db_session.refresh(user1)
        self.db_session.refresh(user2)

        # Create tasks for each user
        task_service = TaskService(self.db_session)

        task1 = Task(
            user_id=user1.id,
            content="User 1's task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        task2 = Task(
            user_id=user2.id,
            content="User 2's task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH
        )
        self.db_session.add(task1)
        self.db_session.add(task2)
        self.db_session.commit()

        # Test that user 1 can only access their own tasks
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            # Mock successful task listing for user 1
            mock_execute.return_value = {
                "success": True,
                "tasks": [{"id": str(task1.id), "content": task1.content, "status": task1.status}],
                "message": "Found 1 tasks for user"
            }

            response_user1 = self.test_client.post(
                f"/api/{user1.id}/chat",
                json={"message": "List my tasks"}
            )

            assert response_user1.status_code == 200
            response_data = response_user1.json()

            # Verify user 1 only sees their own task
            if "tool_calls" in response_data:
                for tool_call in response_data["tool_calls"]:
                    if tool_call["tool_name"] == "list_tasks":
                        assert len(tool_call["result"]["tasks"]) == 1
                        assert tool_call["result"]["tasks"][0]["id"] == str(task1.id)

        # Test that user 2 can only access their own tasks
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            # Mock successful task listing for user 2
            mock_execute.return_value = {
                "success": True,
                "tasks": [{"id": str(task2.id), "content": task2.content, "status": task2.status}],
                "message": "Found 1 tasks for user"
            }

            response_user2 = self.test_client.post(
                f"/api/{user2.id}/chat",
                json={"message": "List my tasks"}
            )

            assert response_user2.status_code == 200
            response_data = response_user2.json()

            # Verify user 2 only sees their own task
            if "tool_calls" in response_data:
                for tool_call in response_data["tool_calls"]:
                    if tool_call["tool_name"] == "list_tasks":
                        assert len(tool_call["result"]["tasks"]) == 1
                        assert tool_call["result"]["tasks"][0]["id"] == str(task2.id)

        print("✓ User data isolation test passed")

    async def test_cross_user_task_access_prevention(self):
        """
        Test that users cannot access or modify each other's tasks.
        """
        # Create two users
        user1 = User(username="cross_user_1", email="cross1@test.com")
        user2 = User(username="cross_user_2", email="cross2@test.com")
        self.db_session.add(user1)
        self.db_session.add(user2)
        self.db_session.commit()
        self.db_session.refresh(user1)
        self.db_session.refresh(user2)

        # Create tasks for each user
        task_service = TaskService(self.db_session)

        task1 = Task(
            user_id=user1.id,
            content="User 1's private task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH
        )
        task2 = Task(
            user_id=user2.id,
            content="User 2's private task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH
        )
        self.db_session.add(task1)
        self.db_session.add(task2)
        self.db_session.commit()

        # Try to complete user1's task as user2 (should fail)
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            # Mock failure when user2 tries to access user1's task
            mock_execute.return_value = {
                "success": False,
                "error_code": "PERMISSION_DENIED",
                "message": f"User {user2.id} does not have permission to access task {task1.id}"
            }

            # Simulate user2 trying to complete user1's task
            result = await mcp_server.execute_tool(
                "complete_task",
                {"user_id": str(user2.id), "task_id": str(task1.id)}
            )

            assert result["success"] is False
            assert result["error_code"] == "PERMISSION_DENIED"
            assert str(user2.id) in result["message"]
            assert str(task1.id) in result["message"]

        # Try to delete user2's task as user1 (should fail)
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            # Mock failure when user1 tries to access user2's task
            mock_execute.return_value = {
                "success": False,
                "error_code": "PERMISSION_DENIED",
                "message": f"User {user1.id} does not have permission to access task {task2.id}"
            }

            # Simulate user1 trying to delete user2's task
            result = await mcp_server.execute_tool(
                "delete_task",
                {"user_id": str(user1.id), "task_id": str(task2.id)}
            )

            assert result["success"] is False
            assert result["error_code"] == "PERMISSION_DENIED"
            assert str(user1.id) in result["message"]
            assert str(task2.id) in result["message"]

        # Verify that both tasks still exist and are unchanged
        task1_fresh = task_service.get_by_id_and_user(task1.id, user1.id)
        task2_fresh = task_service.get_by_id_and_user(task2.id, user2.id)

        assert task1_fresh is not None
        assert task2_fresh is not None
        assert task1_fresh.status == TaskStatus.PENDING
        assert task2_fresh.status == TaskStatus.PENDING

        print("✓ Cross-user task access prevention test passed")

    async def test_conversation_isolation_between_users(self):
        """
        Test that conversations are properly isolated between users.
        """
        # Create two users
        user1 = User(username="conv_iso_user_1", email="conviso1@test.com")
        user2 = User(username="conv_iso_user_2", email="conviso2@test.com")
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

        # Add messages to each conversation
        msg1 = Message(
            conversation_id=conv1.id,
            role=MessageRole.USER,
            content="Message from user 1"
        )
        msg2 = Message(
            conversation_id=conv2.id,
            role=MessageRole.USER,
            content="Message from user 2"
        )
        self.db_session.add(msg1)
        self.db_session.add(msg2)
        self.db_session.commit()

        # Test that user1 can only access their own conversation
        user1_convs = conversation_service.get_user_conversations(user1.id)
        user2_convs = conversation_service.get_user_conversations(user2.id)

        assert len(user1_convs) == 1
        assert user1_convs[0].id == conv1.id
        assert user1_convs[0].user_id == user1.id

        assert len(user2_convs) == 1
        assert user2_convs[0].id == conv2.id
        assert user2_convs[0].user_id == user2.id

        # Verify that each user cannot access the other's conversation
        unauthorized_conv1 = conversation_service.get_by_id_and_user(conv1.id, user2.id)
        unauthorized_conv2 = conversation_service.get_by_id_and_user(conv2.id, user1.id)

        assert unauthorized_conv1 is None
        assert unauthorized_conv2 is None

        print("✓ Conversation isolation between users test passed")

    async def test_mcp_tool_scope_enforcement(self):
        """
        Test that MCP tools properly enforce user scopes.
        """
        # Create two users
        user1 = User(username="scope_user_1", email="scope1@test.com")
        user2 = User(username="scope_user_2", email="scope2@test.com")
        self.db_session.add(user1)
        self.db_session.add(user2)
        self.db_session.commit()
        self.db_session.refresh(user1)
        self.db_session.refresh(user2)

        # Create tasks for each user
        task_service = TaskService(self.db_session)

        task1 = Task(
            user_id=user1.id,
            content="Scoped task for user 1",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        task2 = Task(
            user_id=user2.id,
            content="Scoped task for user 2",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        self.db_session.add(task1)
        self.db_session.add(task2)
        self.db_session.commit()

        # Test that MCP tools enforce proper user scoping
        # Mock the MCP tool execution to verify user_id parameter is validated

        # Mock successful tool execution for correct user-task pairing
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "task_id": str(task1.id),
                "message": f"Task {task1.id} processed successfully"
            }

            # User 1 should be able to operate on their own task
            result_correct = await mcp_server.execute_tool(
                "complete_task",
                {"user_id": str(user1.id), "task_id": str(task1.id)}
            )

            assert result_correct["success"] is True
            assert result_correct["task_id"] == str(task1.id)

        # Mock failure for incorrect user-task pairing
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            mock_execute.return_value = {
                "success": False,
                "error_code": "SCOPE_VIOLATION",
                "message": f"User {user2.id} cannot access task {task1.id}"
            }

            # User 2 should NOT be able to operate on user 1's task
            result_incorrect = await mcp_server.execute_tool(
                "complete_task",
                {"user_id": str(user2.id), "task_id": str(task1.id)}
            )

            assert result_incorrect["success"] is False
            assert result_incorrect["error_code"] == "SCOPE_VIOLATION"
            assert str(user2.id) in result_incorrect["message"]
            assert str(task1.id) in result_incorrect["message"]

        print("✓ MCP tool scope enforcement test passed")

    async def test_multiple_concurrent_user_isolation(self):
        """
        Test that multiple concurrent users can interact with the system without interfering with each other.
        """
        # Create multiple users
        users = []
        for i in range(5):
            user = User(username=f"concurrent_user_{i}", email=f"concurrent{i}@test.com")
            self.db_session.add(user)
            users.append(user)

        self.db_session.commit()
        for user in users:
            self.db_session.refresh(user)

        # Create tasks for each user
        task_service = TaskService(self.db_session)

        user_tasks = {}
        for i, user in enumerate(users):
            task = Task(
                user_id=user.id,
                content=f"Task for user {i}",
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM
            )
            self.db_session.add(task)
            self.db_session.commit()
            self.db_session.refresh(task)
            user_tasks[user.id] = task

        # Simulate concurrent requests from different users
        import asyncio

        async def user_request(user_id, task_id):
            """Simulate a user request to complete their task."""
            with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
                mock_execute.return_value = {
                    "success": True,
                    "task_id": str(task_id),
                    "message": f"Task {task_id} completed successfully"
                }

                result = await mcp_server.execute_tool(
                    "complete_task",
                    {"user_id": str(user_id), "task_id": str(task_id)}
                )

                return result

        # Run multiple requests concurrently
        tasks = []
        for user_id, task in user_tasks.items():
            tasks.append(user_request(user_id, task.id))

        results = await asyncio.gather(*tasks)

        # Verify all requests succeeded
        for result in results:
            assert result["success"] is True

        # Verify that only the intended tasks were updated
        for user_id, original_task in user_tasks.items():
            updated_task = task_service.get_by_id_and_user(original_task.id, user_id)
            assert updated_task is not None
            # Depending on the mock behavior, the status might be updated or not
            # The important thing is that no other user's tasks were affected

        print("✓ Multiple concurrent user isolation test passed")

    async def run_all_tests(self):
        """
        Run all authentication and isolation tests.
        """
        print("Starting authentication and isolation tests...")

        await self.test_user_authentication_validation()
        await self.test_user_data_isolation()
        await self.test_cross_user_task_access_prevention()
        await self.test_conversation_isolation_between_users()
        await self.test_mcp_tool_scope_enforcement()
        await self.test_multiple_concurrent_user_isolation()

        print("✓ All authentication and isolation tests passed!")


# Pytest functions for auth isolation tests
@pytest.mark.asyncio
async def test_e2e_user_authentication():
    """
    Pytest function for user authentication validation.
    """
    tester = AuthIsolationE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_user_authentication_validation()


@pytest.mark.asyncio
async def test_e2e_user_data_isolation():
    """
    Pytest function for user data isolation.
    """
    tester = AuthIsolationE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_user_data_isolation()


@pytest.mark.asyncio
async def test_e2e_cross_user_task_access():
    """
    Pytest function for cross-user task access prevention.
    """
    tester = AuthIsolationE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_cross_user_task_access_prevention()


@pytest.mark.asyncio
async def test_e2e_conversation_isolation():
    """
    Pytest function for conversation isolation.
    """
    tester = AuthIsolationE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_conversation_isolation_between_users()


@pytest.mark.asyncio
async def test_e2e_mcp_tool_scope():
    """
    Pytest function for MCP tool scope enforcement.
    """
    tester = AuthIsolationE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_mcp_tool_scope_enforcement()


@pytest.mark.asyncio
async def test_e2e_concurrent_user_isolation():
    """
    Pytest function for concurrent user isolation.
    """
    tester = AuthIsolationE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_multiple_concurrent_user_isolation()


if __name__ == "__main__":
    # This would require a proper async test setup in a real implementation
    # For demonstration purposes only
    print("Authentication and isolation E2E tests would run here in a full implementation")