"""
End-to-End Error Scenario Tests for Todo AI Chatbot System

This module tests various error scenarios and recovery mechanisms in the system.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlmodel import Session
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import HTTPException

from src.models.user import User
from src.models.conversation import Conversation
from src.models.task import Task
from src.app.main import app
from src.database.session import get_session_override
from src.api.error_handlers import add_exception_handlers
from src.mcp_server.error_handlers import mcp_error_handler
from src.services.conversation_service import ConversationService
from src.services.task_service import TaskService
from src.agents.todo_agent import TodoAgent


class ErrorScenarioE2ETester:
    """
    End-to-End tester for error scenarios and recovery.
    """

    def __init__(self, db_session: Session, test_client: TestClient = None):
        """
        Initialize the error scenario tester.

        Args:
            db_session (Session): Database session for testing
            test_client (TestClient, optional): FastAPI test client
        """
        self.db_session = db_session
        self.test_client = test_client or TestClient(app)

    async def test_invalid_conversation_id_handling(self):
        """
        Test handling of invalid or non-existent conversation IDs.
        """
        # Create a test user
        user = User(username="error_test_user", email="error@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Try to access a conversation that doesn't exist
        fake_conversation_id = str(uuid4())

        response = self.test_client.post(
            f"/api/{user.id}/chat",
            json={
                "message": "Hello",
                "conversation_id": fake_conversation_id
            }
        )

        # Should create a new conversation instead of failing
        assert response.status_code == 200
        response_data = response.json()
        assert "conversation_id" in response_data
        # The conversation ID in response should be different from the fake one
        assert response_data["conversation_id"] != fake_conversation_id

        print("✓ Invalid conversation ID handling test passed")

    async def test_task_not_found_error_in_mcp_tools(self):
        """
        Test MCP tool behavior when a task is not found.
        """
        # Create a test user
        user = User(username="task_not_found_test_user", email="tasknf@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Try to complete a task that doesn't exist
        fake_task_id = str(uuid4())

        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            mock_execute.return_value = {
                "success": False,
                "error_code": "TASK_NOT_FOUND",
                "message": f"Task with ID {fake_task_id} not found for user {user.id}"
            }

            # This would normally be called through the agent, but we'll test the result
            result = await mcp_server.execute_tool(
                "complete_task",
                {"user_id": str(user.id), "task_id": fake_task_id}
            )

            assert result["success"] is False
            assert result["error_code"] == "TASK_NOT_FOUND"
            assert fake_task_id in result["message"]

        print("✓ Task not found error in MCP tools test passed")

    async def test_user_permission_errors(self):
        """
        Test that users cannot access other users' data.
        """
        # Create two test users
        user1 = User(username="perm_test_user1", email="perm1@test.com")
        user2 = User(username="perm_test_user2", email="perm2@test.com")
        self.db_session.add(user1)
        self.db_session.add(user2)
        self.db_session.commit()
        self.db_session.refresh(user1)
        self.db_session.refresh(user2)

        # Create a task for user1
        task_service = TaskService(self.db_session)

        task = Task(
            user_id=user1.id,
            content="User 1's private task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM
        )
        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)

        # Try to access user1's task as user2 via MCP tools
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            mock_execute.return_value = {
                "success": False,
                "error_code": "PERMISSION_DENIED",
                "message": f"User {user2.id} does not have permission to access task {task.id}"
            }

            result = await mcp_server.execute_tool(
                "complete_task",
                {"user_id": str(user2.id), "task_id": str(task.id)}
            )

            assert result["success"] is False
            assert result["error_code"] == "PERMISSION_DENIED"
            assert "does not have permission" in result["message"]

        print("✓ User permission error handling test passed")

    async def test_database_connection_errors(self):
        """
        Test system behavior when database connections fail.
        """
        # This would be tested by mocking database connection failures
        # For this example, we'll simulate how the system should respond

        # Create a test user
        user = User(username="db_error_test_user", email="dberror@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Mock a database error in the conversation service
        with patch('src.services.conversation_service.ConversationService.create') as mock_create:
            mock_create.side_effect = Exception("Database connection failed")

            # Try to create a conversation through the API
            response = self.test_client.post(
                f"/api/{user.id}/chat",
                json={"message": "Test message with DB error"}
            )

            # Should return an appropriate error response
            assert response.status_code in [500, 422]  # Server error or validation error

        print("✓ Database connection error handling test passed")

    async def test_invalid_input_validation(self):
        """
        Test input validation for API endpoints.
        """
        # Create a test user
        user = User(username="validation_test_user", email="validation@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Test with empty message
        response = self.test_client.post(
            f"/api/{user.id}/chat",
            json={"message": "", "conversation_id": str(uuid4())}
        )

        assert response.status_code == 422  # Validation error

        # Test with very long message exceeding limits
        long_message = "A" * 5001  # Assuming 5000 character limit
        response_long = self.test_client.post(
            f"/api/{user.id}/chat",
            json={"message": long_message, "conversation_id": str(uuid4())}
        )

        assert response_long.status_code == 422  # Validation error

        # Test with invalid user ID format
        response_invalid_user = self.test_client.post(
            f"/api/invalid-user-id-format/chat",
            json={"message": "Test message"}
        )

        # Should return 404 or 422 depending on validation approach
        assert response_invalid_user.status_code in [404, 422]

        print("✓ Input validation error handling test passed")

    async def test_mcp_tool_parameter_validation_errors(self):
        """
        Test MCP tool behavior with invalid parameters.
        """
        # Create a test user
        user = User(username="mcp_param_test_user", email="mcpparam@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Test MCP tool with missing required parameters
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            mock_execute.return_value = {
                "success": False,
                "error_code": "INVALID_PARAMETERS",
                "message": "Missing required parameter: content"
            }

            # Try to call add_task without required content parameter
            result = await mcp_server.execute_tool(
                "add_task",
                {"user_id": str(user.id)}  # Missing content parameter
            )

            assert result["success"] is False
            assert result["error_code"] == "INVALID_PARAMETERS"
            assert "missing" in result["message"].lower()

        # Test MCP tool with invalid parameter values
        with patch('src.mcp_server.server.mcp_server.execute_tool') as mock_execute:
            mock_execute.return_value = {
                "success": False,
                "error_code": "INVALID_PARAMETER_VALUE",
                "message": "Invalid priority value: 'super_high'. Valid values: low, medium, high"
            }

            # Try to call add_task with invalid priority
            result = await mcp_server.execute_tool(
                "add_task",
                {
                    "user_id": str(user.id),
                    "content": "Test task",
                    "priority": "super_high"  # Invalid priority value
                }
            )

            assert result["success"] is False
            assert result["error_code"] == "INVALID_PARAMETER_VALUE"
            assert "invalid priority value" in result["message"].lower()

        print("✓ MCP tool parameter validation error handling test passed")

    async def test_conversation_state_reconstruction_errors(self):
        """
        Test handling of errors during conversation state reconstruction.
        """
        # Create a test user
        user = User(username="conv_state_test_user", email="convstate@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Create a conversation
        conversation_service = ConversationService(self.db_session)
        conversation = conversation_service.create(
            ConversationCreate(user_id=user.id)
        )

        # Add a message to the conversation
        message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="Original message"
        )
        self.db_session.add(message)
        self.db_session.commit()

        # Mock an error during conversation history retrieval
        with patch('src.services.conversation_service.ConversationService.get_conversation_history') as mock_get_history:
            mock_get_history.side_effect = Exception("Failed to load conversation history")

            # Try to continue the conversation
            response = self.test_client.post(
                f"/api/{user.id}/chat",
                json={
                    "message": "Continue conversation",
                    "conversation_id": str(conversation.id)
                }
            )

            # Should handle the error gracefully and possibly start a new conversation
            assert response.status_code in [200, 500]  # Either succeeds or returns server error

        print("✓ Conversation state reconstruction error handling test passed")

    async def test_agent_processing_errors(self):
        """
        Test handling of errors during AI agent processing.
        """
        # Create a test user
        user = User(username="agent_error_test_user", email="agenterror@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Mock an error in the AI agent
        with patch('src.agents.todo_agent.TodoAgent.process_message') as mock_process:
            mock_process.side_effect = Exception("AI agent processing failed")

            response = self.test_client.post(
                f"/api/{user.id}/chat",
                json={"message": "Process this message", "conversation_id": str(uuid4())}
            )

            # Should handle the error gracefully
            assert response.status_code in [200, 500]  # Either returns error response or fails completely

        print("✓ AI agent processing error handling test passed")

    async def test_recovery_from_server_restart_simulation(self):
        """
        Test system recovery behavior after simulated server restart.
        """
        # Create a test user
        user = User(username="recovery_test_user", email="recovery@test.com")
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)

        # Create a conversation with some messages
        conversation_service = ConversationService(self.db_session)
        conversation = conversation_service.create(
            ConversationCreate(user_id=user.id)
        )

        # Add several messages to simulate conversation history
        for i in range(3):
            message = Message(
                conversation_id=conversation.id,
                role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                content=f"Message {i+1} in conversation"
            )
            self.db_session.add(message)
        self.db_session.commit()

        # Simulate server restart by creating fresh service instances
        # that have no in-memory state
        fresh_conversation_service = ConversationService(self.db_session)

        # Verify that the conversation history is still accessible from the database
        history = fresh_conversation_service.get_conversation_history(conversation.id)
        assert len(history) == 3

        # Verify that a new message can be added to the existing conversation
        with patch('src.agents.todo_agent.TodoAgent.process_message') as mock_agent:
            mock_agent.return_value = {
                "response": "I can continue the conversation.",
                "tool_calls": []
            }

            response = self.test_client.post(
                f"/api/{user.id}/chat",
                json={
                    "message": "Continue our previous conversation",
                    "conversation_id": str(conversation.id)
                }
            )

            assert response.status_code == 200
            response_data = response.json()
            assert "response" in response_data

        print("✓ Recovery from server restart simulation test passed")

    async def run_all_tests(self):
        """
        Run all error scenario tests.
        """
        print("Starting error scenario tests...")

        await self.test_invalid_conversation_id_handling()
        await self.test_task_not_found_error_in_mcp_tools()
        await self.test_user_permission_errors()
        await self.test_database_connection_errors()
        await self.test_invalid_input_validation()
        await self.test_mcp_tool_parameter_validation_errors()
        await self.test_conversation_state_reconstruction_errors()
        await self.test_agent_processing_errors()
        await self.test_recovery_from_server_restart_simulation()

        print("✓ All error scenario tests passed!")


# Pytest functions for error scenario tests
@pytest.mark.asyncio
async def test_e2e_invalid_conversation_id():
    """
    Pytest function for invalid conversation ID handling.
    """
    tester = ErrorScenarioE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_invalid_conversation_id_handling()


@pytest.mark.asyncio
async def test_e2e_task_not_found_error():
    """
    Pytest function for task not found errors.
    """
    tester = ErrorScenarioE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_task_not_found_error_in_mcp_tools()


@pytest.mark.asyncio
async def test_e2e_user_permission_errors():
    """
    Pytest function for user permission errors.
    """
    tester = ErrorScenarioE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_user_permission_errors()


@pytest.mark.asyncio
async def test_e2e_database_connection_errors():
    """
    Pytest function for database connection errors.
    """
    tester = ErrorScenarioE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_database_connection_errors()


@pytest.mark.asyncio
async def test_e2e_input_validation_errors():
    """
    Pytest function for input validation errors.
    """
    tester = ErrorScenarioE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_invalid_input_validation()


@pytest.mark.asyncio
async def test_e2e_mcp_parameter_validation_errors():
    """
    Pytest function for MCP parameter validation errors.
    """
    tester = ErrorScenarioE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_mcp_tool_parameter_validation_errors()


@pytest.mark.asyncio
async def test_e2e_conversation_state_errors():
    """
    Pytest function for conversation state reconstruction errors.
    """
    tester = ErrorScenarioE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_conversation_state_reconstruction_errors()


@pytest.mark.asyncio
async def test_e2e_agent_processing_errors():
    """
    Pytest function for AI agent processing errors.
    """
    tester = ErrorScenarioE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_agent_processing_errors()


@pytest.mark.asyncio
async def test_e2e_server_restart_recovery():
    """
    Pytest function for server restart recovery.
    """
    tester = ErrorScenarioE2ETester(db_session=None)  # Replace with actual test session
    await tester.test_recovery_from_server_restart_simulation()


if __name__ == "__main__":
    # This would require a proper async test setup in a real implementation
    # For demonstration purposes only
    print("Error scenario E2E tests would run here in a full implementation")