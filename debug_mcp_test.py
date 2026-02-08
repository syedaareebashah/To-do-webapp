"""
Debug test for MCP tools to see what's happening with the mocked database operations.
"""

import asyncio
from unittest.mock import Mock, patch, MagicMock
from src.mcp_server.server import MCPServer
from src.services.task_service import TaskService
from src.models.task import Task, TaskStatus, TaskPriority
from uuid import UUID, uuid4
from datetime import datetime


class MockDBSession:
    """Mock database session for testing"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def create_mock_task(task_id=None, user_id=None, content="Test task",
                     status=TaskStatus.PENDING, due_date=None, priority=TaskPriority.MEDIUM):
    """Helper to create mock task objects"""
    if task_id is None:
        task_id = uuid4()
    if user_id is None:
        user_id = uuid4()  # user_id should be a UUID

    mock_task = Mock(spec=Task)
    mock_task.id = task_id
    mock_task.user_id = user_id
    mock_task.content = content
    mock_task.status = status
    mock_task.due_date = due_date
    mock_task.priority = priority
    mock_task.created_at = datetime.utcnow()
    mock_task.completed_at = None
    mock_task.updated_at = datetime.utcnow()

    return mock_task


async def debug_mcp_add_task():
    """Debug the add_task MCP tool"""
    print("Debugging add_task MCP tool...")

    # Create MCP server instance
    mcp_server = MCPServer()

    # Mock the database session and task service
    mock_session = MockDBSession()
    mock_task_service = Mock(spec=TaskService)

    # Create a mock task that will be returned by the service
    mock_created_task = create_mock_task(content="Buy groceries")

    # Configure the mock to return our test task
    mock_task_service.create.return_value = mock_created_task

    # Patch the get_db_session function to return our mock session
    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            # Call the add_task method
            result = await mcp_server.add_task(
                user_id=str(uuid4()),
                content="Buy groceries",
                due_date="2023-12-31",
                priority="high"
            )

            print(f"Result: {result}")
            print(f"Success: {result.get('success', 'NO SUCCESS KEY')}")

            # Check if there are any errors
            if result.get('error'):
                print(f"Error: {result['error']}")
                print(f"Message: {result['message']}")


if __name__ == "__main__":
    asyncio.run(debug_mcp_add_task())