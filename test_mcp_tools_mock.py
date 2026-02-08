"""
Mock test for MCP tools to verify they work correctly with mocked database operations.
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


async def test_mcp_add_task():
    """Test the add_task MCP tool"""
    print("Testing add_task MCP tool...")

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
                user_id=str(uuid4()),  # Convert UUID to string for the MCP tool
                content="Buy groceries",
                due_date="2023-12-31",
                priority="high"
            )

            # Verify the result
            assert result["success"] is True
            assert result["task_id"] is not None
            assert "Buy groceries" in result["message"]
            print(f"[PASS] add_task test passed: {result}")

    print("add_task MCP tool test completed successfully!\n")


async def test_mcp_list_tasks():
    """Test the list_tasks MCP tool"""
    print("Testing list_tasks MCP tool...")

    # Create MCP server instance
    mcp_server = MCPServer()

    # Create mock tasks
    mock_tasks = [
        create_mock_task(task_id=uuid4(), content="Task 1", status=TaskStatus.PENDING),
        create_mock_task(task_id=uuid4(), content="Task 2", status=TaskStatus.COMPLETED),
        create_mock_task(task_id=uuid4(), content="Task 3", status=TaskStatus.PENDING),
    ]

    # Mock the database session and task service
    mock_session = MockDBSession()
    mock_task_service = Mock(spec=TaskService)
    mock_task_service.get_tasks_by_user.return_value = mock_tasks

    # Patch the get_db_session function to return our mock session
    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            # Call the list_tasks method
            result = await mcp_server.list_tasks(user_id=str(uuid4()))

            # Verify the result
            assert result["success"] is True
            assert len(result["tasks"]) == 3
            assert result["total_count"] == 3
            print(f"[PASS] list_tasks test passed: {result['total_count']} tasks retrieved")

    print("list_tasks MCP tool test completed successfully!\n")


async def test_mcp_complete_task():
    """Test the complete_task MCP tool"""
    print("Testing complete_task MCP tool...")

    # Create MCP server instance
    mcp_server = MCPServer()

    # Create a mock task that will be returned by the service
    mock_task = create_mock_task(content="Complete this task")
    mock_task.status = TaskStatus.COMPLETED
    mock_task.completed_at = datetime.utcnow()

    # Mock the database session and task service
    mock_session = MockDBSession()
    mock_task_service = Mock(spec=TaskService)
    mock_task_service.update_task_status.return_value = mock_task

    # Patch the get_db_session function to return our mock session
    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            # Call the complete_task method
            result = await mcp_server.complete_task(
                user_id=str(uuid4()),
                task_id=str(uuid4())
            )

            # Verify the result
            assert result["success"] is True
            assert result["task_id"] is not None
            print(f"[PASS] complete_task test passed: {result}")

    print("complete_task MCP tool test completed successfully!\n")


async def test_mcp_delete_task():
    """Test the delete_task MCP tool"""
    print("Testing delete_task MCP tool...")

    # Create MCP server instance
    mcp_server = MCPServer()

    # Create a mock task that will be returned by the service
    mock_task = create_mock_task(content="Delete this task")

    # Mock the database session and task service
    mock_session = MockDBSession()
    mock_task_service = Mock(spec=TaskService)
    mock_task_service.delete_task.return_value = mock_task

    # Patch the get_db_session function to return our mock session
    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            # Call the delete_task method
            result = await mcp_server.delete_task(
                user_id=str(uuid4()),
                task_id=str(uuid4())
            )

            # Verify the result
            assert result["success"] is True
            assert result["task_id"] is not None
            print(f"[PASS] delete_task test passed: {result}")

    print("delete_task MCP tool test completed successfully!\n")


async def test_mcp_update_task():
    """Test the update_task MCP tool"""
    print("Testing update_task MCP tool...")

    # Create MCP server instance
    mcp_server = MCPServer()

    # Create a mock task that will be returned by the service
    mock_task = create_mock_task(content="Updated task content")
    mock_task.updated_at = datetime.utcnow()

    # Mock the database session and task service
    mock_session = MockDBSession()
    mock_task_service = Mock(spec=TaskService)
    mock_task_service.partial_update_task.return_value = mock_task

    # Patch the get_db_session function to return our mock session
    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            # Call the update_task method
            updates = {
                "content": "Updated task content",
                "priority": "high"
            }
            result = await mcp_server.update_task(
                user_id=str(uuid4()),
                task_id=str(uuid4()),
                updates=updates
            )

            # Verify the result
            assert result["success"] is True
            assert result["task_id"] is not None
            assert "has been updated" in result["message"]  # Expected message format
            print(f"[PASS] update_task test passed: {result}")

    print("update_task MCP tool test completed successfully!\n")


async def test_error_conditions():
    """Test error conditions for MCP tools"""
    print("Testing error conditions...")

    # Create MCP server instance
    mcp_server = MCPServer()

    # Test add_task with empty content
    result = await mcp_server.add_task(user_id=str(uuid4()), content="")
    assert result["success"] is False
    assert result["error"] == "INVALID_INPUT"
    print("[PASS] Empty content validation test passed")

    # Test list_tasks with invalid filter
    result = await mcp_server.list_tasks(user_id=str(uuid4()), filter_type="invalid_filter")
    assert result["success"] is False
    assert result["error"] == "INVALID_FILTER"
    print("[PASS] Invalid filter validation test passed")

    print("Error condition tests completed successfully!\n")


async def run_all_tests():
    """Run all MCP tool tests"""
    print("=" * 60)
    print("MCP TOOLS MOCK TESTING")
    print("=" * 60)

    try:
        await test_mcp_add_task()
        await test_mcp_list_tasks()
        await test_mcp_complete_task()
        await test_mcp_delete_task()
        await test_mcp_update_task()
        await test_error_conditions()

        print("=" * 60)
        print("ALL MCP TOOL TESTS PASSED! [SUCCESS]")
        print("MCP tools are working correctly with mocked database operations.")
        print("=" * 60)

    except Exception as e:
        print(f"X Test failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())