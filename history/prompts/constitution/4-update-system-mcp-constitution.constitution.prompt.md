---
id: 7
title: Update System MCP Constitution
stage: constitution
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: mehre
command: /sp.constitution
labels: ["constitution", "todo-chatbot", "system-architecture", "mcp-server", "stateless-design"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```text
Project: Todo AI Chatbot — System & MCP Specification (Spec 2)

Scope:
This constitution governs the backend system architecture, MCP server behavior,
API contracts, data persistence, and stateless execution model.
It does NOT define AI reasoning or intent interpretation logic.

Core principles:
- Stateless system design (no in-memory state across requests)
- Tool-based interaction (AI interacts with the system only via MCP tools)
- Clear separation of concerns (API, MCP server, database)
- Deterministic behavior (same inputs produce the same outputs)
- Reliability and data integrity (persistent, consistent storage)

Key standards:
- Backend must be implemented using Python FastAPI
- MCP server must use the Official MCP SDK only
- All task operations must be exposed exclusively as MCP tools
- MCP tools must be stateless and persist all state in the database
- Chat endpoint must reconstruct conversation state from the database on every request
- Server must hold zero runtime state between requests
- API responses must strictly follow the defined request/response schema

Architecture rules:
- Single chat endpoint: POST /api/{user_id}/chat
- Chat endpoint responsibilities:
  - Fetch conversation history from the database
  - Store incoming user messages
  - Execute the AI agent with MCP tools
  - Store assistant responses
  - Return response and tool call metadata
- MCP server must act as the sole interface for task CRUD operations
- Database must be the single source of truth for tasks and conversations

Data integrity rules:
- All database access must be performed via SQLModel
- Every task must be scoped by user_id
- Every message must be linked to a conversation_id
- Message roles must be explicitly stored as user or assistant
- Timestamps must be recorded for all persistent entities

Tool contract enforcement:
- MCP tool names, parameters, and return values must match the specification exactly
- Tools must validate required parameters
- Tools must return structured, predictable responses
- Er
```

## Response snapshot

Updated comprehensive constitution from v2.0.0 to v3.0.0 for Todo AI Chatbot System & MCP Specification with:

1. **Five Core Principles:**
   - Stateless System Design: No in-memory state across requests, all state in database
   - Tool-Based Interaction: AI interacts with system only via MCP tools
   - Clear Separation of Concerns: Distinct responsibilities for API, MCP server, database
   - Deterministic Behavior: Same inputs produce same outputs consistently
   - Reliability and Data Integrity: Atomic operations and consistent storage

2. **Technology Standards:**
   - Backend Architecture: Python FastAPI, SQLModel ORM, MCP SDK
   - API Design: Single endpoint with strict schema compliance
   - MCP Server: Official SDK with stateless tools
   - Database: SQLModel with proper relationships and constraints

3. **Quality Requirements:**
   - System Behavior: Strict schema compliance and consistent error handling
   - Data Integrity: Proper scoping, linking, and timestamp recording
   - API Quality: RESTful design with semantic status codes
   - MCP Tool Quality: Exact specification matching with validation
   - Security: User isolation and input validation

4. **Mandatory Constraints:**
   - Server holds zero runtime state between requests
   - All task operations exposed exclusively as MCP tools
   - MCP tools persist all state in database
   - API responses follow defined schemas
   - Tasks scoped by user_id with proper isolation

5. **Governance:**
   - Semantic versioning (3.0.0 reflecting major architectural focus shift)
   - Amendment process with impact analysis
   - Compliance review requirements
   - Dependent artifact consistency checks for system-specific templates

## Outcome

- ✅ Impact: Updated constitution from v2.0.0 to v3.0.0 for system architecture focus
- 🧪 Tests: none (constitution document update)
- 📁 Files: .specify/memory/constitution.md updated with system/MCP focus
- 🔁 Next prompts: Update dependent templates (plan, spec, tasks) for system-specific constraints
- 🧠 Reflection: Constitution properly captures stateless, tool-based system architecture with clear separation of concerns

## Evaluation notes

- Failure modes observed: none
- Graders run and results: PASS (all principles clearly defined and testable for system architecture)
- Prompt variant: Constitution update from agent behavior to system architecture focus
- Next experiment: Update plan-template.md, spec-template.md, and tasks-template.md for system-specific constraints