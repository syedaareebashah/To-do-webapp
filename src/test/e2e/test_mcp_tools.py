"""
End-to-End Test for MCP Tools in Todo AI Chatbot System

This module tests the MCP tools integration with database persistence and user isolation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlmodel import Session
from uuid import uuid4
from src.models.user import User
from src.models.task import Task
from src.mcp_server.server import mcp_server
from src.services.task_service import TaskService
from src.database.session import get_session


class MCPTOOLS_E2ETester:
    """
    End-to-End tester for MCP tools functionality.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the MCP tools E2E tester.

        Args:
            db_session (Session): Database session for testing
        """
        self.db_session = db_session

    async def test_add_task_tool_integration(self):
        """
        Test the add_task MCP tool with database persistence.
        """
        # Create a test user
        user = User(username="mcp_add_test_user", email="mcp_add@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Test the add_task MCP tool
        tool_params = {
            "user_id": str(user.id),
            "content": "Test task from MCP tool",
            "priority": "medium"
        }

        result = await mcp_server.execute_tool("add_task", tool_params)

        # Verify the tool executed successfully
        assert result["success"] is True
        assert "task_id" in result
        assert result["message"] == "Task 'Test task from MCP tool' added successfully"

        # Verify the task was persisted in the database
        task_service = TaskService(self.db_session)
        created_task = task_service.get_by_id_and_user(uuid.UUID(result["task_id"]), user.id)

        assert created_task is not None
        assert created_task.content == "Test task from MCP tool"
        assert created_task.user_id == user.id

        print("✓ Add task MCP tool integration test passed")

    async def test_list_tasks_tool_integration(self):
        """
        Test the list_tasks MCP tool with database retrieval.
        """
        # Create a test user
        user = User(username="mcp_list_test_user", email="mcp_list@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Create some tasks for the user
        task_service = TaskService(self.db_session)

        task1 = Task(
            user_id=user.id,
            content="First test task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH
        )
        task2 = Task(
            user_id=user.id,
            content="Second test task",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM
        )
        self.db_session.add(task1)
        self.db_session.add(task2)
        self.db_session.commit()

        # Test the list_tasks MCP tool
        tool_params = {
            "user_id": str(user.id),
            "filter": "all"
        }

        result = await mcp_server.execute_tool("list_tasks", tool_params)

        # Verify the tool executed successfully
        assert result["success"] is True
        assert "tasks" in result
        assert len(result["tasks"]) == 2

        # Verify the tasks belong to the correct user
        for task in result["tasks"]:
            assert task["user_id"] == str(user.id)

        # Test with filter
        tool_params["filter"] = "pending"
        result_filtered = await mcp_server.execute_tool("list_tasks", tool_params)

        assert result_filtered["success"] is True
        assert len(result_filtered["tasks"]) == 1
        assert result_filtered["tasks"][0]["status"] == "pending"

        print("✓ List tasks MCP tool integration test passed")

    async def test_complete_task_tool_integration(self):
        """
        Test the complete_task MCP tool with database update.
        """
        # Create a test user
        user = User(username="mcp_complete_test_user", email="mcp_complete@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Create a task for the user
        task_service = TaskService(self.db_session)

        task = Task(
            user_id=user.id,
            content="Task to complete",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)

        # Test the complete_task MCP tool
        tool_params = {
            "user_id": str(user.id),
            "task_id": str(task.id)
        }

        result = await mcp_server.execute_tool("complete_task", tool_params)

        # Verify the tool executed successfully
        assert result["success"] is True
        assert result["task_id"] == str(task.id)
        assert "completed_at" in result

        # Verify the task status was updated in the database
        updated_task = task_service.get_by_id_and_user(task.id, user.id)
        assert updated_task is not None
        assert updated_task.status == TaskStatus.COMPLETED

        print("✓ Complete task MCP tool integration test passed")

    async def test_delete_task_tool_integration(self):
        """
        Test the delete_task MCP tool with database removal.
        """
        # Create a test user
        user = User(username="mcp_delete_test_user", email="mcp_delete@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Create a task for the user
        task_service = TaskService(self.db_session)

        task = Task(
            user_id=user.id,
            content="Task to delete",
            status=TaskStatus.PENDING,
            priority=TaskPriority.LOW
        )
        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)

        # Verify the task exists before deletion
        existing_task = task_service.get_by_id_and_user(task.id, user.id)
        assert existing_task is not None

        # Test the delete_task MCP tool
        tool_params = {
            "user_id": str(user.id),
            "task_id": str(task.id)
        }

        result = await mcp_server.execute_tool("delete_task", tool_params)

        # Verify the tool executed successfully
        assert result["success"] is True
        assert result["task_id"] == str(task.id)
        assert result["message"] == f"Task {task.id} has been deleted"

        # Verify the task was removed from the database
        deleted_task = task_service.get_by_id_and_user(task.id, user.id)
        assert deleted_task is None

        print("✓ Delete task MCP tool integration test passed")

    async def test_update_task_tool_integration(self):
        """
        Test the update_task MCP tool with database update.
        """
        # Create a test user
        user = User(username="mcp_update_test_user", email="mcp_update@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Create a task for the user
        task_service = TaskService(self.db_session)

        task = Task(
            user_id=user.id,
            content="Original task content",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)

        # Test the update_task MCP tool
        tool_params = {
            "user_id": str(user.id),
            "task_id": str(task.id),
            "updates": {
                "content": "Updated task content",
                "priority": "high"
            }
        }

        result = await mcp_server.execute_tool("update_task", tool_params)

        # Verify the tool executed successfully
        assert result["success"] is True
        assert result["task_id"] == str(task.id)
        assert "updated_fields" in result
        assert "content" in result["updated_fields"]
        assert "priority" in result["updated_fields"]

        # Verify the task was updated in the database
        updated_task = task_service.get_by_id_and_user(task.id, user.id)
        assert updated_task is not None
        assert updated_task.content == "Updated task content"
        assert updated_task.priority == TaskPriority.HIGH

        print("✓ Update task MCP tool integration test passed")

    async def test_user_isolation_in_mcp_tools(self):
        """
        Test that MCP tools properly isolate user data.
        """
        # Create two test users
        user1 = User(username="iso_user1", email="iso1@test.com")
        user2 = User(username="iso_user2", email="iso2@test.com")
        self.db_session.add(user1)
        self.db_session.add(user2)
        self.db_session.commit()
        self.db_session.refresh(user1)
        self.db_session.refresh(user2)

        # Create tasks for each user
        task_service = TaskService(self.db_session)

        task1 = Task(
            user_id=user1.id,
            content="User 1 task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        task2 = Task(
            user_id=user2.id,
            content="User 2 task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        self.db_session.add(task1)
        self.db_session.add(task2)
        self.db_session.commit()
        self.db_session.refresh(task1)
        self.db_session.refresh(task2)

        # Test that user1 cannot access user2's task via MCP tools
        # Try to complete user2's task with user1's ID
        tool_params_wrong_user = {
            "user_id": str(user1.id),  # User 1 trying to access user 2's task
            "task_id": str(task2.id)   # But the task belongs to user 2
        }

        result = await mcp_server.execute_tool("complete_task", tool_params_wrong_user)

        # This should fail because user1 doesn't own task2
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["message"].lower() or "access denied" in result["message"].lower()

        # Test that each user can access their own tasks
        # User 1 accesses their own task
        tool_params_user1 = {
            "user_id": str(user1.id),
            "task_id": str(task1.id)
        }

        result_user1 = await mcp_server.execute_tool("complete_task", tool_params_user1)
        assert result_user1["success"] is True

        # User 2 accesses their own task
        tool_params_user2 = {
            "user_id": str(user2.id),
            "task_id": str(task2.id)
        }

        result_user2 = await mcp_server.execute_tool("complete_task", tool_params_user2)
        assert result_user2["success"] is True

        # Verify that both tasks were updated correctly
        updated_task1 = task_service.get_by_id_and_user(task1.id, user1.id)
        updated_task2 = task_service.get_by_id_and_user(task2.id, user2.id)

        assert updated_task1.status == TaskStatus.COMPLETED
        assert updated_task2.status == TaskStatus.COMPLETED

        print("✓ User isolation in MCP tools test passed")

    async def test_error_handling_in_mcp_tools(self):
        """
        Test error handling in MCP tools.
        """
        # Create a test user
        user = User(username="mcp_error_test_user", email="mcp_error@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Test with invalid parameters
        invalid_params = {
            "user_id": str(user.id),
            # Missing required "task_id" parameter for complete_task
        }

        result = await mcp_server.execute_tool("complete_task", invalid_params)

        # This should return an error
        assert result["success"] is False
        assert "error" in result

        # Test with non-existent task ID
        nonexistent_task_params = {
            "user_id": str(user.id),
            "task_id": str(uuid4())  # Random UUID that doesn't exist
        }

        result_nonexistent = await mcp_server.execute_tool("complete_task", nonexistent_task_params)

        # This should return a "not found" error
        assert result_nonexistent["success"] is False
        assert "error" in result_nonexistent
        assert "not found" in result_nonexistent["message"].lower()

        print("✓ Error handling in MCP tools test passed")

    async def run_all_tests(self):
        """
        Run all MCP tools integration tests.
        """
        print("Starting MCP tools integration tests...")

        await self.test_add_task_tool_integration()
        await self.test_list_tasks_tool_integration()
        await self.test_complete_task_tool_integration()
        await self.test_delete_task_tool_integration()
        await self.test_update_task_tool_integration()
        await self.test_user_isolation_in_mcp_tools()
        await self.test_error_handling_in_mcp_tools()

        print("✓ All MCP tools integration tests passed!")


# Pytest functions for MCP tools E2E tests
@pytest.mark.asyncio
async def test_e2e_mcp_add_task():
    """
    Pytest function for add_task MCP tool.
    """
    tester = MCPTOOLS_E2ETester(db_session=None)  # Replace with actual test session
    await tester.test_add_task_tool_integration()


@pytest.mark.asyncio
async def test_e2e_mcp_list_tasks():
    """
    Pytest function for list_tasks MCP tool.
    """
    tester = MCPTOOLS_E2ETester(db_session=None)  # Replace with actual test session
    await tester.test_list_tasks_tool_integration()


@pytest.mark.asyncio
async def test_e2e_mcp_complete_task():
    """
    Pytest function for complete_task MCP tool.
    """
    tester = MCPTOOLS_E2ETester(db_session=None)  # Replace with actual test session
    await tester.test_complete_task_tool_integration()


@pytest.mark.asyncio
async def test_e2e_mcp_delete_task():
    """
    Pytest function for delete_task MCP tool.
    """
    tester = MCPTOOLS_E2ETester(db_session=None)  # Replace with actual test session
    await tester.test_delete_task_tool_integration()


@pytest.mark.asyncio
async def test_e2e_mcp_update_task():
    """
    Pytest function for update_task MCP tool.
    """
    tester = MCPTOOLS_E2ETester(db_session=None)  # Replace with actual test session
    await tester.test_update_task_tool_integration()


@pytest.mark.asyncio
async def test_e2e_mcp_user_isolation():
    """
    Pytest function for user isolation in MCP tools.
    """
    tester = MCPTOOLS_E2ETester(db_session=None)  # Replace with actual test session
    await tester.test_user_isolation_in_mcp_tools()


@pytest.mark.asyncio
async def test_e2e_mcp_error_handling():
    """
    Pytest function for error handling in MCP tools.
    """
    tester = MCPTOOLS_E2ETester(db_session=None)  # Replace with actual test session
    await tester.test_error_handling_in_mcp_tools()


if __name__ == "__main__":
    # This would require a proper async test setup in a real implementation
    # For demonstration purposes only
    print("MCP tools E2E tests would run here in a full implementation")