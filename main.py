"""
The main entry point for the interactive terminal application.
"""
import os
import sys
from dotenv import load_dotenv

from agent import setup_agent

def main():
    # Load environment variables from .env file (if it exists)
    load_dotenv()
    
    # Check if GOOGLE_API_KEY is present
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY is not set.")
        print("Please copy .env.example to .env and add your Google API key.")
        sys.exit(1)

    print("Initializing Restaurant Agent...")
    try:
        agent_executor = setup_agent()
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        sys.exit(1)
        
    print("\n" + "*"*40)
    print("* Welcome to the Restaurant Terminal! *")
    print("*"*40)
    print("\nThe waiter is ready. Type 'quit', 'exit', or 'bye' to leave.\n")
    
    # Interactive chat loop
    while True:
        try:
            # 1. Take user input
            user_input = input("You: ").strip()
            
            # 2. Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nWaiter: Thank you for visiting! Have a great day!")
                break
                
            if not user_input:
                continue
                
            # 3. Pass input to AgentExecutor
            # The 'chat_history' is automatically maintained by ConversationBufferMemory inside the executor
            response = agent_executor.invoke({"input": user_input})
            
            # 4. Print the agent's textual response
            print(f"Waiter: {response['output']}\n")
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nWaiter: Thank you for visiting! Have a great day!")
            break
        except Exception as e:
            print(f"\nAn error occurred during communication: {e}")

if __name__ == "__main__":
    main()
