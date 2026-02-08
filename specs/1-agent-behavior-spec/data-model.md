# Data Model: Todo AI Chatbot Agent

## Core Entities

### Intent
Represents the user's intention extracted from natural language input.

**Fields:**
- `id`: Unique identifier for the intent
- `type`: Enum (ADD_TASK, LIST_TASKS, COMPLETE_TASK, DELETE_TASK, UPDATE_TASK, AMBIGUOUS)
- `confidence`: Float (0.0-1.0) representing confidence in intent classification
- `parameters`: Object containing extracted parameters from user input
- `timestamp`: When the intent was recognized

**Validation Rules:**
- Confidence must be between 0.0 and 1.0
- Type must be one of the defined enum values
- Parameters must conform to the schema for the specific intent type

### ToolMapping
Defines the relationship between recognized intents and MCP tools.

**Fields:**
- `intent_type`: The type of intent (matches Intent.type)
- `mcp_tool`: String name of the corresponding MCP tool
- `required_parameters`: Array of required parameter names
- `optional_parameters`: Array of optional parameter names

**Validation Rules:**
- intent_type must be a valid intent enum value
- mcp_tool must correspond to an existing MCP tool
- required_parameters must be a subset of valid parameters for the tool

### ResponseTemplate
Standardized templates for agent responses based on action type.

**Fields:**
- `action_type`: String indicating the type of action (SUCCESS, ERROR, CLARIFICATION)
- `template`: String template with placeholders for dynamic content
- `tone`: Enum (FRIENDLY, PROFESSIONAL, NEUTRAL)

**Validation Rules:**
- action_type must be one of the defined values
- template must contain valid placeholders
- tone must be one of the defined enum values

### ConversationContext
Represents the current state of the conversation.

**Fields:**
- `conversation_id`: Unique identifier for the conversation
- `turns`: Array of conversation turns (user input and agent responses)
- `active_tasks`: Array of task IDs relevant to the current conversation
- `last_intent`: The most recently recognized intent
- `summary`: Optional summary of the conversation for context management

**Validation Rules:**
- conversation_id must be unique
- turns must alternate between user and agent
- active_tasks must contain valid task IDs

## Relationships

- One Intent maps to one ToolMapping
- One ConversationContext contains many Intent objects
- One ConversationContext contains many ResponseTemplate instances (through responses)

## State Transitions

### Intent States
- `RECOGNIZED`: Intent has been identified from user input
- `VALIDATED`: Parameters have been validated against tool requirements
- `EXECUTED`: MCP tool has been called successfully
- `FAILED`: Tool execution or validation failed

### Conversation States
- `ACTIVE`: Conversation is ongoing and accepting input
- `WAITING_FOR_CLARIFICATION`: Awaiting user response to clarification question
- `COMPLETED`: Conversation has reached a natural conclusion
- `EXPIRED`: Conversation has timed out due to inactivity