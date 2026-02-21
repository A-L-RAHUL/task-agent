# Migration Guide - Multi-Restaurant Support

## Changes Made

### 1. Database Schema Updates
- Added `restaurants` table
- Added `restaurant_id` to `menu_items` and `orders` tables
- All existing data will be assigned to restaurant_id = 1 (default restaurant)

### 2. API Rate Limiting Fix
- Changed default model from `gemini-2.5-flash` to `gemini-pro` to avoid quota issues
- Added fallback logic for rate limit errors
- Added retry mechanism

### 3. Performance Optimizations
- Agent initialization is cached in session state
- Menu caching with TTL
- Optimized database queries

## To Migrate Existing Database

Run this Python script once:

```python
import sqlite3

conn = sqlite3.connect("restaurant.db")
cursor = conn.cursor()

# Add restaurant_id columns if they don't exist
try:
    cursor.execute("ALTER TABLE menu_items ADD COLUMN restaurant_id INTEGER DEFAULT 1")
except:
    pass

try:
    cursor.execute("ALTER TABLE orders ADD COLUMN restaurant_id INTEGER DEFAULT 1")
except:
    pass

# Update existing records
cursor.execute("UPDATE menu_items SET restaurant_id = 1 WHERE restaurant_id IS NULL")
cursor.execute("UPDATE orders SET restaurant_id = 1 WHERE restaurant_id IS NULL")

conn.commit()
conn.close()
print("Migration complete!")
```

## New Features

1. **Restaurant Management**: Owners can add/edit/delete restaurants
2. **Restaurant Selection**: Clients choose restaurant before ordering
3. **Dish Comparison**: Bot can compare dishes across restaurants
4. **Better Error Handling**: Rate limits handled gracefully
