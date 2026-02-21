# Multi-Server Streamlit Restaurant Application

This project extends the LangGraph restaurant agent into a multi-interface Streamlit application with two separate apps that communicate via a shared SQLite database.

## Architecture

- **database.py**: SQLite database utilities and initialization
- **owner_app.py**: Restaurant owner dashboard (authentication, menu management, order tracking)
- **client_app.py**: Customer-facing chat interface with LangGraph agent
- **restaurant.db**: Shared SQLite database (created automatically)

## Setup

1. **Install dependencies:**
```bash
python3 -m pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY
```

3. **Initialize database:**
The database is automatically initialized when you run either app for the first time.

## Running the Applications

### Owner Dashboard
```bash
streamlit run owner_app.py
```

**Login Credentials:**
- Username: `owner`
- Password: `admin123`

**Features:**
- Add, edit, delete menu items
- View incoming orders in real-time
- Update order status
- Auto-refresh dashboard

### Client Order Bot
```bash
streamlit run client_app.py
```

**Features:**
- Chat interface with BiteBot (LangGraph agent)
- Dynamic menu loading from database
- Order placement that saves to database
- Menu display in sidebar

## Database Schema

### menu_items Table
- `id`: INTEGER PRIMARY KEY
- `name`: TEXT (UNIQUE)
- `description`: TEXT
- `price`: REAL
- `category`: TEXT
- `dietary`: TEXT
- `ingredients`: TEXT
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

### orders Table
- `id`: INTEGER PRIMARY KEY
- `items_json`: TEXT (JSON string of order items)
- `total_price`: REAL
- `status`: TEXT (pending, preparing, ready, completed)
- `created_at`: TIMESTAMP

## Key Features

### Dynamic Menu Injection
The LangGraph agent receives the menu directly from the database on startup. The system prompt explicitly instructs the model to:
- ONLY discuss items in the provided menu
- NOT hallucinate or invent menu items
- Use exact prices and descriptions from the database

### State Management
- Chat history is maintained in `st.session_state.messages`
- Agent is cached in session state to avoid re-initialization
- Menu is cached for 10 seconds to reduce database load

### Order Processing
When a customer places an order:
1. The `place_order` tool calculates the total using exact database prices
2. Order is saved to the `orders` table as JSON
3. Order immediately appears on the owner dashboard

## Best Practices Implemented

- **Caching**: Menu cached with `@st.cache_data(ttl=10)` to reduce DB queries
- **Database Safety**: Proper connection handling with context managers
- **Error Handling**: Graceful error messages for missing API keys, empty menus, etc.
- **State Management**: Proper session state usage to maintain chat history
- **Security**: Simple authentication (for demo; use proper auth in production)

## Notes

- Both apps can run simultaneously on different ports
- The database file (`restaurant.db`) is shared between both apps
- Menu changes in owner app are reflected in client app after cache refresh
- Orders placed in client app appear immediately in owner dashboard
