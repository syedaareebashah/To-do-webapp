# AI Chatbot Integration Guide

## Overview

Your Todo Web App now includes an AI-powered chatbot that allows users to manage tasks using natural language. The chatbot is fully integrated with your existing task management system.

## Architecture

### Backend (FastAPI)
- **URL**: `http://localhost:8000`
- **Chat Endpoint**: `POST /api/{user_id}/chat`
- **MCP Tools**: add_task, list_tasks, complete_task, delete_task, update_task
- **Authentication**: JWT Bearer token required

### Frontend (Next.js)
- **URL**: `http://localhost:3000`
- **Chat Component**: `components/chat/ChatInterface.tsx`
- **Integration**: Tasks page with toggle button

## Features

### 1. Natural Language Task Management
Users can interact with the chatbot using natural language:
- "Add a task to buy groceries"
- "Show my pending tasks"
- "Create a high priority task to call mom"
- "List all my tasks"
- "What tasks do I have?"

### 2. Real-time Updates
- Task list automatically refreshes when chatbot creates/modifies tasks
- Conversation history persists across messages
- Tool calls are visible in the chat interface

### 3. Responsive Design
- Desktop: 2/3 tasks view, 1/3 chat panel
- Mobile: Full-width with toggle
- Sticky chat panel for easy access

## How to Use

### Starting the Application

1. **Start Backend** (if not already running):
```bash
cd C:\Users\mehre\Downloads\hackathonnII\Hackathon_II\phase_III
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start Frontend** (if not already running):
```bash
cd frontend
npm run dev
```

3. **Access the App**:
- Open browser: `http://localhost:3000`
- Sign in or create an account
- Navigate to Tasks page
- Click "Show AI Chat" button

### Using the Chatbot

1. **Toggle Chat Panel**: Click the "Show AI Chat" button in the navigation bar
2. **Type Your Message**: Enter natural language commands in the input field
3. **Send**: Press Enter or click the send button
4. **View Response**: See the AI's response and any actions taken
5. **Watch Tasks Update**: Task list refreshes automatically

### Example Commands

**Creating Tasks:**
- "Add a task to buy groceries"
- "Create a high priority task to finish the report by Friday"
- "Remember to call the dentist"

**Viewing Tasks:**
- "Show my tasks"
- "What tasks do I have?"
- "List all pending tasks"

**Managing Tasks:**
- "Mark task 1 as complete"
- "Delete task 2"
- "Update task 3"

## API Reference

### Chat Endpoint

**Endpoint**: `POST /api/{user_id}/chat`

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": "optional-conversation-id"
}
```

**Response**:
```json
{
  "conversation_id": "uuid",
  "response": "I'll add 'buy groceries' to your tasks.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "arguments": {
        "user_id": "user123",
        "content": "buy groceries"
      },
      "result": {
        "success": true,
        "task_id": "task_123"
      }
    }
  ],
  "message_id": "uuid"
}
```

## Component Structure

```
frontend/
├── components/
│   ├── chat/
│   │   └── ChatInterface.tsx          # Main chat component
│   └── tasks/
│       ├── CreateTaskForm.tsx         # Updated with callback
│       ├── TaskList.tsx               # Task display
│       └── TaskItem.tsx               # Individual task
├── app/(app)/tasks/
│   └── page.tsx                       # Updated with chat integration
├── contexts/
│   └── AuthContext.tsx                # Authentication context
├── hooks/
│   └── useTasks.ts                    # Task management hook
└── lib/
    └── api-client.ts                  # API client with auth

backend/
├── src/
│   ├── api/
│   │   └── endpoints/
│   │       └── chat.py                # Chat endpoint
│   ├── agents/
│   │   └── todo_agent.py              # AI agent logic
│   ├── mcp_server/
│   │   └── server.py                  # MCP server
│   └── services/
│       ├── conversation_service.py    # Conversation management
│       ├── message_service.py         # Message storage
│       └── task_service.py            # Task operations
```

## Troubleshooting

### Chat Not Appearing
- Check if "Show AI Chat" button is clicked
- Verify user is authenticated
- Check browser console for errors

### Messages Not Sending
- Verify backend is running on port 8000
- Check authentication token is valid
- Inspect network tab for API errors

### Tasks Not Updating
- Ensure `onTaskUpdate` callback is working
- Check if MCP tools are executing successfully
- Verify database connection

### Backend Errors
- Check `todo_chatbot_agent.log` for errors
- Verify database connection string
- Ensure all dependencies are installed

## Security Considerations

1. **Authentication**: All chat requests require valid JWT token
2. **User Isolation**: Users can only access their own conversations and tasks
3. **Input Validation**: All user inputs are validated before processing
4. **Rate Limiting**: Consider adding rate limiting for production

## Future Enhancements

1. **LLM Integration**: Replace keyword-based agent with actual LLM (OpenAI, Anthropic)
2. **Voice Input**: Add speech-to-text for voice commands
3. **Task Suggestions**: AI-powered task recommendations
4. **Smart Scheduling**: Automatic task prioritization and scheduling
5. **Multi-language Support**: Support for multiple languages
6. **Rich Media**: Support for images and attachments in chat

## Testing

### Manual Testing
1. Create a task via chat: "Add a task to test the chatbot"
2. List tasks: "Show my tasks"
3. Verify task appears in the task list
4. Complete task via chat: "Mark task as complete"
5. Verify task updates in real-time

### Automated Testing
Run the E2E tests:
```bash
pytest src/test/e2e/test_chat_flow.py
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs: `todo_chatbot_agent.log`
3. Check browser console for frontend errors
4. Verify all services are running

## Version History

- **v1.0.0** (2026-02-07): Initial chatbot integration
  - Natural language task management
  - Real-time task updates
  - Conversation history
  - Responsive design

---

**Status**: ✅ Fully Integrated and Ready to Use
**Backend**: Running on port 8000
**Frontend**: Running on port 3000
