"""
Defines the LangChain agent logic, including the system prompt, memory, and tools.
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.tools import tool
from langchain.memory import ConversationBufferMemory

from menu import get_menu_string

# Define the explicit schema for the tool inputs so the LLM knows exactly what to provide
class PlaceOrderInput(BaseModel):
    items: List[Dict[str, Any]] = Field(
        description="A list of dictionaries. Each dictionary must contain a 'name' (str) for the menu item name, and a 'quantity' (int) for how many."
    )

@tool(args_schema=PlaceOrderInput)
def place_order(items: List[Dict[str, Any]]) -> str:
    """
    Submits the user's final order to the kitchen and calculates the total price.
    Call this tool ONLY when the user is completely ready to finalize their order.
    """
    from menu import MENU
    
    # Flatten menu for easy string-matching price lookup
    menu_prices = {}
    for category_items in MENU.values():
        for item in category_items:
            # lowercasing for easier/fuzzy matching
            menu_prices[item["name"].lower()] = item["price"]

    total_price = 0.0
    order_summary = []

    for ordered_item in items:
        # Provide fallbacks if LLM formats it slightly wrong
        name = ordered_item.get("name", "Unknown Item")
        quantity = ordered_item.get("quantity", 1)
        
        # Look up price, default to 0.0 if the item isn't strictly found
        price = menu_prices.get(str(name).lower(), 0.0)
        item_total = price * int(quantity)
        total_price += item_total
        
        order_summary.append(f"{quantity}x {name} (${price:.2f} each)")

    summary_str = "\n".join(order_summary)
    
    # Print the confirmation as a side effect directly to the terminal
    print("\n" + "="*25)
    print("--- KITCHEN TICKET ---")
    print(summary_str)
    print("-" * 25)
    print(f"Total: ${total_price:.2f}")
    print("="*25 + "\n")

    # The string returned here is fed back into the LLM so it knows the tool succeeded
    return f"Order placed successfully! The total price is ${total_price:.2f}. Please confirm this with the user and thank them."

def setup_agent() -> AgentExecutor:
    """Creates and configures the LangChain agent pipeline."""
    
    # 1. Choose the LLM. Using Google Gemini as requested.
    # Note: Requires GOOGLE_API_KEY environment variable to be set.
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    
    # 2. Setup the tools array
    tools = [place_order]
    
    # 3. Define the System Prompt
    system_message = f"""You are a polite, helpful waiter at a restaurant. 
Your job is to assist the user with the menu, answer questions about the food, and take their order.

Here is the current menu:
{get_menu_string()}

Instructions:
1. Greet the user politely and ask if they would like to hear the menu or if they have questions.
2. ONLY offer items that are on the menu provided above. If a user asks for something else, politely inform them it's not available.
3. Help the user build their order. Keep track of what they want.
4. When the user indicates they are completely ready to order (e.g., "that's all", "I'm ready to order", "place my order"), use the `place_order` tool.
5. Provide the `place_order` tool with a list of items and their quantities based on the conversation.
6. After the order is placed successfully via the tool, inform the user of their total and thank them.
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        # This placeholder will be injected with messages from the ConversationBufferMemory
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        # This placeholder is required for Tool Calling Agents to store intermediate steps and tool responses
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # 4. Create the Tool Calling Agent (Modern equivalent of older initialize_agent / LLMChain)
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # 5. Setup Memory
    # memory_key must match the variable_name in the MessagesPlaceholder above
    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True
    )
    
    # 6. Create the Agent Executor to handle running the agent and executing tools
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        memory=memory, 
        verbose=False  # Set to True if you want to see standard LangChain debug output
    )
    
    return agent_executor
