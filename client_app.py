"""
Client Order Bot - Streamlit App
---------------------------------

This Streamlit application provides a chat interface for customers to:
- Chat with BiteBot (LangGraph agent) about the menu
- Place orders that are saved to the database

Run with: streamlit run client_app.py
"""

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from database import (
    init_database, 
    get_all_menu_items,
    get_all_restaurants,
    get_restaurant,
    get_menu_items_by_restaurant,
    get_all_menu_items_all_restaurants
)
from agent import create_agent_with_menu

# Page configuration
st.set_page_config(
    page_title="BiteBot - Order Online",
    page_icon="🤖",
    layout="wide"
)

# Initialize database on startup
if "db_initialized" not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None
    st.session_state.agent_initialized = False

if "selected_restaurant_id" not in st.session_state:
    st.session_state.selected_restaurant_id = None

if "comparison_mode" not in st.session_state:
    st.session_state.comparison_mode = False


@st.cache_data(ttl=10)  # Cache menu for 10 seconds
def get_cached_menu():
    """Get menu items with caching."""
    return get_all_menu_items()


def initialize_agent(restaurant_id: int = None, comparison_mode: bool = False):
    """Initialize the LangGraph agent with current menu."""
    # Check if we need to reinitialize (restaurant changed or first time)
    cache_key = f"agent_{restaurant_id}_{comparison_mode}"
    
    if st.session_state.agent_initialized and st.session_state.get("agent_cache_key") == cache_key:
        return
    
    try:
        if comparison_mode:
            # Get menus from all restaurants for comparison
            menu_items = get_all_menu_items_all_restaurants()
        elif restaurant_id:
            menu_items = get_menu_items_by_restaurant(restaurant_id)
        else:
            menu_items = get_cached_menu()
        
        if not menu_items:
            st.error("⚠️ No menu items available. Please ask the restaurant owner to add items to the menu.")
            return
        
        # Create agent with dynamic menu
        with st.spinner("🤖 Initializing BiteBot..."):
            st.session_state.agent = create_agent_with_menu(menu_items, save_to_db=True)
            st.session_state.agent_initialized = True
            st.session_state.menu_items = menu_items
            st.session_state.agent_cache_key = cache_key
        
        st.success("✅ BiteBot is ready!")
        
    except Exception as e:
        st.error(f"❌ Error initializing agent: {e}")
        st.info("Please check your .env file has GOOGLE_API_KEY set correctly.")


def restaurant_selection_section():
    """Restaurant selection interface."""
    restaurants = get_all_restaurants()
    
    if not restaurants:
        st.error("⚠️ No restaurants available. Please ask the owner to add restaurants.")
        return None
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        restaurant_options = {f"{r['name']}": r['id'] for r in restaurants}
        selected_name = st.selectbox(
            "🍽️ Select Restaurant",
            options=list(restaurant_options.keys()),
            index=0 if not st.session_state.selected_restaurant_id else None,
            key="restaurant_selector_main"
        )
        selected_id = restaurant_options[selected_name]
        
        # Show restaurant info
        restaurant = get_restaurant(selected_id)
        if restaurant and restaurant.get("description"):
            st.caption(restaurant["description"])
    
    with col2:
        comparison_mode = st.checkbox("🔍 Compare Across Restaurants", value=st.session_state.comparison_mode)
        st.session_state.comparison_mode = comparison_mode
    
    # Update selected restaurant if changed
    if st.session_state.selected_restaurant_id != selected_id or st.session_state.comparison_mode != comparison_mode:
        st.session_state.selected_restaurant_id = selected_id if not comparison_mode else None
        st.session_state.agent_initialized = False  # Force reinitialize
        st.session_state.messages = []  # Clear chat history
        st.rerun()
    
    return selected_id if not comparison_mode else None


def main():
    """Main application logic."""
    st.title("🤖 BiteBot - Your Friendly Waiter")
    
    # Restaurant selection
    restaurant_id = restaurant_selection_section()
    
    if restaurant_id is None and not st.session_state.comparison_mode:
        st.info("👆 Please select a restaurant above to continue.")
        return
    
    if st.session_state.comparison_mode:
        st.markdown("**🔍 Comparison Mode:** I can help you compare dishes across all restaurants!")
    else:
        restaurant = get_restaurant(restaurant_id)
        if restaurant:
            st.markdown(f"Welcome to **{restaurant['name']}**! I'm here to help you with our menu and take your order.")
    
    # Initialize agent
    initialize_agent(restaurant_id, st.session_state.comparison_mode)
    
    # Sidebar with menu display
    with st.sidebar:
        st.header("📋 Current Menu")
        
        # Refresh menu button
        if st.button("🔄 Refresh Menu", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        if st.session_state.comparison_mode:
            menu_items = get_all_menu_items_all_restaurants()
        elif st.session_state.selected_restaurant_id:
            menu_items = get_menu_items_by_restaurant(st.session_state.selected_restaurant_id)
        else:
            menu_items = get_cached_menu()
        
        if not menu_items:
            st.info("No menu items available.")
        else:
            # Group by restaurant and category
            from collections import defaultdict
            if st.session_state.comparison_mode:
                by_restaurant = defaultdict(lambda: defaultdict(list))
                for item in menu_items:
                    restaurant_name = item.get("restaurant_name", "Unknown")
                    category = item.get("category", "Other")
                    by_restaurant[restaurant_name][category].append(item)
                
                for restaurant_name in sorted(by_restaurant.keys()):
                    st.subheader(f"🍽️ {restaurant_name}")
                    for category in sorted(by_restaurant[restaurant_name].keys()):
                        st.write(f"**{category}**")
                        for item in sorted(by_restaurant[restaurant_name][category], key=lambda x: x["name"]):
                            st.write(f"  • {item['name']} - ${item['price']:.2f}")
                    st.divider()
            else:
                by_category = defaultdict(list)
                for item in menu_items:
                    by_category[item["category"]].append(item)
                
                for category in sorted(by_category.keys()):
                    st.subheader(category)
                    for item in sorted(by_category[category], key=lambda x: x["name"]):
                        st.write(f"**{item['name']}** - ${item['price']:.2f}")
                        if item.get("description"):
                            st.caption(item["description"])
                    st.divider()
    
    # Main chat interface
    if not st.session_state.agent_initialized:
        st.info("⏳ Please wait while BiteBot initializes...")
        return
    
    # Display chat history
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Prepare input for agent
                    # Convert messages to format expected by LangGraph
                    agent_messages = []
                    for msg in st.session_state.messages:
                        if isinstance(msg, HumanMessage):
                            agent_messages.append({"role": "user", "content": msg.content})
                        elif isinstance(msg, AIMessage):
                            agent_messages.append({"role": "assistant", "content": msg.content})
                    
                    # Invoke agent with timeout handling
                    try:
                        agent_input = {"messages": agent_messages}
                        response = st.session_state.agent.invoke(agent_input)
                    except Exception as api_error:
                        if "429" in str(api_error) or "quota" in str(api_error).lower():
                            st.error("⚠️ API quota exceeded. Please try again in a few minutes or check your billing.")
                            st.info("💡 Tip: The system will automatically retry with a different model.")
                            raise
                        else:
                            raise
                    
                    # Extract AI response
                    if isinstance(response, dict) and "messages" in response:
                        updated_messages = response["messages"]
                        
                        # Find new messages (messages that weren't in our history)
                        our_message_count = len(st.session_state.messages)
                        new_messages = updated_messages[our_message_count:]
                        
                        # Extract the final AI response
                        ai_response = None
                        for msg in reversed(new_messages):
                            if hasattr(msg, "content") and msg.content:
                                # Skip tool call messages, get the actual response
                                if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                    ai_response = msg.content
                                    break
                        
                        if not ai_response and new_messages:
                            last_msg = new_messages[-1]
                            if hasattr(last_msg, "content"):
                                ai_response = last_msg.content
                            else:
                                ai_response = str(last_msg)
                        
                        if not ai_response:
                            ai_response = "I'm here to help! What would you like to know?"
                        
                        # Update session state with all messages from agent
                        # Convert LangGraph messages back to LangChain messages
                        from langchain_core.messages import HumanMessage as LC_HumanMessage, AIMessage as LC_AIMessage
                        
                        st.session_state.messages = []
                        for msg in updated_messages:
                            if hasattr(msg, "content"):
                                if isinstance(msg, LC_HumanMessage) or (hasattr(msg, "type") and msg.type == "human"):
                                    st.session_state.messages.append(LC_HumanMessage(content=msg.content))
                                elif isinstance(msg, LC_AIMessage) or (hasattr(msg, "type") and msg.type == "ai"):
                                    # Only add AI messages that aren't tool calls
                                    if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                        st.session_state.messages.append(LC_AIMessage(content=msg.content))
                        
                        st.write(ai_response)
                    else:
                        ai_response = str(response)
                        st.write(ai_response)
                        st.session_state.messages.append(AIMessage(content=ai_response))
                
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append(AIMessage(content=error_msg))
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=False):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    main()
