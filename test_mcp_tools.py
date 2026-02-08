"""
Test script to verify MCP tools are working properly
"""

import asyncio
from src.mcp_server.server import mcp_server


async def test_mcp_tools():
    print("Testing MCP tools...")
    
    import uuid
    
    # Create a proper UUID for testing
    test_user_uuid = uuid.uuid4()
    print(f"Using test user UUID: {test_user_uuid}")
    
    # Test adding a task
    print("\n1. Testing add_task...")
    add_result = await mcp_server.add_task(
        user_id=str(test_user_uuid),
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
        user_id=str(test_user_uuid),
        filter_type="all"
    )
    print(f"List tasks result: {list_result}")
    
    # Test completing a task
    print("\n3. Testing complete_task...")
    if task_id:
        complete_result = await mcp_server.complete_task(
            user_id=str(test_user_uuid),
            task_id=task_id
        )
        print(f"Complete task result: {complete_result}")
    
    # Test listing tasks again to see the change
    print("\n4. Testing list_tasks after completion...")
    list_result_after = await mcp_server.list_tasks(
        user_id=str(test_user_uuid),
        filter_type="all"
    )
    print(f"List tasks result after completion: {list_result_after}")
    
    # Test deleting a task
    print("\n5. Testing delete_task...")
    if task_id:
        delete_result = await mcp_server.delete_task(
            user_id=str(test_user_uuid),
            task_id=task_id
        )
        print(f"Delete task result: {delete_result}")


if __name__ == "__main__":
    asyncio.run(test_mcp_tools())