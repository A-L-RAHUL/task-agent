"""
Menu Data Module
----------------

This module contains the restaurant menu structure with categories, items,
descriptions, prices, dietary information, and ingredients.

The menu is structured as a dictionary for easy access and manipulation.
"""

from typing import Dict, List, Optional, Any

# Menu structure: category -> list of items
# Each item is a dictionary with: name, description, price, dietary, ingredients
MENU: Dict[str, List[Dict[str, Any]]] = {
    "Appetizers": [
        {
            "name": "Garlic Bread",
            "description": "Freshly baked bread with garlic butter and parsley",
            "price": 5.00,
            "dietary": "Vegetarian",
            "ingredients": ["bread", "garlic butter", "parsley"]
        },
        {
            "name": "Calamari",
            "description": "Crispy fried squid rings served with lemon aioli",
            "price": 9.00,
            "dietary": "Seafood",
            "ingredients": ["squid", "flour", "lemon aioli"]
        }
    ],
    "Mains": [
        {
            "name": "Margherita Pizza",
            "description": "Classic pizza with tomato sauce, mozzarella, and fresh basil",
            "price": 14.00,
            "dietary": "Vegetarian",
            "ingredients": ["dough", "tomato sauce", "mozzarella", "basil"]
        },
        {
            "name": "Spaghetti Carbonara",
            "description": "Creamy pasta with eggs, pancetta, parmesan, and black pepper",
            "price": 16.00,
            "dietary": "Contains Pork",
            "ingredients": ["pasta", "eggs", "pancetta", "parmesan", "black pepper"]
        },
        {
            "name": "Vegan Burger",
            "description": "Plant-based patty with vegan bun, lettuce, tomato, and vegan mayo",
            "price": 15.00,
            "dietary": "Vegan",
            "ingredients": ["plant-based patty", "vegan bun", "lettuce", "tomato", "vegan mayo"]
        }
    ],
    "Drinks": [
        {
            "name": "Cola",
            "description": "Refreshing carbonated cola drink",
            "price": 3.00,
            "dietary": "Vegan",
            "ingredients": ["carbonated water", "sugar", "flavorings"]
        },
        {
            "name": "Sparkling Water",
            "description": "Pure carbonated water",
            "price": 2.50,
            "dietary": "Vegan",
            "ingredients": ["carbonated water"]
        }
    ]
}


def get_item_by_name(item_name: str) -> Optional[Dict[str, Any]]:
    """
    Search for a menu item by name (case-insensitive, flexible matching).
    
    Args:
        item_name: The name of the item to search for
        
    Returns:
        The item dictionary if found, None otherwise
    """
    item_name_lower = item_name.lower().strip()
    
    for category_items in MENU.values():
        for item in category_items:
            # Exact match (case-insensitive)
            if item["name"].lower() == item_name_lower:
                return item
            # Partial match (contains)
            if item_name_lower in item["name"].lower() or item["name"].lower() in item_name_lower:
                return item
    
    return None


def get_all_items() -> List[Dict[str, Any]]:
    """
    Get all menu items flattened into a single list.
    
    Returns:
        List of all menu items
    """
    all_items = []
    for category_items in MENU.values():
        all_items.extend(category_items)
    return all_items


def format_menu_for_prompt() -> str:
    """
    Format the menu as a readable string for inclusion in prompts.
    
    Returns:
        Formatted menu string
    """
    lines = []
    for category, items in MENU.items():
        lines.append(f"\n{category}:")
        for item in items:
            lines.append(
                f"  - {item['name']} (${item['price']:.2f}) - {item['description']}"
            )
            lines.append(f"    Dietary: {item['dietary']}")
            lines.append(f"    Ingredients: {', '.join(item['ingredients'])}")
    
    return "\n".join(lines)
