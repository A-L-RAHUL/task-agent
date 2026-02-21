## Interactive LangChain Restaurant Ordering Agent (LangGraph)

This project is a simple, interactive Python chatbot using **modern LangGraph** with `create_react_agent`.
It acts as a restaurant order-taking agent ("BiteBot") using a tool-based architecture.

### Architecture

- **menu.py**: Structured menu data with helper functions
- **agent.py**: LangGraph agent with `place_order` tool using `create_react_agent`
- **main.py**: Interactive CLI interface with conversation history

### Setup

- **Python**: 3.10+
- **Install dependencies**:

```bash
python3 -m pip install -r requirements.txt
```

- **Configure environment**:

```bash
cp .env.example .env
```

Open `.env` and set:

- `GOOGLE_API_KEY=...` (get from https://makersuite.google.com/app/apikey)

Optionally:

- `GOOGLE_MODEL` (default: `gemini-2.5-flash`)
- `GOOGLE_TEMPERATURE` (default: `0.7`)

### Run

```bash
python3 main.py
```

### Features

- **Tool-based ordering**: Uses `place_order` tool to process orders
- **Conversation memory**: Maintains chat history throughout the session
- **Flexible input**: Handles typos, informal language, and variations
- **Menu queries**: Answers questions about ingredients, dietary info, prices
- **Modern LangGraph**: Uses `create_react_agent` (not deprecated patterns)

### Exit

Type `quit`, `exit`, `bye`, or `goodbye`, or press `Ctrl+C`.
