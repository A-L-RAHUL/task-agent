"""
Defines the restaurant menu structure.
Provides a simple dictionary mapping categories to lists of items.
"""

MENU = {
    "Appetizers": [
        {"name": "Garlic Bread", "price": 5.00, "description": "Toasted baguette slices with garlic butter and herbs."},
        {"name": "Mozzarella Sticks", "price": 7.50, "description": "Crispy fried mozzarella sticks served with marinara sauce."}
    ],
    "Mains": [
        {"name": "Classic Burger", "price": 10.00, "description": "Beef patty, lettuce, tomato, house sauce."},
        {"name": "Margherita Pizza", "price": 12.00, "description": "Classic pizza with tomato sauce, fresh mozzarella, and basil."},
        {"name": "Grilled Chicken Salad", "price": 11.50, "description": "Mixed greens, grilled chicken breast, cherry tomatoes, and balsamic vinaigrette."}
    ],
    "Drinks": [
        {"name": "Soda", "price": 2.50, "description": "Cola, Lemon-Lime, or Orange."},
        {"name": "Craft Beer", "price": 6.00, "description": "Local IPA or Stout."},
        {"name": "Water", "price": 0.00, "description": "Tap water or sparkling water ($2.00)."}
    ]
}

def get_menu_string() -> str:
    """Formats the menu into a readable string for the LLM context."""
    menu_str = "--- RESTAURANT MENU ---\n\n"
    for category, items in MENU.items():
        menu_str += f"{category}:\n"
        for item in items:
            menu_str += f"- {item['name']} (${item['price']:.2f}): {item['description']}\n"
        menu_str += "\n"
    return menu_str.strip()
