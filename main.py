"""
Main Entry Point - Interactive CLI
-----------------------------------

This module provides the interactive command-line interface for the restaurant agent.
It maintains conversation history and handles user input/output.

Usage:
    python3 main.py
"""

import sys
from typing import List

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory

from agent import create_agent


class InMemoryChatHistory(BaseChatMessageHistory):
    """
    Simple in-memory chat history implementation.
    
    This stores conversation messages in memory for the duration of the session.
    For production use, consider using a persistent store (database, Redis, etc.).
    """
    
    def __init__(self):
        self.messages: List = []
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to the history."""
        self.messages.append(HumanMessage(content=message))
    
    def add_ai_message(self, message: str) -> None:
        """Add an AI message to the history."""
        self.messages.append(AIMessage(content=message))
    
    def clear(self) -> None:
        """Clear all messages from history."""
        self.messages = []
    
    @property
    def messages(self) -> List:
        """Get all messages."""
        return self._messages
    
    @messages.setter
    def messages(self, value: List) -> None:
        """Set messages."""
        self._messages = value


def main():
    """
    Main interactive loop for the restaurant agent.
    
    This function:
    1. Creates the agent
    2. Initializes conversation history
    3. Runs a while loop to handle user input
    4. Maintains conversation context across turns
    """
    print("\n" + "="*60)
    print("Welcome to BiteBot Restaurant Ordering System!")
    print("="*60)
    print("\nBiteBot: Hi! I'm BiteBot, your friendly waiter.")
    print("         How can I help you today?\n")
    
    try:
        # Create the agent
        agent = create_agent()
        print("✓ Agent initialized successfully\n")
    except Exception as e:
        print(f"\n✗ Error initializing agent: {e}", file=sys.stderr)
        print("\nPlease check:")
        print("1. Your .env file has GOOGLE_API_KEY set")
        print("2. Your API key is valid")
        print("3. You have internet connectivity")
        sys.exit(1)
    
    # Initialize conversation history
    chat_history = InMemoryChatHistory()
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input("Client: ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in {"quit", "exit", "bye", "goodbye"}:
                print("\nBiteBot: Thank you for visiting! Have a great day! 👋\n")
                break
            
            # Add user message to history
            chat_history.add_user_message(user_input)
            
            # Prepare input for agent
            # LangGraph agents expect messages in the state
            # We'll pass the full conversation history
            agent_input = {
                "messages": chat_history.messages
            }
            
            # Invoke the agent
            # The agent will process the input, potentially call tools,
            # and return a response with updated messages
            try:
                response = agent.invoke(agent_input)
                
                # Extract the AI's response from the agent output
                # The agent returns a state dict with "messages" key
                if isinstance(response, dict) and "messages" in response:
                    # Update our chat history with the agent's updated messages
                    # This ensures we stay in sync with the agent's state
                    updated_messages = response["messages"]
                    
                    # Find new messages (messages that weren't in our history)
                    # The agent may have added tool calls, tool results, and final response
                    our_message_count = len(chat_history.messages)
                    new_messages = updated_messages[our_message_count:]
                    
                    # Extract the final AI response (last non-tool message)
                    ai_response = None
                    for msg in reversed(new_messages):
                        if hasattr(msg, "content") and msg.content:
                            # Skip tool call messages, get the actual response
                            if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                ai_response = msg.content
                                break
                    
                    if not ai_response:
                        # Fallback: use the last message's content
                        if new_messages:
                            last_msg = new_messages[-1]
                            if hasattr(last_msg, "content"):
                                ai_response = last_msg.content
                            else:
                                ai_response = str(last_msg)
                        else:
                            ai_response = "I'm here to help! What would you like to know?"
                    
                    # Update chat history with all new messages from agent
                    chat_history.messages = updated_messages
                    
                else:
                    ai_response = str(response)
                    # Fallback: add as AI message
                    chat_history.add_ai_message(ai_response)
                
                # Print agent response
                print(f"\nBiteBot: {ai_response}\n")
                
            except Exception as e:
                error_msg = f"I apologize, but I encountered an error: {str(e)}"
                print(f"\nBiteBot: {error_msg}\n")
                print(f"Debug info: {type(e).__name__}", file=sys.stderr)
                # Don't add error messages to history to avoid polluting the conversation
        
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nBiteBot: Thanks for visiting! Goodbye! 👋\n")
            break
        except EOFError:
            # Handle Ctrl+D (EOF)
            print("\n\nBiteBot: Thanks for visiting! Goodbye! 👋\n")
            break


if __name__ == "__main__":
    main()
