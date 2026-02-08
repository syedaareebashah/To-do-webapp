<!--
Sync Impact Report:
- Version change: 2.0.0 → 3.0.0
- Modified principles: Replaced AI agent behavior principles with system architecture and MCP principles
- Added sections: System architecture principles, MCP server behavior, API contracts, Data integrity
- Removed sections: Previous AI agent behavior principles (Intent-First, Tool-First, etc.)
- Templates requiring updates: ⚠ pending (templates need review for system-specific changes)
- Follow-up TODOs: Update plan-template.md, spec-template.md, tasks-template.md for system-specific constraints
-->

# Project Constitution

**Project Name:** Todo AI Chatbot — System & MCP Specification (Spec 2)

**Version:** 3.0.0
**Ratification Date:** 2026-02-06
**Last Amended Date:** 2026-02-06

---

## Purpose

This constitution establishes the foundational principles, standards, and constraints for the backend system architecture, MCP server behavior, API contracts, data persistence, and stateless execution model in the Todo AI Chatbot project. It serves as the authoritative reference for all system operations and ensures consistency in how the system handles task management and conversation state.

---

## Core Principles

### Principle 1: Stateless System Design

**Statement:** The system MUST maintain no in-memory state across requests. All persistent state MUST be stored in the database and retrieved as needed for each operation.

**Rationale:** Stateless design ensures reliability, scalability, and consistency across deployments. It prevents data loss from server restarts and ensures that the system behaves predictably regardless of server state.

**Requirements:**
- Server MUST hold zero runtime state between requests
- All conversation history MUST be fetched from the database for each request
- All task state MUST be persisted in the database
- Session data MUST be stored externally or in the database
- System MUST be able to recover state completely after restart

### Principle 2: Tool-Based Interaction

**Statement:** The AI agent MUST interact with the system exclusively via MCP tools. Direct database access or bypassing tools is strictly prohibited for task operations.

**Rationale:** MCP tools provide standardized interfaces, logging, validation, and safety checks that direct operations cannot guarantee. This principle ensures consistency, auditability, and safety in all operations.

**Requirements:**
- ALL task operations MUST use MCP tools only (no direct database access)
- MCP server MUST act as the sole interface for task CRUD operations
- Direct database access is forbidden during task execution
- Tool usage MUST follow defined patterns and interfaces
- Tool failures MUST be handled gracefully with proper error propagation

### Principle 3: Clear Separation of Concerns

**Statement:** The system MUST maintain clear boundaries between API layer, MCP server, and database layer. Each component MUST have distinct responsibilities.

**Rationale:** Separation of concerns enables independent development, testing, and scaling of system components. It also improves maintainability and makes the system easier to reason about.

**Requirements:**
- API layer handles HTTP requests/responses and authentication
- MCP server handles task management logic and business rules
- Database layer stores all persistent data
- Each layer communicates only through well-defined interfaces
- No direct dependencies between distant layers

### Principle 4: Deterministic Behavior

**Statement:** The system MUST produce the same outputs for identical inputs regardless of when or how many times the operation is performed.

**Rationale:** Deterministic behavior ensures reliability and makes the system predictable for both users and developers. It also simplifies testing and debugging.

**Requirements:**
- Same inputs MUST produce the same outputs consistently
- System behavior MUST be reproducible given identical conditions
- Timestamps MUST be recorded consistently
- No random or time-dependent behavior in core operations
- Error handling MUST be consistent across all operations

### Principle 5: Reliability and Data Integrity

**Statement:** The system MUST maintain data integrity and provide reliable access to persistent data. All operations MUST be atomic and consistent.

**Rationale:** Data integrity is fundamental to user trust and system reliability. Users need assurance that their tasks and conversations are safely stored and accessible.

**Requirements:**
- All database transactions MUST be atomic
- Every task MUST be scoped by user_id
- Every message MUST be linked to a conversation_id
- Data consistency MUST be maintained across all operations
- Backup and recovery procedures MUST be in place

---

## Technology Standards

### Backend Architecture

- **Framework:** Python FastAPI (as specified in project)
- **Database:** SQLModel for all database operations
- **MCP Server:** Official MCP SDK only
- **API Layer:** RESTful endpoints with proper HTTP semantics
- **Authentication:** Per-user scoping with user_id

### API Design

- **Single Endpoint:** POST /api/{user_id}/chat for all chat operations
- **Request/Response:** Strictly follow defined schemas
- **Error Handling:** Consistent error response format
- **Rate Limiting:** Proper throttling mechanisms
- **Logging:** Comprehensive request/response logging

### MCP Server Implementation

- **SDK:** Official MCP SDK only (no custom implementations)
- **Tools:** Expose task operations as MCP tools only
- **State:** MCP tools must be stateless (persist in database)
- **Validation:** All inputs must be validated
- **Security:** User isolation through user_id scoping

### Database Design

- **ORM:** SQLModel for all database access
- **Entities:** Tasks, Conversations, Messages with proper relationships
- **Indexing:** Proper indexes for performance
- **Constraints:** Foreign key and uniqueness constraints
- **Migration:** Proper schema evolution support

---

## Quality Requirements

### System Behavior Standards

- API responses MUST strictly follow the defined request/response schema
- MCP tools MUST validate required parameters before processing
- Error handling MUST be consistent across all operations
- Response times MUST be reasonable (under 2 seconds for typical operations)
- Tool contract enforcement MUST be strict and predictable

### Data Integrity Requirements

- All database access MUST be performed via SQLModel
- Every task MUST be scoped by user_id with foreign key constraints
- Every message MUST be linked to a conversation_id with foreign key constraints
- Message roles MUST be explicitly stored as user or assistant
- Timestamps MUST be recorded for all persistent entities with timezone awareness

### API Quality Requirements

- All endpoints MUST follow RESTful principles
- HTTP status codes MUST be semantically correct
- Request/response bodies MUST follow defined schemas
- Authentication MUST be validated for all requests
- Rate limiting MUST be implemented to prevent abuse

### MCP Tool Quality Requirements

- MCP tool names, parameters, and return values MUST match the specification exactly
- Tools MUST validate required parameters before processing
- Tools MUST return structured, predictable responses
- Tools MUST handle errors gracefully with appropriate messages
- Tool execution MUST be atomic and consistent

### Security Requirements

- User data MUST be isolated by user_id
- Authentication MUST be validated for all operations
- Input validation MUST prevent injection attacks
- No sensitive data MUST be logged
- MCP tools MUST validate user permissions before operations

---

## Constraints

### Mandatory Constraints

1. **Stateless Operation:** Server MUST hold zero runtime state between requests
2. **Tool-Based Access:** ALL task operations MUST be exposed exclusively as MCP tools
3. **Database Persistence:** MCP tools MUST persist all state in the database
4. **API Contract:** API responses MUST follow the defined request/response schema
5. **User Isolation:** Every task MUST be scoped by user_id with proper constraints

### Technology Constraints

1. Backend MUST be implemented using Python FastAPI
2. MCP server MUST use the Official MCP SDK only
3. All database access MUST be performed via SQLModel
4. Single chat endpoint: POST /api/{user_id}/chat
5. MCP tools MUST be stateless and persist all state in the database

### Architecture Constraints

1. Chat endpoint MUST fetch conversation history from the database
2. Chat endpoint MUST store incoming user messages
3. Chat endpoint MUST execute the AI agent with MCP tools
4. Chat endpoint MUST store assistant responses
5. Chat endpoint MUST return response and tool call metadata

### Process Constraints

1. MCP server MUST act as the sole interface for task CRUD operations
2. Database MUST be the single source of truth for tasks and conversations
3. All task operations MUST be exposed exclusively as MCP tools
4. Tools MUST validate required parameters before processing
5. System behavior MUST be deterministic given identical inputs

---

## Governance

### Amendment Process

1. Proposed amendments MUST be documented with rationale for system architecture changes
2. Amendments MUST be reviewed for impact on existing system operations
3. Version MUST be incremented according to semantic versioning:
   - **MAJOR:** Backward-incompatible changes to core principles or constraints
   - **MINOR:** New principles or sections added for system behavior
   - **PATCH:** Clarifications, wording improvements, non-semantic changes
4. `LAST_AMENDED_DATE` MUST be updated to current date
5. Sync Impact Report MUST be generated and prepended as HTML comment

### Versioning Policy

- Constitution version follows semantic versioning (MAJOR.MINOR.PATCH)
- All dependent templates MUST be reviewed when constitution changes
- Breaking changes to system behavior MUST be communicated to stakeholders
- Version history MUST be maintained in git commits

### Compliance Review

- All system implementations MUST reference this constitution
- All architectural decisions for system behavior MUST align with core principles
- System operations MUST be verified for adherence to standards
- Violations MUST be documented and corrected or justified

### Dependent Artifacts

The following artifacts MUST remain consistent with this constitution:

- `.specify/templates/plan-template.md` - System architecture planning template
- `.specify/templates/spec-template.md` - System feature specification template
- `.specify/templates/tasks-template.md` - System task breakdown template
- `.specify/templates/commands/*.md` - System command definitions
- `README.md` - Project documentation
- All system architecture specifications in `specs/*/spec.md`

---

## Success Criteria

A system operation is considered successful when:

1. ✅ Same inputs produce the same outputs consistently
2. ✅ MCP tools validate required parameters before processing
3. ✅ All state is persisted in the database (no in-memory state)
4. ✅ API responses follow the defined request/response schema
5. ✅ User data is properly isolated by user_id
6. ✅ All operations are atomic and maintain data integrity
7. ✅ Error handling is consistent and appropriate
8. ✅ System behavior follows all constitutional principles
9. ✅ Performance meets defined requirements (response times under 2s)
10. ✅ System behavior is consistent with written specifications

---

**End of Constitution**
