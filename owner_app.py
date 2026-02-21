"""
Restaurant Owner Dashboard - Streamlit App
------------------------------------------

This Streamlit application provides a dashboard for restaurant owners to:
- Authenticate and access the dashboard
- Manage menu items (add, edit, delete)
- View incoming orders in real-time

Run with: streamlit run owner_app.py
"""

import streamlit as st
import json
from datetime import datetime
from database import (
    init_database,
    get_all_menu_items,
    add_menu_item,
    update_menu_item,
    delete_menu_item,
    get_all_orders,
    update_order_status,
    get_all_restaurants,
    get_restaurant,
    add_restaurant,
    update_restaurant,
    delete_restaurant,
    get_menu_items_by_restaurant
)

# Page configuration
st.set_page_config(
    page_title="Restaurant Owner Dashboard",
    page_icon="🍽️",
    layout="wide"
)

# Initialize database on startup
if "db_initialized" not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

# Simple authentication
OWNER_USERNAME = "owner"
OWNER_PASSWORD = "admin123"  # In production, use proper authentication!


def check_authentication():
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False)


def login_page():
    """Display login page."""
    st.title("🍽️ Restaurant Owner Dashboard")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if username == OWNER_USERNAME and password == OWNER_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")
        
        st.info("**Demo Credentials:**\n- Username: `owner`\n- Password: `admin123`")


def menu_management_section():
    """Menu management interface."""
    st.header("📋 Menu Management")
    
    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["Add Item", "Edit Item", "Delete Item"])
    
    with tab1:
        st.subheader("Add New Menu Item")
        
        # Get selected restaurant
        restaurant_id = st.session_state.get("selected_restaurant_id", 1)
        
        with st.form("add_item_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Item Name *", placeholder="e.g., Margherita Pizza")
                category = st.selectbox(
                    "Category *",
                    ["Appetizers", "Mains", "Drinks", "Desserts", "Sides"]
                )
                price = st.number_input("Price ($) *", min_value=0.0, step=0.01, format="%.2f")
            
            with col2:
                description = st.text_area("Description", placeholder="Brief description of the item")
                dietary = st.text_input("Dietary Info", placeholder="e.g., Vegetarian, Vegan, Contains Pork")
                ingredients = st.text_input("Ingredients", placeholder="Comma-separated list")
            
            submitted = st.form_submit_button("Add Item", type="primary", use_container_width=True)
            
            if submitted:
                if not name or not price:
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    try:
                        item_id = add_menu_item(
                            name=name,
                            description=description,
                            price=price,
                            category=category,
                            restaurant_id=restaurant_id,
                            dietary=dietary,
                            ingredients=ingredients
                        )
                        st.success(f"✅ Menu item '{name}' added successfully! (ID: {item_id})")
                        st.cache_data.clear()  # Clear menu cache
                    except ValueError as e:
                        st.error(f"❌ Error: {e}")
    
    with tab2:
        st.subheader("Edit Existing Menu Item")
        
        # Get menu items for selected restaurant
        restaurant_id = st.session_state.get("selected_restaurant_id", 1)
        menu_items = get_menu_items_by_restaurant(restaurant_id)
        
        if not menu_items:
            st.info("No menu items available. Add some items first!")
        else:
            item_names = [f"{item['name']} (${item['price']:.2f})" for item in menu_items]
            selected_display = st.selectbox("Select Item to Edit", item_names)
            
            if selected_display:
                # Find the selected item
                selected_item = next(
                    item for item in menu_items
                    if f"{item['name']} (${item['price']:.2f})" == selected_display
                )
                
                with st.form("edit_item_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Item Name", value=selected_item["name"])
                        new_category = st.selectbox(
                            "Category",
                            ["Appetizers", "Mains", "Drinks", "Desserts", "Sides"],
                            index=["Appetizers", "Mains", "Drinks", "Desserts", "Sides"].index(selected_item["category"])
                        )
                        new_price = st.number_input("Price ($)", min_value=0.0, step=0.01, value=selected_item["price"], format="%.2f")
                    
                    with col2:
                        new_description = st.text_area("Description", value=selected_item["description"])
                        new_dietary = st.text_input("Dietary Info", value=selected_item["dietary"])
                        new_ingredients = st.text_input("Ingredients", value=selected_item["ingredients"])
                    
                    submitted = st.form_submit_button("Update Item", type="primary", use_container_width=True)
                    
                    if submitted:
                        success = update_menu_item(
                            item_id=selected_item["id"],
                            name=new_name if new_name != selected_item["name"] else None,
                            description=new_description if new_description != selected_item["description"] else None,
                            price=new_price if new_price != selected_item["price"] else None,
                            category=new_category if new_category != selected_item["category"] else None,
                            dietary=new_dietary if new_dietary != selected_item["dietary"] else None,
                            ingredients=new_ingredients if new_ingredients != selected_item["ingredients"] else None
                        )
                        
                        if success:
                            st.success(f"✅ Menu item updated successfully!")
                            st.cache_data.clear()  # Clear menu cache
                        else:
                            st.error("❌ Failed to update menu item")
    
    with tab3:
        st.subheader("Delete Menu Item")
        
        restaurant_id = st.session_state.get("selected_restaurant_id", 1)
        menu_items = get_menu_items_by_restaurant(restaurant_id)
        
        if not menu_items:
            st.info("No menu items available.")
        else:
            item_names = [f"{item['name']} (${item['price']:.2f})" for item in menu_items]
            selected_display = st.selectbox("Select Item to Delete", item_names, key="delete_select")
            
            if selected_display:
                selected_item = next(
                    item for item in menu_items
                    if f"{item['name']} (${item['price']:.2f})" == selected_display
                )
                
                st.warning(f"⚠️ Are you sure you want to delete '{selected_item['name']}'?")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Delete", type="primary", use_container_width=True):
                        success = delete_menu_item(selected_item["id"])
                        if success:
                            st.success(f"✅ '{selected_item['name']}' deleted successfully!")
                            st.cache_data.clear()  # Clear menu cache
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete menu item")
                
                with col2:
                    if st.button("Cancel", use_container_width=True):
                        st.rerun()


@st.cache_data(ttl=5)  # Cache for 5 seconds to reduce DB load
def get_cached_orders(restaurant_id=None):
    """Get orders with caching."""
    return get_all_orders(restaurant_id=restaurant_id, limit=100)


def order_dashboard_section():
    """Order tracking dashboard."""
    st.header("📊 Order Dashboard")
    
    # Auto-refresh option
    auto_refresh = st.checkbox("Auto-refresh (every 5 seconds)", value=False)
    
    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()
    
    # Manual refresh button
    if st.button("🔄 Refresh Orders", use_container_width=False):
        st.cache_data.clear()
        st.rerun()
    
    # Get orders for selected restaurant
    restaurant_id = st.session_state.get("selected_restaurant_id", None)
    orders = get_cached_orders(restaurant_id) if restaurant_id else get_cached_orders()
    
    if not orders:
        st.info("📭 No orders yet. Orders will appear here when customers place them.")
    else:
        st.metric("Total Orders", len(orders))
        
        # Display orders
        for order in orders:
            with st.expander(f"Order #{order['id']} - ${order['total_price']:.2f} - {order['created_at']}", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    # Parse order items
                    try:
                        items = json.loads(order["items_json"])
                        st.write("**Items:**")
                        for item in items:
                            st.write(f"- {item['quantity']}x {item['name']} @ ${item['unit_price']:.2f} = ${item['total']:.2f}")
                    except json.JSONDecodeError:
                        st.write(f"Raw data: {order['items_json']}")
                
                with col2:
                    st.write(f"**Total:** ${order['total_price']:.2f}")
                    st.write(f"**Status:** {order['status']}")
                
                with col3:
                    # Status update
                    new_status = st.selectbox(
                        "Update Status",
                        ["pending", "preparing", "ready", "completed"],
                        index=["pending", "preparing", "ready", "completed"].index(order["status"]),
                        key=f"status_{order['id']}"
                    )
                    
                    if new_status != order["status"]:
                        if st.button("Update", key=f"update_{order['id']}"):
                            update_order_status(order["id"], new_status)
                            st.success("Status updated!")
                            st.cache_data.clear()
                            st.rerun()


def restaurant_management_section():
    """Restaurant management interface."""
    st.header("🏢 Restaurant Management")
    
    # Get current restaurant selection
    restaurants = get_all_restaurants()
    
    if "selected_restaurant_id" not in st.session_state:
        st.session_state.selected_restaurant_id = restaurants[0]["id"] if restaurants else None
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if restaurants:
            restaurant_options = {f"{r['name']}": r['id'] for r in restaurants}
            selected_name = st.selectbox(
                "Select Restaurant to Manage",
                options=list(restaurant_options.keys()),
                index=0 if st.session_state.selected_restaurant_id else None,
                key="restaurant_selector"
            )
            st.session_state.selected_restaurant_id = restaurant_options[selected_name]
            selected_restaurant = get_restaurant(st.session_state.selected_restaurant_id)
            if selected_restaurant:
                st.info(f"**Current Restaurant:** {selected_restaurant['name']}")
                if selected_restaurant['description']:
                    st.caption(selected_restaurant['description'])
        else:
            st.warning("No restaurants found. Please add a restaurant first.")
    
    with col2:
        with st.expander("➕ Add Restaurant"):
            with st.form("add_restaurant_form", clear_on_submit=True):
                new_name = st.text_input("Restaurant Name *")
                new_description = st.text_area("Description")
                if st.form_submit_button("Add Restaurant", type="primary"):
                    if new_name:
                        try:
                            add_restaurant(new_name, new_description)
                            st.success(f"✅ Restaurant '{new_name}' added!")
                            st.cache_data.clear()
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ {e}")
                    else:
                        st.error("Please enter a restaurant name")
    
    # Edit/Delete current restaurant
    if st.session_state.selected_restaurant_id and selected_restaurant:
        with st.expander("✏️ Edit Restaurant"):
            with st.form("edit_restaurant_form"):
                edit_name = st.text_input("Name", value=selected_restaurant['name'])
                edit_description = st.text_area("Description", value=selected_restaurant['description'])
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update", type="primary"):
                        update_restaurant(st.session_state.selected_restaurant_id, edit_name, edit_description)
                        st.success("✅ Restaurant updated!")
                        st.cache_data.clear()
                        st.rerun()
                with col2:
                    if st.form_submit_button("Delete Restaurant", type="secondary"):
                        delete_restaurant(st.session_state.selected_restaurant_id)
                        st.success("✅ Restaurant deleted!")
                        st.session_state.selected_restaurant_id = restaurants[0]["id"] if len(restaurants) > 1 else None
                        st.cache_data.clear()
                        st.rerun()


def main():
    """Main application logic."""
    if not check_authentication():
        login_page()
    else:
        # Logged in - show dashboard
        st.title("🍽️ Restaurant Owner Dashboard")
        
        # Logout button
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.pop("username", None)
                st.rerun()
        
        st.markdown("---")
        
        # Restaurant management section
        restaurant_management_section()
        st.markdown("---")
        
        # Main sections (now restaurant-specific)
        menu_management_section()
        st.markdown("---")
        order_dashboard_section()


if __name__ == "__main__":
    main()
