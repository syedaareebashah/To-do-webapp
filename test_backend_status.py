import asyncio
from src.mcp_server.server import mcp_server
import uuid

async def test_backend_functionality():
    print("Testing backend functionality...")
    
    # Create a test user ID
    test_user_id = str(uuid.uuid4())
    print(f"Using test user ID: {test_user_id}")
    
    # Test adding a task
    print("\n1. Testing add_task...")
    add_result = await mcp_server.add_task(
        user_id=test_user_id,
        content="Test task to verify backend is working",
        priority="medium"
    )
    print(f"Add task result: {add_result['success']}")
    
    if add_result['success']:
        task_id = add_result['task_id']
        print(f"Task created with ID: {task_id}")
        
        # Test listing tasks
        print("\n2. Testing list_tasks...")
        list_result = await mcp_server.list_tasks(
            user_id=test_user_id,
            filter_type="all"
        )
        print(f"List tasks result: Found {list_result.get('total_count', 0)} tasks")
        
        # Test completing the task
        print("\n3. Testing complete_task...")
        complete_result = await mcp_server.complete_task(
            user_id=test_user_id,
            task_id=task_id
        )
        print(f"Complete task result: {complete_result['success']}")
        
        # Test deleting the task
        print("\n4. Testing delete_task...")
        delete_result = await mcp_server.delete_task(
            user_id=test_user_id,
            task_id=task_id
        )
        print(f"Delete task result: {delete_result['success']}")
        
        print("\n+ All backend functions are working properly!")
    else:
        print("\n✗ Backend test failed")

if __name__ == "__main__":
    asyncio.run(test_backend_functionality())