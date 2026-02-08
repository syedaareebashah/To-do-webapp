"""
Simple test script to verify the Todo AI Chatbot Agent functionality.
"""

from src.agents.todo_chatbot_agent import TodoChatbotAgent
from src.models.conversation_context import ConversationContext


def test_agent():
    """
    Test the TodoChatbotAgent with sample inputs.
    """
    print("Initializing TodoChatbotAgent...")
    agent = TodoChatbotAgent(confidence_threshold=0.3)  # Lower threshold for testing

    print("\nTesting various user inputs:")

    # Test cases - focusing on different intent types
    test_cases = [
        "Add a task to buy groceries",      # ADD_TASK
        "Create a task to call mom",       # ADD_TASK
        "Show my tasks",                   # LIST_TASKS
        "List all my tasks",               # LIST_TASKS
        "Complete task 1",                 # COMPLETE_TASK
        "Finish task 2",                   # COMPLETE_TASK
        "Delete task 3",                   # DELETE_TASK
        "Remove task 4",                  # DELETE_TASK
        "Update task 1 to 'Call doctor'", # UPDATE_TASK
        "Change task 2 priority to high",  # UPDATE_TASK
        "What can you do?",               # AMBIGUOUS
        "Help me"                          # AMBIGUOUS
    ]

    conversation_context = ConversationContext()

    for i, user_input in enumerate(test_cases):
        print(f"\nTest {i+1}: User input: '{user_input}'")

        try:
            response = agent.process_input(user_input, conversation_context)
            print(f"Agent response: '{response}'")
        except Exception as e:
            print(f"Error processing input: {e}")

    print("\nTest completed!")

    # Test the MCP tool interface directly to verify it's working
    print("\nTesting MCP tool interface directly:")
    from src.interfaces.mcp_tool_interface import MCPTOOLInterface
    mcp_interface = MCPTOOLInterface()

    # Test add_task
    result = mcp_interface.execute_tool("add_task", {"task_content": "Test task from direct interface"})
    print(f"Direct add_task result: {result}")

    # Test list_tasks
    result = mcp_interface.execute_tool("list_tasks", {"filter": "all"})
    print(f"Direct list_tasks result: {result}")


if __name__ == "__main__":
    test_agent()