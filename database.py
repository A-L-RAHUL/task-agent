"""
Database Utilities Module
--------------------------

This module provides database initialization and utility functions for the
restaurant management system using SQLite.

Tables:
- restaurants: Stores restaurant information (name, description, etc.)
- menu_items: Stores menu items with name, description, price, category, dietary info (linked to restaurant)
- orders: Stores customer orders with items, quantities, totals, and timestamps (linked to restaurant)
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Database file path
DB_PATH = "restaurant.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Create and return a database connection.
    
    Returns:
        SQLite connection object
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn


def init_database():
    """
    Initialize the database with required tables.
    Creates restaurants, menu_items, and orders tables if they don't exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create restaurants table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create menu_items table (now linked to restaurant)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            dietary TEXT,
            ingredients TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
            UNIQUE(restaurant_id, name)
        )
    """)
    
    # Create orders table (now linked to restaurant)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            items_json TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        )
    """)
    
    # Create indexes for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_menu_items_restaurant ON menu_items(restaurant_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_menu_items_name ON menu_items(name)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_restaurant ON orders(restaurant_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC)
    """)
    
    # Create default restaurant if none exists
    cursor.execute("SELECT COUNT(*) FROM restaurants")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO restaurants (name, description)
            VALUES (?, ?)
        """, ("My Restaurant", "Welcome to our restaurant!"))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Database initialized: {DB_PATH}")


def get_all_menu_items(restaurant_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all menu items from the database.
    
    Args:
        restaurant_id: Optional restaurant ID to filter by. If None, returns all items.
    
    Returns:
        List of menu item dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if restaurant_id:
        cursor.execute("""
            SELECT id, restaurant_id, name, description, price, category, dietary, ingredients
            FROM menu_items
            WHERE restaurant_id = ?
            ORDER BY category, name
        """, (restaurant_id,))
    else:
        cursor.execute("""
            SELECT id, restaurant_id, name, description, price, category, dietary, ingredients
            FROM menu_items
            ORDER BY category, name
        """)
    
    items = []
    for row in cursor.fetchall():
        items.append({
            "id": row["id"],
            "restaurant_id": row.get("restaurant_id", 1),  # Default to 1 for backward compatibility
            "name": row["name"],
            "description": row["description"] or "",
            "price": float(row["price"]),
            "category": row["category"],
            "dietary": row["dietary"] or "",
            "ingredients": row["ingredients"] or ""
        })
    
    conn.close()
    return items


def get_menu_item_by_name(item_name: str) -> Optional[Dict[str, Any]]:
    """
    Find a menu item by name (case-insensitive, flexible matching).
    
    Args:
        item_name: The name of the item to search for
        
    Returns:
        Menu item dictionary if found, None otherwise
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Try exact match first (case-insensitive)
    cursor.execute("""
        SELECT id, name, description, price, category, dietary, ingredients
        FROM menu_items
        WHERE LOWER(name) = LOWER(?)
    """, (item_name.strip(),))
    
    row = cursor.fetchone()
    if row:
        conn.close()
        return {
            "id": row["id"],
            "name": row["name"],
            "description": row["description"] or "",
            "price": float(row["price"]),
            "category": row["category"],
            "dietary": row["dietary"] or "",
            "ingredients": row["ingredients"] or ""
        }
    
    # Try partial match
    cursor.execute("""
        SELECT id, name, description, price, category, dietary, ingredients
        FROM menu_items
        WHERE LOWER(name) LIKE LOWER(?)
    """, (f"%{item_name.strip()}%",))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "name": row["name"],
            "description": row["description"] or "",
            "price": float(row["price"]),
            "category": row["category"],
            "dietary": row["dietary"] or "",
            "ingredients": row["ingredients"] or ""
        }
    
    return None


def add_menu_item(
    name: str,
    description: str,
    price: float,
    category: str,
    restaurant_id: int = 1,
    dietary: str = "",
    ingredients: str = ""
) -> int:
    """
    Add a new menu item to the database.
    
    Args:
        name: Item name (must be unique)
        description: Item description
        price: Item price
        category: Item category (e.g., "Appetizers", "Mains", "Drinks")
        dietary: Dietary information (e.g., "Vegetarian", "Vegan", "Contains Pork")
        ingredients: Comma-separated list of ingredients
        
    Returns:
        The ID of the newly created menu item
        
    Raises:
        sqlite3.IntegrityError: If item name already exists
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO menu_items (restaurant_id, name, description, price, category, dietary, ingredients)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (restaurant_id, name.strip(), description.strip(), price, category.strip(), dietary.strip(), ingredients.strip()))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Menu item '{name}' already exists")


def update_menu_item(
    item_id: int,
    name: str = None,
    description: str = None,
    price: float = None,
    category: str = None,
    dietary: str = None,
    ingredients: str = None
) -> bool:
    """
    Update an existing menu item.
    
    Args:
        item_id: The ID of the item to update
        name: New name (optional)
        description: New description (optional)
        price: New price (optional)
        category: New category (optional)
        dietary: New dietary info (optional)
        ingredients: New ingredients (optional)
        
    Returns:
        True if update was successful, False if item not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build dynamic UPDATE query
    updates = []
    params = []
    
    if name is not None:
        updates.append("name = ?")
        params.append(name.strip())
    if description is not None:
        updates.append("description = ?")
        params.append(description.strip())
    if price is not None:
        updates.append("price = ?")
        params.append(price)
    if category is not None:
        updates.append("category = ?")
        params.append(category.strip())
    if dietary is not None:
        updates.append("dietary = ?")
        params.append(dietary.strip())
    if ingredients is not None:
        updates.append("ingredients = ?")
        params.append(ingredients.strip())
    
    if not updates:
        conn.close()
        return False
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(item_id)
    
    query = f"UPDATE menu_items SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, params)
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success


def delete_menu_item(item_id: int) -> bool:
    """
    Delete a menu item from the database.
    
    Args:
        item_id: The ID of the item to delete
        
    Returns:
        True if deletion was successful, False if item not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
    success = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return success


def create_order(items_json: str, total_price: float, restaurant_id: int = 1, status: str = "pending") -> int:
    """
    Create a new order in the database.
    
    Args:
        items_json: JSON string containing order items with quantities
        total_price: Total price of the order
        status: Order status (default: "pending")
        
    Returns:
        The ID of the newly created order
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO orders (restaurant_id, items_json, total_price, status)
        VALUES (?, ?, ?, ?)
    """, (restaurant_id, items_json, total_price, status))
    
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return order_id


def get_all_orders(restaurant_id: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve all orders from the database, most recent first.
    
    Args:
        restaurant_id: Optional restaurant ID to filter by. If None, returns all orders.
        limit: Maximum number of orders to retrieve
        
    Returns:
        List of order dictionaries
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if restaurant_id:
        cursor.execute("""
            SELECT o.id, o.restaurant_id, r.name as restaurant_name,
                   o.items_json, o.total_price, o.status, o.created_at
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.id
            WHERE o.restaurant_id = ?
            ORDER BY o.created_at DESC
            LIMIT ?
        """, (restaurant_id, limit))
    else:
        cursor.execute("""
            SELECT o.id, o.restaurant_id, r.name as restaurant_name,
                   o.items_json, o.total_price, o.status, o.created_at
            FROM orders o
            JOIN restaurants r ON o.restaurant_id = r.id
            ORDER BY o.created_at DESC
            LIMIT ?
        """, (limit,))
    
    orders = []
    for row in cursor.fetchall():
        orders.append({
            "id": row["id"],
            "restaurant_id": row.get("restaurant_id", 1),
            "restaurant_name": row.get("restaurant_name", "Unknown"),
            "items_json": row["items_json"],
            "total_price": float(row["total_price"]),
            "status": row["status"],
            "created_at": row["created_at"]
        })
    
    conn.close()
    return orders


def update_order_status(order_id: int, status: str) -> bool:
    """
    Update the status of an order.
    
    Args:
        order_id: The ID of the order to update
        status: New status (e.g., "pending", "preparing", "ready", "completed")
        
    Returns:
        True if update was successful, False if order not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE orders SET status = ? WHERE id = ?
    """, (status, order_id))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success


def format_menu_for_prompt(menu_items: List[Dict[str, Any]]) -> str:
    """
    Format menu items as a readable string for LLM prompts.
    
    Args:
        menu_items: List of menu item dictionaries
        
    Returns:
        Formatted menu string
    """
    if not menu_items:
        return "No menu items available."
    
    # Group by category
    by_category = {}
    for item in menu_items:
        category = item.get("category", "Other")
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(item)
    
    lines = []
    for category in sorted(by_category.keys()):
        lines.append(f"\n{category}:")
        for item in sorted(by_category[category], key=lambda x: x["name"]):
            lines.append(f"  - {item['name']} (${item['price']:.2f}) - {item.get('description', '')}")
            if item.get("dietary"):
                lines.append(f"    Dietary: {item['dietary']}")
            if item.get("ingredients"):
                ingredients = item["ingredients"].split(",") if isinstance(item["ingredients"], str) else item["ingredients"]
                if isinstance(ingredients, list):
                    lines.append(f"    Ingredients: {', '.join([i.strip() for i in ingredients])}")
    
    return "\n".join(lines)


# ==================== RESTAURANT MANAGEMENT FUNCTIONS ====================

def get_all_restaurants() -> List[Dict[str, Any]]:
    """Get all restaurants."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM restaurants ORDER BY name")
    restaurants = []
    for row in cursor.fetchall():
        restaurants.append({
            "id": row["id"],
            "name": row["name"],
            "description": row["description"] or ""
        })
    conn.close()
    return restaurants


def get_restaurant(restaurant_id: int) -> Optional[Dict[str, Any]]:
    """Get restaurant by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM restaurants WHERE id = ?", (restaurant_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row["id"],
            "name": row["name"],
            "description": row["description"] or ""
        }
    return None


def add_restaurant(name: str, description: str = "") -> int:
    """Add a new restaurant."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO restaurants (name, description) VALUES (?, ?)", 
                       (name.strip(), description.strip()))
        restaurant_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return restaurant_id
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError(f"Restaurant '{name}' already exists")


def update_restaurant(restaurant_id: int, name: str = None, description: str = None) -> bool:
    """Update restaurant."""
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name.strip())
    if description is not None:
        updates.append("description = ?")
        params.append(description.strip())
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(restaurant_id)
        cursor.execute(f"UPDATE restaurants SET {', '.join(updates)} WHERE id = ?", params)
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    conn.close()
    return False


def delete_restaurant(restaurant_id: int) -> bool:
    """Delete restaurant (cascades to menu items and orders)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM restaurants WHERE id = ?", (restaurant_id,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success


def get_menu_items_by_restaurant(restaurant_id: int) -> List[Dict[str, Any]]:
    """Get menu items for a specific restaurant."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, restaurant_id, name, description, price, category, dietary, ingredients
        FROM menu_items
        WHERE restaurant_id = ?
        ORDER BY category, name
    """, (restaurant_id,))
    items = []
    for row in cursor.fetchall():
        items.append({
            "id": row["id"],
            "restaurant_id": row["restaurant_id"],
            "name": row["name"],
            "description": row["description"] or "",
            "price": float(row["price"]),
            "category": row["category"],
            "dietary": row["dietary"] or "",
            "ingredients": row["ingredients"] or ""
        })
    conn.close()
    return items


def get_all_menu_items_all_restaurants() -> List[Dict[str, Any]]:
    """Get all menu items from all restaurants with restaurant info."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mi.id, mi.restaurant_id, r.name as restaurant_name,
               mi.name, mi.description, mi.price, mi.category, mi.dietary, mi.ingredients
        FROM menu_items mi
        JOIN restaurants r ON mi.restaurant_id = r.id
        ORDER BY r.name, mi.category, mi.name
    """)
    items = []
    for row in cursor.fetchall():
        items.append({
            "id": row["id"],
            "restaurant_id": row["restaurant_id"],
            "restaurant_name": row["restaurant_name"],
            "name": row["name"],
            "description": row["description"] or "",
            "price": float(row["price"]),
            "category": row["category"],
            "dietary": row["dietary"] or "",
            "ingredients": row["ingredients"] or ""
        })
    conn.close()
    return items
