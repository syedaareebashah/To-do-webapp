# How to Test the Chatbot with Task Operations

## 1. Make Sure the Backend is Running
- Start the backend with: `uvicorn src.app.main:app --host 0.0.0.0 --port 8001 --reload`
- Verify it's running by visiting: http://localhost:8001/health

## 2. Set Up Authentication
- The backend requires authentication for the chat endpoint
- You'll need to implement the authentication flow in your frontend
- Or use an API client that can handle authentication headers

## 3. Example API Calls (once authenticated)

### Add a task
- **Method**: POST
- **Endpoint**: `/api/{user_id}/chat`
- **Body**: `{"message": "Add a task to buy groceries"}`
- **Expected**: Will trigger add_task MCP tool and respond appropriately

### List tasks
- **Method**: POST
- **Endpoint**: `/api/{user_id}/chat`
- **Body**: `{"message": "What tasks do I have?"}`
- **Expected**: Will trigger list_tasks MCP tool and show your tasks

### Complete a task
- **Method**: POST
- **Endpoint**: `/api/{user_id}/chat`
- **Body**: `{"message": "Complete the task to buy groceries"}`
- **Expected**: Will trigger complete_task MCP tool

### Delete a task
- **Method**: POST
- **Endpoint**: `/api/{user_id}/chat`
- **Body**: `{"message": "Delete the task to call mom"}`
- **Expected**: Will trigger delete_task MCP tool

## 4. Using with Frontend Application
- Your frontend needs to handle authentication with the backend
- Pass the authenticated user ID in the API call
- The backend will process natural language and execute appropriate MCP tools
- Responses will include both the chat response and tool execution results

## 5. Verification That Task Operations Work
- ✅ Direct MCP tool calls work perfectly
- ✅ TodoAgent can process messages and trigger task operations
- ✅ All task operations (add, list, complete, delete) are functional
- ✅ Database integration is working properly
- ✅ Backend authentication is working as designed

## 6. Troubleshooting
- If tasks aren't being created/listed/completed/deleted:
  - Make sure the database is initialized: `python -c "from src.database.session import init_db; init_db()"`
  - Verify the backend is running on port 8001
  - Check that authentication is properly implemented in your frontend
  - Ensure user IDs are valid UUIDs in your requests

## Summary
The chatbot backend is now fully functional for task operations! Once you implement proper authentication in your frontend, all task operations will work as expected.