"""
Database Migration Script
--------------------------

Run this script once to migrate existing database to support multi-restaurant functionality.
"""

import sqlite3
import os

DB_PATH = "restaurant.db"

def migrate():
    """Migrate database to support restaurants."""
    if not os.path.exists(DB_PATH):
        print("Database doesn't exist yet. It will be created on first run.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if restaurants table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='restaurants'")
        if not cursor.fetchone():
            # Create restaurants table
            cursor.execute("""
                CREATE TABLE restaurants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create default restaurant
            cursor.execute("""
                INSERT INTO restaurants (name, description)
                VALUES (?, ?)
            """, ("My Restaurant", "Welcome to our restaurant!"))
            
            print("✓ Created restaurants table")
        
        # Check if menu_items has restaurant_id column
        cursor.execute("PRAGMA table_info(menu_items)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "restaurant_id" not in columns:
            # Add restaurant_id column
            cursor.execute("ALTER TABLE menu_items ADD COLUMN restaurant_id INTEGER DEFAULT 1")
            cursor.execute("UPDATE menu_items SET restaurant_id = 1 WHERE restaurant_id IS NULL")
            print("✓ Added restaurant_id to menu_items")
        
        # Check if orders has restaurant_id column
        cursor.execute("PRAGMA table_info(orders)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "restaurant_id" not in columns:
            # Add restaurant_id column
            cursor.execute("ALTER TABLE orders ADD COLUMN restaurant_id INTEGER DEFAULT 1")
            cursor.execute("UPDATE orders SET restaurant_id = 1 WHERE restaurant_id IS NULL")
            print("✓ Added restaurant_id to orders")
        
        # Add foreign key constraints (SQLite doesn't support ALTER TABLE ADD CONSTRAINT, so we'll recreate)
        # For now, just ensure indexes exist
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_menu_items_restaurant ON menu_items(restaurant_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_restaurant ON orders(restaurant_id)")
            print("✓ Created indexes")
        except:
            pass
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
