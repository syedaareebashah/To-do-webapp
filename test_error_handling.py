"""
Error handling tests for the Todo AI Chatbot System.
This module tests various error conditions and invalid inputs to ensure proper error responses.
"""

import asyncio
from unittest.mock import Mock, patch
from src.mcp_server.server import MCPServer
from src.services.task_service import TaskService
from src.models.task import Task, TaskStatus, TaskPriority
from uuid import uuid4
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


async def test_add_task_errors():
    """Test error conditions for add_task MCP tool"""
    print("Testing add_task error conditions...")

    mcp_server = MCPServer()

    # Test 1: Empty content
    result = await mcp_server.add_task(user_id=str(uuid4()), content="")
    assert result["success"] is False
    assert result["error"] == "INVALID_INPUT"
    assert "empty" in result["message"].lower()
    print("[PASS] Empty content validation passed")

    # Test 2: None content
    result = await mcp_server.add_task(user_id=str(uuid4()), content=None)
    assert result["success"] is False
    assert result["error"] == "INVALID_INPUT"
    print("[PASS] None content validation passed")

    # Test 3: Whitespace-only content
    result = await mcp_server.add_task(user_id=str(uuid4()), content="   ")
    assert result["success"] is False
    assert result["error"] == "INVALID_INPUT"
    assert "empty" in result["message"].lower()
    print("[PASS] Whitespace-only content validation passed")

    # Test 4: Simulate database error
    mock_session = MockDBSession()
    mock_task_service = Mock(spec=TaskService)
    mock_task_service.create_task.side_effect = Exception("Database connection failed")

    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            result = await mcp_server.add_task(
                user_id=str(uuid4()),
                content="Valid content",
                priority="high"
            )
            assert result["success"] is False
            assert result["error"] == "TASK_CREATION_FAILED"
            print("[PASS] Database error handling passed")

    print("add_task error tests completed successfully!\n")


async def test_list_tasks_errors():
    """Test error conditions for list_tasks MCP tool"""
    print("Testing list_tasks error conditions...")

    mcp_server = MCPServer()

    # Test 1: Invalid filter type
    result = await mcp_server.list_tasks(user_id=str(uuid4()), filter_type="invalid_filter")
    assert result["success"] is False
    assert result["error"] == "INVALID_FILTER"
    assert "invalid" in result["message"].lower()
    print("[PASS] Invalid filter type validation passed")

    # Test 2: Simulate database error
    mock_session = MockDBSession()
    mock_task_service = Mock(spec=TaskService)
    mock_task_service.get_tasks_by_user.side_effect = Exception("Database query failed")

    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            result = await mcp_server.list_tasks(user_id=str(uuid4()))
            assert result["success"] is False
            assert result["error"] == "LIST_RETRIEVAL_FAILED"
            print("[PASS] Database error handling passed")

    print("list_tasks error tests completed successfully!\n")


async def test_complete_task_errors():
    """Test error conditions for complete_task MCP tool"""
    print("Testing complete_task error conditions...")

    mcp_server = MCPServer()

    # Test 1: Non-existent task
    mock_session = MockDBSession()
    mock_task_service = Mock(spec=TaskService)
    mock_task_service.update_task_status.return_value = None  # Simulate task not found

    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            result = await mcp_server.complete_task(
                user_id=str(uuid4()),
                task_id=str(uuid4())
            )
            assert result["success"] is False
            assert result["error"] == "TASK_NOT_FOUND"
            print("[PASS] Task not found validation passed")

    # Test 2: Simulate database error
    mock_task_service.update_task_status.side_effect = Exception("Database update failed")

    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            result = await mcp_server.complete_task(
                user_id=str(uuid4()),
                task_id=str(uuid4())
            )
            assert result["success"] is False
            assert result["error"] == "TASK_COMPLETION_FAILED"
            print("[PASS] Database error handling passed")

    print("complete_task error tests completed successfully!\n")


async def test_delete_task_errors():
    """Test error conditions for delete_task MCP tool"""
    print("Testing delete_task error conditions...")

    mcp_server = MCPServer()

    # Test 1: Non-existent task
    mock_session = MockDBSession()
    mock_task_service = Mock(spec=TaskService)
    mock_task_service.delete_task.return_value = None  # Simulate task not found

    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            result = await mcp_server.delete_task(
                user_id=str(uuid4()),
                task_id=str(uuid4())
            )
            assert result["success"] is False
            assert result["error"] == "TASK_NOT_FOUND"
            print("[PASS] Task not found validation passed")

    # Test 2: Simulate database error
    mock_task_service.delete_task.side_effect = Exception("Database delete failed")

    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            result = await mcp_server.delete_task(
                user_id=str(uuid4()),
                task_id=str(uuid4())
            )
            assert result["success"] is False
            assert result["error"] == "TASK_DELETION_FAILED"
            print("[PASS] Database error handling passed")

    print("delete_task error tests completed successfully!\n")


async def test_update_task_errors():
    """Test error conditions for update_task MCP tool"""
    print("Testing update_task error conditions...")

    mcp_server = MCPServer()

    # Test 1: Invalid field in updates
    result = await mcp_server.update_task(
        user_id=str(uuid4()),
        task_id=str(uuid4()),
        updates={"invalid_field": "some_value"}
    )
    assert result["success"] is False
    assert result["error"] == "INVALID_INPUT"
    assert "invalid" in result["message"].lower()
    print("[PASS] Invalid field validation passed")

    # Test 2: Non-existent task
    mock_session = MockDBSession()
    mock_task_service = Mock(spec=TaskService)
    mock_task_service.partial_update_task.return_value = None  # Simulate task not found

    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            result = await mcp_server.update_task(
                user_id=str(uuid4()),
                task_id=str(uuid4()),
                updates={"content": "Updated content"}
            )
            assert result["success"] is False
            assert result["error"] == "TASK_NOT_FOUND"
            print("[PASS] Task not found validation passed")

    # Test 3: Simulate database error
    mock_task_service.partial_update_task.side_effect = Exception("Database update failed")

    with patch('src.mcp_server.server.get_db_session', return_value=mock_session):
        with patch('src.mcp_server.server.TaskService', return_value=mock_task_service):
            result = await mcp_server.update_task(
                user_id=str(uuid4()),
                task_id=str(uuid4()),
                updates={"content": "Updated content"}
            )
            assert result["success"] is False
            assert result["error"] == "TASK_UPDATE_FAILED"
            print("[PASS] Database error handling passed")

    print("update_task error tests completed successfully!\n")


async def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("Testing edge cases...")

    mcp_server = MCPServer()

    # Test with very long content
    long_content = "A" * 1000  # Exceeds typical length limits
    result = await mcp_server.add_task(user_id=str(uuid4()), content=long_content)
    # This might pass or fail depending on validation, but shouldn't crash
    assert isinstance(result, dict)
    assert "success" in result
    print("[PASS] Long content handling passed")

    # Test with maximum limit values
    result = await mcp_server.list_tasks(user_id=str(uuid4()), limit=10000)
    # Should handle large limits gracefully
    assert isinstance(result, dict)
    assert "success" in result
    print("[PASS] Large limit handling passed")

    # Test with invalid UUID-like strings
    result = await mcp_server.list_tasks(user_id="not-a-valid-uuid")
    # Should handle invalid user_id gracefully
    assert isinstance(result, dict)
    assert "success" in result
    print("[PASS] Invalid UUID handling passed")

    print("Edge case tests completed successfully!\n")


async def run_all_error_tests():
    """Run all error handling tests"""
    print("=" * 60)
    print("ERROR HANDLING TESTS")
    print("=" * 60)

    try:
        await test_add_task_errors()
        await test_list_tasks_errors()
        await test_complete_task_errors()
        await test_delete_task_errors()
        await test_update_task_errors()
        await test_edge_cases()

        print("=" * 60)
        print("ALL ERROR HANDLING TESTS PASSED! [SUCCESS]")
        print("System properly handles invalid inputs and error conditions.")
        print("=" * 60)

    except Exception as e:
        print(f"[FAILED] Error handling test failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_error_tests())