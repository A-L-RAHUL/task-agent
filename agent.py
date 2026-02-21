"""
Agent Module - LangGraph Agent with Tools
------------------------------------------

This module creates a LangGraph agent using create_react_agent (modern approach)
with a place_order tool for handling restaurant orders.

Key components:
- System prompt with menu context
- place_order tool for order processing
- LangGraph agent using create_react_agent
"""

import os
import json
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from menu import MENU, get_item_by_name, format_menu_for_prompt
from database import get_menu_item_by_name, format_menu_for_prompt as db_format_menu_for_prompt

# Load environment variables
load_dotenv()


def create_place_order_tool(menu_items: List[Dict[str, Any]], save_to_db: bool = True):
    """
    Create a place_order tool function that uses the provided menu items.
    
    Args:
        menu_items: List of menu item dictionaries from database
        save_to_db: Whether to save orders to database (default: True)
    
    Returns:
        A tool function for placing orders
    """
    from database import create_order
    
    # Create a lookup dictionary for fast access
    menu_lookup = {}
    for item in menu_items:
        menu_lookup[item["name"].lower()] = item
    
    def find_menu_item(item_name: str):
        """Find menu item by name (case-insensitive, flexible)."""
        item_name_lower = item_name.lower().strip()
        
        # Exact match
        if item_name_lower in menu_lookup:
            return menu_lookup[item_name_lower]
        
        # Partial match
        for key, item in menu_lookup.items():
            if item_name_lower in key or key in item_name_lower:
                return item
        
        return None
    
    # Define the tool function with proper docstring
    @tool
    def place_order(items: List[Dict[str, Any]]) -> str:
        """
        Place an order for restaurant items.
        
        This tool processes a list of items with quantities, calculates the total price,
        and saves the order to the database. The agent should call this when the user
        is ready to finalize their order.
        
        Args:
            items: List of dictionaries, each containing:
                - "name": str - The name of the menu item
                - "quantity": int - The quantity ordered (defaults to 1 if not provided)
        
        Returns:
            A formatted confirmation string with order details and total price
        
        Example:
            place_order([
                {"name": "Margherita Pizza", "quantity": 1},
                {"name": "Cola", "quantity": 2}
            ])
        """
        if not items or len(items) == 0:
            return "No items in the order. Please specify what you'd like to order."
        
        order_items = []
        total_price = 0.0
        
        for item_data in items:
            item_name = item_data.get("name", "").strip()
            quantity = item_data.get("quantity", 1)
            
            if not item_name:
                continue
            
            # Find the menu item
            menu_item = find_menu_item(item_name)
            
            if menu_item is None:
                return f"Error: '{item_name}' is not on the menu. Please check the menu and try again."
            
            item_total = menu_item["price"] * quantity
            total_price += item_total
            
            order_items.append({
                "name": menu_item["name"],
                "quantity": quantity,
                "unit_price": menu_item["price"],
                "total": item_total
            })
        
        # Save to database if enabled
        if save_to_db:
            try:
                items_json = json.dumps(order_items)
                # Get restaurant_id from first menu item if available
                restaurant_id = menu_items[0].get("restaurant_id", 1) if menu_items else 1
                create_order(items_json, total_price, restaurant_id=restaurant_id, status="pending")
            except Exception as e:
                # Log error but don't fail the order
                print(f"Warning: Could not save order to database: {e}")
        
        # Build confirmation message
        confirmation_lines = [
            "\n" + "="*50,
            "ORDER CONFIRMATION",
            "="*50
        ]
        
        for order_item in order_items:
            confirmation_lines.append(
                f"{order_item['quantity']}x {order_item['name']} @ ${order_item['unit_price']:.2f} = ${order_item['total']:.2f}"
            )
        
        confirmation_lines.append("-" * 50)
        confirmation_lines.append(f"TOTAL: ${total_price:.2f}")
        confirmation_lines.append("="*50 + "\n")
        
        confirmation = "\n".join(confirmation_lines)
        
        # Print to console (for internal logging)
        print(confirmation)
        
        return (
            f"Order placed successfully! Your order includes {len(order_items)} item(s) "
            f"for a total of ${total_price:.2f}. Thank you for your order!"
        )
    
    return place_order


def create_agent():
    """
    Create and return a LangGraph agent configured for restaurant order-taking.
    Uses the static menu from menu.py (for backward compatibility).
    
    Returns:
        A compiled LangGraph agent ready to use
    """
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing GOOGLE_API_KEY. Please set it in your .env file.\n"
            "Get your key from: https://makersuite.google.com/app/apikey"
        )
    
    # Initialize LLM
    # Using gemini-2.5-flash or gemini-3.0-flash as requested
    model_name = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
    temperature = float(os.getenv("GOOGLE_TEMPERATURE", "0.7"))
    
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=api_key,
    )
    
    # Format menu for system prompt
    menu_text = format_menu_for_prompt()
    
    # System prompt with menu context
    system_prompt_text = f"""You are BiteBot, a friendly and helpful waiter at a restaurant.

Your role:
- Greet customers warmly and help them with the menu
- Answer questions about menu items (ingredients, dietary restrictions, prices, descriptions)
- Be conversational, natural, and handle typos or informal language
- Only offer items that are on the menu - if asked for something not available, politely suggest alternatives
- When the customer is ready to order, use the place_order tool with a list of items and quantities
- Be flexible and understanding with customer requests

Menu:
{menu_text}

Important:
- Always be polite and helpful
- Match customer requests to menu items intelligently (handle typos, abbreviations, etc.)
- When the customer says they're ready to order or want to place an order, use the place_order tool
- The place_order tool requires a list of dictionaries with "name" and "quantity" keys
- If quantity is not specified, assume 1

Remember: You're here to help customers have a great dining experience!"""
    
    # Bind system message to the LLM
    # This ensures the system prompt is included in every LLM call
    from langchain_core.messages import SystemMessage
    llm_with_system = llm.bind(system=system_prompt_text)
    
    # Define tools available to the agent
    tools = [place_order]
    
    # Create the LangGraph agent using create_react_agent
    # This is the modern, recommended way to create agents in LangGraph
    # It handles tool-calling, state management, and execution loops automatically
    agent = create_react_agent(
        model=llm_with_system,
        tools=tools,
    )
    
    return agent


def create_agent_with_menu(menu_items: List[Dict[str, Any]], save_to_db: bool = True):
    """
    Create and return a LangGraph agent configured for restaurant order-taking
    using a dynamic menu from the database.
    
    Args:
        menu_items: List of menu item dictionaries from database
        save_to_db: Whether to save orders to database (default: True)
    
    Returns:
        A compiled LangGraph agent ready to use
    
    Raises:
        ValueError: If GOOGLE_API_KEY is missing or menu_items is empty
    """
    if not menu_items:
        raise ValueError("Cannot create agent: menu_items list is empty")
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing GOOGLE_API_KEY. Please set it in your .env file.\n"
            "Get your key from: https://makersuite.google.com/app/apikey"
        )
    
    # Initialize LLM with rate limit handling
    model_name = os.getenv("GOOGLE_MODEL", "gemini-pro")  # Use gemini-pro as default to avoid quota issues
    temperature = float(os.getenv("GOOGLE_TEMPERATURE", "0.7"))
    
    # Try to create LLM, fallback to gemini-pro if rate limited
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=api_key,
            max_retries=2,
        )
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower() or "rate" in str(e).lower():
            # Fallback to gemini-pro if rate limited
            if model_name != "gemini-pro":
                print(f"⚠️ Rate limit reached for {model_name}. Falling back to gemini-pro...")
                llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    temperature=temperature,
                    google_api_key=api_key,
                    max_retries=2,
                )
            else:
                raise ValueError(f"API quota exceeded. Please check your billing: {e}")
        else:
            raise
    
    # Format menu for system prompt using database formatter
    menu_text = db_format_menu_for_prompt(menu_items)
    
    # Check if we're in comparison mode (multiple restaurants)
    has_multiple_restaurants = any("restaurant_name" in item for item in menu_items)
    
    comparison_instructions = ""
    if has_multiple_restaurants:
        comparison_instructions = """
COMPARISON MODE - MULTI-RESTAURANT SUPPORT:
- You can compare dishes across different restaurants
- When asked to compare, mention the restaurant name along with the dish
- Help customers find the best option by comparing prices, ingredients, and descriptions
- If a customer asks "which restaurant has X?", search across all restaurants in the menu
- You can recommend dishes from different restaurants if the customer is open to it
"""
    
    # System prompt with STRICT menu adherence
    system_prompt_text = f"""You are BiteBot, a friendly and helpful waiter assistant.

CRITICAL INSTRUCTIONS - STRICT MENU ADHERENCE:
- You MUST ONLY discuss, offer, or suggest items that are EXACTLY listed in the menu below
- You CANNOT make assumptions, hallucinate, or invent menu items
- If a customer asks for something NOT in the menu, politely say "I'm sorry, we don't have that on our menu" and suggest similar items from the ACTUAL menu
- You MUST use the EXACT item names, prices, and descriptions as shown in the menu below
- DO NOT guess prices, ingredients, or descriptions - only use what is explicitly provided
- Respond quickly and concisely - keep explanations brief and helpful

{comparison_instructions}

Your role:
- Greet customers warmly and help them with the menu
- Answer questions about menu items (ingredients, dietary restrictions, prices, descriptions) using ONLY the information provided
- Be conversational, natural, and handle typos or informal language
- When the customer is ready to order, use the place_order tool with a list of items and quantities
- Be flexible and understanding with customer requests, but always within the constraints of the actual menu
- Keep responses concise and fast - don't over-explain

CURRENT MENU (this is the ONLY menu available - do not offer anything else):
{menu_text}

Important:
- Always be polite and helpful
- Match customer requests to menu items intelligently (handle typos, abbreviations, etc.)
- When the customer says they're ready to order or want to place an order, use the place_order tool
- The place_order tool requires a list of dictionaries with "name" and "quantity" keys
- If quantity is not specified, assume 1
- REMEMBER: You can ONLY offer items from the menu above - nothing else exists!
- Keep responses brief and to the point for faster interactions

Remember: You're here to help customers have a great dining experience, but you must stick to the actual menu!"""
    
    # Bind system message to the LLM
    llm_with_system = llm.bind(system=system_prompt_text)
    
    # Create place_order tool with dynamic menu
    place_order_tool = create_place_order_tool(menu_items, save_to_db)
    
    # Define tools available to the agent
    tools = [place_order_tool]
    
    # Create the LangGraph agent using create_react_agent
    agent = create_react_agent(
        model=llm_with_system,
        tools=tools,
    )
    
    return agent
