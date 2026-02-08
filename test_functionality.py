"""
Test script to verify the chat endpoint works with task operations using mock authentication
"""

import asyncio
from unittest.mock import patch, MagicMock
from src.api.endpoints.chat import chat_endpoint
from src.models.message import MessageCreate
from src.database.session import get_session
from sqlmodel import create_engine
from sqlmodel import Session as SQLModelSession
import uuid


async def test_chat_with_mock_auth():
    # Create a test user ID
    test_user_id = str(uuid.uuid4())
    print(f"Using test user ID: {test_user_id}")
    
    # Create a message to add a task
    message_data = MessageCreate(content="Add a task to buy groceries")
    
    # Create a database session
    DATABASE_URL = "sqlite:///./test_todo_chatbot.db"  # Using SQLite for testing
    engine = create_engine(DATABASE_URL)
    
    with SQLModelSession(engine) as db:
        # Mock the current_user dependency
        current_user = {"id": test_user_id}
        
        try:
            # Call the chat endpoint with mocked authentication
            result = await chat_endpoint(
                user_id=test_user_id,
                message_data=message_data,
                db=db,
                current_user=current_user
            )
            
            print("Chat endpoint response:")
            print(f"- Conversation ID: {result['conversation_id']}")
            print(f"- Response: {result['response']}")
            print(f"- Tool calls: {result['tool_calls']}")
            
            # Check if any tool calls were made
            if result['tool_calls']:
                print("\nTool calls executed:")
                for tool_call in result['tool_calls']:
                    print(f"- Tool: {tool_call['tool_name']}")
                    print(f"  Arguments: {tool_call['arguments']}")
                    print(f"  Result: {tool_call['result']}")
            else:
                print("\nNo tool calls were executed")
                
        except Exception as e:
            print(f"Error calling chat endpoint: {e}")
            import traceback
            traceback.print_exc()


def test_direct_mcp_calls():
    """Test MCP tools directly without going through the chat endpoint"""
    print("\n" + "="*50)
    print("TESTING MCP TOOLS DIRECTLY")
    print("="*50)
    
    import asyncio
    from src.mcp_server.server import mcp_server
    import uuid
    
    # Create a test user ID
    test_user_id = str(uuid.uuid4())
    print(f"Using test user ID: {test_user_id}")
    
    async def run_tests():
        # Test adding a task
        print("\n1. Testing add_task...")
        add_result = await mcp_server.add_task(
            user_id=test_user_id,
            content="Test task for verification",
            priority="medium"
        )
        print(f"Add task result: {add_result}")
        
        task_id = None
        if add_result.get("success"):
            task_id = add_result.get("task_id")
            print(f"Created task with ID: {task_id}")
        else:
            print("Failed to create task")
            return
        
        # Test listing tasks
        print("\n2. Testing list_tasks...")
        list_result = await mcp_server.list_tasks(
            user_id=test_user_id,
            filter_type="all"
        )
        print(f"List tasks result: {list_result}")
        
        # Test completing a task
        print("\n3. Testing complete_task...")
        if task_id:
            complete_result = await mcp_server.complete_task(
                user_id=test_user_id,
                task_id=task_id
            )
            print(f"Complete task result: {complete_result}")
        
        # Test listing tasks again to see the change
        print("\n4. Testing list_tasks after completion...")
        list_result_after = await mcp_server.list_tasks(
            user_id=test_user_id,
            filter_type="all"
        )
        print(f"List tasks result after completion: {list_result_after}")
        
        # Test deleting a task
        print("\n5. Testing delete_task...")
        if task_id:
            delete_result = await mcp_server.delete_task(
                user_id=test_user_id,
                task_id=task_id
            )
            print(f"Delete task result: {delete_result}")
    
    # Run the async tests
    asyncio.run(run_tests())


if __name__ == "__main__":
    print("Testing MCP tools directly (this should work)...")
    test_direct_mcp_calls()
    
    print("\nNote: The chat endpoint requires proper authentication.")
    print("Direct MCP tool calls work without authentication.")