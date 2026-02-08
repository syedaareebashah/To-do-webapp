# Data Model: Todo AI Chatbot System & MCP

## Core Entities

### User
Represents a system user.

**Fields:**
- `id`: String (Primary Key) - Unique identifier for the user
- `username`: String - Unique username for the user
- `email`: String - User's email address
- `created_at`: DateTime - Timestamp when the user account was created

**Validation Rules:**
- `id` must be unique and non-null
- `username` must be unique and non-null
- `email` must be a valid email format and unique
- `created_at` is set automatically upon creation

**Relationships:**
- One User to Many Tasks
- One User to Many Conversations

### Task
Represents a user's task in the todo system.

**Fields:**
- `id`: String (Primary Key) - Unique identifier for the task
- `user_id`: String (Foreign Key) - References the User who owns the task
- `content`: String - The content/description of the task
- `status`: String - Current status of the task (pending, completed)
- `due_date`: DateTime (Optional) - Deadline for the task
- `priority`: String - Priority level (low, medium, high)
- `created_at`: DateTime - Timestamp when the task was created
- `completed_at`: DateTime (Optional) - Timestamp when the task was completed

**Validation Rules:**
- `id` must be unique and non-null
- `user_id` must reference an existing User
- `content` must be non-null and non-empty
- `status` must be one of the allowed values: 'pending', 'completed'
- `priority` must be one of the allowed values: 'low', 'medium', 'high'
- `completed_at` can only be set when status is 'completed'

**Relationships:**
- Many Tasks to One User (via user_id)

### Conversation
Represents a conversation thread between user and assistant.

**Fields:**
- `id`: String (Primary Key) - Unique identifier for the conversation
- `user_id`: String (Foreign Key) - References the User who owns the conversation
- `created_at`: DateTime - Timestamp when the conversation was started
- `updated_at`: DateTime - Timestamp when the conversation was last updated

**Validation Rules:**
- `id` must be unique and non-null
- `user_id` must reference an existing User
- `created_at` is set automatically upon creation
- `updated_at` is updated automatically when messages are added

**Relationships:**
- Many Conversations to One User (via user_id)
- One Conversation to Many Messages

### Message
Represents a single message in a conversation.

**Fields:**
- `id`: String (Primary Key) - Unique identifier for the message
- `conversation_id`: String (Foreign Key) - References the Conversation this message belongs to
- `role`: String - Role of the message sender (user, assistant)
- `content`: String - The content of the message
- `timestamp`: DateTime - Timestamp when the message was sent

**Validation Rules:**
- `id` must be unique and non-null
- `conversation_id` must reference an existing Conversation
- `role` must be one of the allowed values: 'user', 'assistant'
- `content` must be non-null and non-empty
- `timestamp` is set automatically upon creation

**Relationships:**
- Many Messages to One Conversation (via conversation_id)

## Relationships

### User ↔ Task
- One-to-Many relationship
- A User can have many Tasks
- A Task belongs to one User
- Foreign key: `user_id` in Task table references `id` in User table
- Cascade delete: When User is deleted, all their Tasks are also deleted

### User ↔ Conversation
- One-to-Many relationship
- A User can have many Conversations
- A Conversation belongs to one User
- Foreign key: `user_id` in Conversation table references `id` in User table
- Cascade delete: When User is deleted, all their Conversations are also deleted

### Conversation ↔ Message
- One-to-Many relationship
- A Conversation can have many Messages
- A Message belongs to one Conversation
- Foreign key: `conversation_id` in Message table references `id` in Conversation table
- Cascade delete: When Conversation is deleted, all its Messages are also deleted

## State Transitions

### Task Status Transitions
- `pending` → `completed` (when task is marked as done)
- `completed` → `pending` (when task is unmarked as done)

### Valid Transitions:
- A task can transition from pending to completed
- A task can transition from completed back to pending
- A task cannot transition to other statuses directly

## Indexes

### Required Indexes:
- Index on `user_id` in Task table for efficient user-based queries
- Index on `user_id` in Conversation table for efficient user-based queries
- Index on `conversation_id` in Message table for efficient conversation-based queries
- Index on `timestamp` in Message table for chronological ordering
- Index on `status` in Task table for filtering by status

## Constraints

### Database-Level Constraints:
- Foreign key constraints to ensure referential integrity
- Unique constraints on User.username and User.email
- Check constraints on status and priority fields to ensure valid values
- Non-null constraints on required fields
- Cascade delete rules to maintain data consistency

### Business Logic Constraints:
- Users can only access their own tasks and conversations
- Messages must belong to a valid conversation
- Tasks must belong to a valid user
- Conversation timestamps are automatically managed