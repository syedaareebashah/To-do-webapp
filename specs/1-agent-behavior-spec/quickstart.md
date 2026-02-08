# Quickstart Guide: Todo AI Chatbot Agent

## Overview
This guide provides a quick introduction to setting up and using the Todo AI Chatbot Agent that processes natural language requests and maps them to MCP task management tools.

## Prerequisites
- OpenAI API access with appropriate permissions
- MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) available and functioning
- Environment variables configured:
  - OPENAI_API_KEY: Your OpenAI API key
  - MCP_TOOL_ENDPOINT: Base URL for MCP tools

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install Dependencies
```bash
pip install openai
# Other required packages as needed
```

### 3. Configure Environment Variables
Create a `.env` file with the following:
```
OPENAI_API_KEY=your_openai_api_key_here
MCP_TOOL_ENDPOINT=your_mcp_tool_endpoint_here
```

## Basic Usage

### Starting the Agent
```python
from todo_chatbot_agent import TodoChatbotAgent

# Initialize the agent
agent = TodoChatbotAgent()

# Process user input
response = agent.process_input("Add a task to buy groceries")
print(response)  # Output: "Added task: 'buy groceries'"
```

### Supported Commands

#### Task Creation
- "Add a task to [task content]"
- "Create a task for [task content]"
- "Remember to [task content]"

#### Task Listing
- "Show my tasks"
- "List all tasks"
- "What do I have to do?"

#### Task Completion
- "Complete task [id]"
- "Finish task [id]"
- "Mark task [id] as done"

#### Task Deletion
- "Delete task [id]"
- "Remove task [id]"
- "Cancel task [id]"

#### Task Updates
- "Update task [id] to [new content]"
- "Change task [id] to [new content]"

## Configuration Options

### Confidence Threshold
Adjust the confidence threshold for intent recognition:
```python
agent = TodoChatbotAgent(confidence_threshold=0.7)  # Default is 0.7
```

### Context Length
Set the maximum number of conversation turns to retain:
```python
agent = TodoChatbotAgent(max_context_turns=20)  # Default is 20
```

## Error Handling

### Common Errors and Solutions

#### "Task not found"
- **Cause:** User referenced a task that doesn't exist
- **Solution:** The agent will respond with a friendly message and may offer to list tasks

#### "Unclear request"
- **Cause:** Intent confidence was below the threshold
- **Solution:** The agent will ask clarifying questions

#### "MCP tool unavailable"
- **Cause:** MCP tool service is temporarily down
- **Solution:** The agent will inform the user and suggest trying again later

## Example Interactions

### Successful Task Addition
```
User: "Add a task to schedule dentist appointment"
Agent: "Added task: 'schedule dentist appointment'"
```

### Task Listing with Filtering
```
User: "Show my pending tasks"
Agent: "Your pending tasks: 1. Buy groceries, 2. Schedule dentist appointment"
```

### Error with Clarification
```
User: "Do that thing"
Agent: "Could you clarify what task you'd like me to perform? You can ask me to add, list, complete, update, or delete tasks."
```

## Development

### Running Tests
```bash
pytest tests/
```

### Local Development Server
```bash
python -m todo_chatbot_agent.local_server
```

## Next Steps
- Review the detailed API documentation
- Explore advanced configuration options
- Set up monitoring and logging
- Implement custom response templates for your use case