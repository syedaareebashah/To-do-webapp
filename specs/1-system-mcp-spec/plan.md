# Todo AI Chatbot — System & MCP Implementation Plan (Spec 2)

## Technical Context

This implementation plan describes the architecture and design for a stateless backend system and MCP server that enables an AI agent to manage todo tasks through standardized MCP tools while persisting all state in a database.

**Architecture Type:** Stateless backend with MCP server integration
**Technology Stack:** Python FastAPI, Official MCP SDK, SQLModel, Neon PostgreSQL
**Runtime Environment:** Cloud-based AI service
**Data Storage:** Neon PostgreSQL database for all persistent data

### System Boundaries

**In Scope:**
- FastAPI backend with stateless chat endpoint
- MCP server for task operations
- Database models for tasks, conversations, and messages
- Authentication and user scoping
- MCP tool contracts and validation
- Conversation state reconstruction

**Out of Scope:**
- AI agent reasoning and intent interpretation logic
- Frontend interfaces or user interfaces
- External service integrations beyond MCP tools
- Real-time WebSocket connections (HTTP requests only)

### Dependencies

- Official MCP SDK
- Python FastAPI framework
- SQLModel for database operations
- Neon PostgreSQL database
- Better Auth for user authentication
- Claude Code for AI agent integration

### Constraints

- All database access must be performed via SQLModel
- Every task must be scoped by user_id
- Every message must be linked to a conversation_id
- Message roles must be explicitly stored as user or assistant
- Timestamps must be recorded for all persistent entities
- Server must hold zero runtime state between requests
- MCP tools must be stateless and persist all state in the database
- API responses must follow the defined request/response schema

## Constitution Check

### Alignment with Constitution Principles

#### Stateless System Design (Section: Core Principles)
- ✅ **Aligned**: System will maintain no in-memory state across requests, all state stored in database
- **Implementation**: Server holds zero runtime state between requests, all conversation history fetched from database

#### Tool-Based Interaction (Section: Core Principles)
- ✅ **Aligned**: AI agent will interact with system exclusively via MCP tools
- **Implementation**: All task operations exposed as MCP tools only, no direct database access

#### Clear Separation of Concerns (Section: Core Principles)
- ✅ **Aligned**: Clear boundaries between API, MCP server, and database layers
- **Implementation**: API layer handles HTTP requests, MCP server handles task logic, database stores data

#### Deterministic Behavior (Section: Core Principles)
- ✅ **Aligned**: System will produce same outputs for identical inputs
- **Implementation**: Stateless design ensures consistent behavior regardless of server state

#### Reliability and Data Integrity (Section: Core Principles)
- ✅ **Aligned**: System maintains data integrity and reliable access to persistent data
- **Implementation**: Atomic transactions and proper user isolation by user_id

### Constraint Verification

#### Technology Constraints (Section: Constraints)
- ✅ **Python FastAPI**: Will use FastAPI framework for backend implementation
- ✅ **MCP SDK Only**: MCP server will use Official MCP SDK exclusively
- ✅ **SQLModel ORM**: All database access will use SQLModel
- ✅ **Neon PostgreSQL**: Database will be Neon PostgreSQL

#### Architecture Constraints (Section: Constraints)
- ✅ **Single Chat Endpoint**: POST /api/{user_id}/chat will be the single endpoint
- ✅ **Stateless Design**: Server will hold zero runtime state between requests
- ✅ **MCP as Sole Interface**: MCP server will be the sole interface for task operations
- ✅ **Database as Source of Truth**: Database will be single source of truth

## Research & Unknowns

### Current Unknowns (NEEDS CLARIFICATION)

*All unknowns have been resolved through research.*

## Gate Evaluations

### Feasibility Gate ✅ PASSED
- MCP SDK is available and compatible with Python
- FastAPI framework is compatible with MCP SDK
- SQLModel works with Neon PostgreSQL
- Architecture aligns with existing system constraints

### Technical Gate ✅ PASSED
- All required technologies are available
- No technical conflicts with existing architecture
- Implementation approach is technically sound

### Compliance Gate ✅ PASSED
- MCP SDK implementation patterns clarified through research
- Better Auth integration approach defined
- Database connection management best practices established

## Phase 0: Research & Resolution

### Research Findings

#### Decision: MCP SDK Implementation Patterns
**Rationale:** Use the Official MCP SDK's recommended patterns for Python integration, following their documentation and examples for creating MCP tools and server setup.
**Alternatives considered:**
- Custom MCP protocol implementation (too complex and error-prone)
- Third-party MCP libraries (may not be compatible with official specification)
- Simplified tool wrappers (may miss important functionality)

#### Decision: Better Auth Integration
**Rationale:** Integrate Better Auth at the FastAPI middleware level to validate user authentication before requests reach the chat endpoint, ensuring user identity is available throughout the request lifecycle.
**Alternatives considered:**
- JWT token validation in each endpoint (repetitive and error-prone)
- Client-side authentication only (insecure approach)
- Custom authentication system (redundant when Better Auth is available)

#### Decision: Database Connection Management
**Rationale:** Use FastAPI's dependency system with SQLModel's async session management to handle database connections efficiently, with proper connection pooling and cleanup.
**Alternatives considered:**
- Global database connection (not scalable and risky)
- Connection per operation (inefficient and slow)
- Manual connection management (error-prone and complex)

## Phase 1: Design & Architecture

### System Architecture

```
Client Request
      ↓
FastAPI Router
      ↓
Better Auth Middleware (Validate user_id)
      ↓
Chat Endpoint Handler
      ↓
Database Service Layer
      ↓
SQLModel Async Sessions
      ↓
Neon PostgreSQL
      ↓
MCP Server
      ↓
MCP Tools (add_task, list_tasks, complete_task, delete_task, update_task)
```

### Component Responsibilities

#### FastAPI Backend
- Handle HTTP requests/responses
- Validate authentication via Better Auth
- Route requests to appropriate handlers
- Serialize/deserialize data

#### Chat Endpoint Handler
- Fetch conversation history from database
- Store incoming user message
- Execute AI agent with MCP tools
- Store assistant response
- Return response with tool call metadata

#### MCP Server
- Implement Official MCP SDK
- Expose task operations as MCP tools
- Validate inputs and enforce user isolation
- Persist state changes to database

#### Database Service Layer
- Manage SQLModel entities
- Handle CRUD operations for tasks, conversations, messages
- Ensure data integrity and user isolation
- Provide efficient querying capabilities

### Database Models

#### Task Model
- Fields: id, user_id, content, status, due_date, priority, created_at, completed_at
- Relationships: Belongs to a single user
- Constraints: Foreign key to user_id, non-null content

#### Conversation Model
- Fields: id, user_id, created_at, updated_at
- Relationships: Contains multiple messages
- Constraints: Foreign key to user_id

#### Message Model
- Fields: id, conversation_id, role, content, timestamp
- Relationships: Belongs to a single conversation
- Constraints: Foreign key to conversation_id, role must be 'user' or 'assistant'

## Phase 2: Implementation Architecture

### API Layer Design

#### Single Chat Endpoint
```
POST /api/{user_id}/chat
```

**Request Body:**
```json
{
  "message": "string",
  "conversation_id": "string (optional)"
}
```

**Response Body:**
```json
{
  "response": "string",
  "conversation_id": "string",
  "tool_calls": [
    {
      "tool_name": "string",
      "parameters": "object",
      "result": "object"
    }
  ]
}
```

### MCP Server Design

#### MCP Tools Implementation
- **add_task**: Creates new tasks with user_id scoping
- **list_tasks**: Retrieves tasks for specific user_id
- **complete_task**: Updates task status for specific user's task
- **delete_task**: Removes specific user's task
- **update_task**: Modifies specific user's task

### State Management

#### Stateless Request Lifecycle
1. Request received with user_id and message
2. Authenticate user via Better Auth
3. Fetch conversation history from database
4. Store incoming user message in database
5. Execute AI agent with available MCP tools
6. Capture MCP tool calls and results
7. Store assistant response in database
8. Return response with conversation_id and tool call metadata

### Security Implementation

#### User Isolation
- All queries filtered by user_id
- MCP tools validate user permissions before operations
- Database constraints enforce user_id relationships
- Authentication validated at API gateway level

## Implementation Approach

### Iteration 1: Core Infrastructure
- Set up FastAPI project structure
- Configure database with SQLModel
- Implement basic authentication middleware
- Create database models

### Iteration 2: MCP Server Integration
- Install and configure Official MCP SDK
- Implement basic MCP tools
- Connect MCP tools to database operations
- Test tool functionality

### Iteration 3: Chat Endpoint Implementation
- Implement stateless chat endpoint
- Add conversation history loading
- Integrate AI agent with MCP tools
- Add response and tool call metadata

### Iteration 4: Testing and Validation
- End-to-end testing of all scenarios
- Stress testing for multiple concurrent users
- Server restart recovery testing
- Performance optimization

## Success Validation Criteria

### Functional Validation
- Chat endpoint correctly reconstructs conversation history from database
- MCP tools properly create, list, update, complete, and delete tasks
- All data is properly isolated by user_id
- System resumes conversations correctly after server restart

### Quality Validation
- Responses are reproducible given identical inputs
- System behavior aligns with written specification
- Error handling works gracefully without data corruption
- Authentication and user isolation are properly enforced

### Performance Validation
- Response time under 2 seconds for typical chat requests
- Database operations complete efficiently
- MCP tool calls execute without blocking
- System handles concurrent users appropriately

## Risk Assessment

### High-Risk Areas
- MCP SDK integration complexity with Python
- Database connection management under load
- User authentication and session management
- Conversation state reconstruction accuracy

### Mitigation Strategies
- Extensive testing with MCP SDK examples
- Proper connection pooling and async session management
- Clear authentication middleware design
- Robust error handling for missing conversation data