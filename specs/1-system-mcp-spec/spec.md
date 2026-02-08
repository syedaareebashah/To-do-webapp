# Todo AI Chatbot — System & MCP Specification (Spec 2)

## Overview

This specification defines the backend system architecture, MCP server behavior, API contracts, database models, and stateless request execution for an AI-powered todo chatbot. The system provides a stateless chat endpoint that reconstructs conversation history from the database on each request and exposes task operations through MCP tools.

**Target Audience:** Claude Code (AI code generation agent) responsible for implementing the backend system, MCP server, database persistence, and stateless chat API.

**Focus:** Backend architecture, MCP server behavior, API contracts, database models, and stateless request execution for an AI-powered todo chatbot.

## User Scenarios & Testing

### Primary User Scenario
As a user of the todo chatbot, I want to interact with the system through a single chat endpoint where my conversation history is automatically reconstructed from the database, allowing me to continue my conversation seamlessly even after server restarts. When I issue task commands (add, list, complete, update, delete), they are processed through MCP tools and the results are persisted to the database.

### Secondary User Scenarios
- **Server Restart Recovery:** When the server restarts, I can continue my conversation from where I left off without losing context.
- **Task Management:** When I request to create, list, complete, update, or delete tasks, the system correctly processes my requests through MCP tools and persists the changes.
- **Concurrent Users:** Multiple users can simultaneously interact with the system without interfering with each other's data.

### Acceptance Scenarios
1. Given a user sends a chat request to POST /api/{user_id}/chat, when the system processes the request, then it should fetch conversation history from the database, store the user message, execute the AI agent with MCP tools, store the assistant response, and return the response with tool call metadata.
2. Given a user requests to create a task, when the MCP tool processes the request, then it should persist the task in the database with the correct user_id and return a success response.
3. Given a user requests to list tasks, when the MCP tool processes the request, then it should retrieve tasks for the correct user_id and return them in a structured format.
4. Given the server restarts, when a user continues their conversation, then the system should reconstruct the conversation history from the database and continue normally.

## Functional Requirements

### FR-1: Stateless Chat Endpoint
The system MUST expose a single stateless chat endpoint at POST /api/{user_id}/chat that reconstructs conversation state from the database on every request.

- The endpoint MUST accept user messages and return AI-generated responses
- The endpoint MUST fetch conversation history from the database before processing
- The endpoint MUST store incoming user messages in the database
- The endpoint MUST execute the AI agent with MCP tools
- The endpoint MUST store assistant responses in the database
- The endpoint MUST return response and tool call metadata to the client

### FR-2: MCP Server Integration
The system MUST expose all task operations as MCP tools using the Official MCP SDK.

- The system MUST implement add_task, list_tasks, complete_task, delete_task, and update_task tools
- MCP tools MUST be stateless and persist all state in the database
- MCP tools MUST validate required parameters before processing
- MCP tools MUST return structured, predictable responses
- MCP tools MUST scope all operations by user_id for proper isolation

### FR-3: Database Persistence
The system MUST persist all task and conversation data in Neon PostgreSQL.

- All tasks MUST be stored with proper user_id scoping
- All conversation messages MUST be stored with conversation_id linking
- Message roles MUST be explicitly stored as user or assistant
- Timestamps MUST be recorded for all persistent entities
- All operations MUST be atomic and maintain data integrity

### FR-4: Conversation State Reconstruction
The system MUST reconstruct conversation state from the database on every request.

- The system MUST fetch all previous messages for the user's conversation
- The system MUST properly order messages by timestamp
- The system MUST handle missing or corrupted conversation data gracefully
- The system MUST maintain conversation context across server restarts

### FR-5: User Isolation
The system MUST ensure proper isolation between different users' data.

- All queries MUST be scoped by user_id
- Users MUST NOT be able to access other users' tasks or conversations
- MCP tools MUST validate user permissions before operations
- Database constraints MUST enforce user_id relationships

### FR-6: Tool Call Observability
The system MUST make MCP tool calls observable and return them in API responses.

- The system MUST track which MCP tools are called during chat processing
- Tool call metadata MUST be included in API responses
- Tool execution results MUST be logged for debugging purposes
- Failed tool calls MUST be reported appropriately to the client

### FR-7: System Reliability
The system MUST maintain reliability and data integrity under normal operating conditions.

- All database transactions MUST be atomic
- The system MUST handle errors gracefully without data corruption
- Backup and recovery procedures MUST be supported
- The system MUST maintain consistent behavior after restarts

## Success Criteria

### Quantitative Metrics
- 99.9% uptime for the chat endpoint under normal load
- Under 2-second response time for typical chat requests
- 100% of user data properly isolated by user_id
- 100% of conversation history correctly reconstructed after server restart
- 95% of MCP tool calls complete successfully

### Qualitative Measures
- Users can seamlessly continue conversations after server restarts
- Task operations (create, list, update, complete, delete) work reliably
- No data leakage occurs between different users
- System behavior is consistent and predictable
- Error conditions are handled gracefully with appropriate user feedback

## Key Entities

### Task
Represents a user's task in the todo system.
- Fields: id, user_id, content, status, due_date, priority, created_at, completed_at
- Relationships: Belongs to a single user
- Constraints: Foreign key to user_id, non-null content

### Conversation
Represents a conversation thread between user and assistant.
- Fields: id, user_id, created_at, updated_at
- Relationships: Contains multiple messages
- Constraints: Foreign key to user_id

### Message
Represents a single message in a conversation.
- Fields: id, conversation_id, role, content, timestamp
- Relationships: Belongs to a single conversation
- Constraints: Foreign key to conversation_id, role must be 'user' or 'assistant'

### User
Represents a system user.
- Fields: id, username, email, created_at
- Relationships: Owns multiple tasks and conversations
- Constraints: Unique username and email

## Constraints

### Technical Constraints
- Backend framework MUST be implemented using Python FastAPI
- MCP server MUST use the Official MCP SDK only
- All database access MUST be performed via SQLModel
- Database MUST be Neon PostgreSQL
- All task operations MUST be exposed exclusively as MCP tools
- MCP tools MUST be stateless and persist all state in the database
- Server MUST hold zero runtime state between requests

### Architecture Constraints
- Single chat endpoint: POST /api/{user_id}/chat
- Chat endpoint MUST fetch conversation history from the database
- Chat endpoint MUST store incoming user messages
- Chat endpoint MUST execute the AI agent with MCP tools
- Chat endpoint MUST store assistant responses
- Chat endpoint MUST return response and tool call metadata
- MCP server MUST act as the sole interface for task CRUD operations
- Database MUST be the single source of truth for tasks and conversations

### Security Constraints
- All data MUST be properly isolated by user_id
- MCP tools MUST validate user permissions before operations
- Input validation MUST prevent injection attacks
- Authentication MUST be validated for all operations

## Assumptions

- Neon PostgreSQL database is available and properly configured
- Official MCP SDK is installed and accessible
- FastAPI framework is properly set up with necessary dependencies
- User authentication is handled at the API gateway level
- Network connectivity is stable between components
- Server resources are adequate for expected load

## Dependencies

- Python FastAPI framework for backend API
- Official MCP SDK for MCP server functionality
- SQLModel for database ORM operations
- Neon PostgreSQL database for data persistence
- AI agent framework for chat processing
- Authentication service for user validation