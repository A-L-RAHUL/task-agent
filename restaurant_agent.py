"""
Interactive LangChain Restaurant Ordering Agent (CLI)
----------------------------------------------------

Goal:
  - A simple, interactive command-line chatbot that acts like a waiter.
  - Uses *modern* LangChain (LCEL) with *message history memory* (RunnableWithMessageHistory).
  - NO tool-using agent, no retrieval, no databases—just a strong system prompt + chat history.

How it works (high level):
  1) We build a ChatPromptTemplate:
       [System message with menu JSON + instructions]
       [MessagesPlaceholder for chat history]
       [Human message: the user's latest input]
  2) We connect the prompt to an LLM (ChatGoogleGenerativeAI) using LCEL piping: prompt | llm | parser
  3) We wrap that runnable with RunnableWithMessageHistory so each turn is remembered.
  4) We run a while-loop CLI that sends user input into the chain and prints the response.

Environment:
  - Put your API key in a .env file (see .env.example).
  - GOOGLE_API_KEY is required (or OPENAI_API_KEY as fallback for compatibility).
"""

from __future__ import annotations

import os
import sys
from typing import Dict

from dotenv import load_dotenv

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_message_histories import ChatMessageHistory


# ---- 1) Load .env (so GOOGLE_API_KEY is available) --------------------------
load_dotenv()


# ---- 2) Configure the LLM ---------------------------------------------------
# Beginners: "model" is the name of the chat model; "temperature" controls randomness.
# Higher temperature => more creative and conversational responses.
MODEL_NAME = os.getenv("GOOGLE_MODEL", "gemini-pro")
TEMPERATURE = float(os.getenv("GOOGLE_TEMPERATURE", "0.7"))

# Check for API key (support both GOOGLE_API_KEY and OPENAI_API_KEY for compatibility)
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
    print(
        "Missing GOOGLE_API_KEY.\n"
        "1) Copy .env.example to .env\n"
        "2) Set GOOGLE_API_KEY in .env\n"
        "   Get your key from: https://makersuite.google.com/app/apikey\n"
        "3) Run again: python3 restaurant_agent.py",
        file=sys.stderr,
    )
    raise SystemExit(1)

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=TEMPERATURE,
    google_api_key=api_key,
)


# ---- 3) System prompt: conversational and flexible waiter persona ------------
# IMPORTANT:
# - The menu JSON is embedded directly here (as you requested).
# - All curly braces in JSON must be escaped (doubled) so LangChain doesn't treat them as template variables.
# - Be natural, conversational, and handle ANY type of question or interaction.
SYSTEM_PROMPT = """You are BiteBot, a friendly and conversational waiter at a restaurant. You're here to help customers in a natural, warm way.

Your personality:
- Be friendly, approachable, and conversational (like a real person, not a robot)
- Use natural language - respond as you would in a real conversation
- Be flexible and understanding - handle typos, slang, casual language, and any type of question
- Show genuine interest in helping the customer
- Keep the conversation flowing naturally

What you can help with:
- Answer ANY questions about the menu (ingredients, dietary info, prices, recommendations)
- Help customers decide what to order
- Take orders naturally (they don't have to be formal - "I'll have X" or "gimme Y" both work)
- Chat about food, make small talk, answer general questions
- Handle any type of input - questions, statements, casual chat, etc.

About the menu:
- You ONLY have items from the menu below. If asked for something not on the menu, politely say you don't have it and suggest something similar.
- Be smart about matching - "marg pizza", "marghsrita", "margherita" all mean "Margherita Pizza"
- Remember what the customer has ordered throughout the conversation
- When they're ready to finish, summarize their order and total, then say goodbye

Menu (JSON):
{{
  "Starters": [
    {{"name": "Garlic Bread", "price": 5.00, "dietary": "Vegetarian", "ingredients": ["bread", "garlic butter", "parsley"]}},
    {{"name": "Calamari", "price": 9.00, "dietary": "Seafood", "ingredients": ["squid", "flour", "lemon aioli"]}}
  ],
  "Mains": [
    {{"name": "Margherita Pizza", "price": 14.00, "dietary": "Vegetarian", "ingredients": ["dough", "tomato sauce", "mozzarella", "basil"]}},
    {{"name": "Spaghetti Carbonara", "price": 16.00, "dietary": "Contains Pork", "ingredients": ["pasta", "eggs", "pancetta", "parmesan", "black pepper"]}},
    {{"name": "Vegan Burger", "price": 15.00, "dietary": "Vegan", "ingredients": ["plant-based patty", "vegan bun", "lettuce", "tomato", "vegan mayo"]}}
  ],
  "Drinks": [
    {{"name": "Cola", "price": 3.00, "dietary": "Vegan", "ingredients": ["carbonated water", "sugar", "flavorings"]}},
    {{"name": "Sparkling Water", "price": 2.50, "dietary": "Vegan", "ingredients": ["carbonated water"]}}
  ]
}}

Remember: Be natural, conversational, and handle ANY type of interaction. Don't be rigid or structured - just be a helpful, friendly waiter having a conversation!
"""


# Build a prompt that includes:
# - System prompt (menu + rules)
# - A placeholder for prior conversation messages (memory)
# - The newest user message
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)


# LCEL chain:
# - prompt formats messages
# - llm generates an AIMessage
# - StrOutputParser turns the AIMessage into plain text for printing
base_chain = prompt | llm | StrOutputParser()


# ---- 4) Message history store (per session) --------------------------------
# RunnableWithMessageHistory needs a function that returns a history object for a session id.
#
# For this simple CLI app, we keep an in-memory dictionary. That means:
# - Memory persists *during the process run*.
# - If you close the program, the memory is lost (which is fine for this assignment).
_STORE: Dict[str, ChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Return the message history for a given session id (create if missing)."""
    if session_id not in _STORE:
        _STORE[session_id] = ChatMessageHistory()
    return _STORE[session_id]


# Wrap the chain with history.
# - input_messages_key: which key in invoke(...) contains the user's new message
# - history_messages_key: the variable name used in MessagesPlaceholder above
chain_with_memory = RunnableWithMessageHistory(
    base_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


# ---- 5) Interactive CLI loop ------------------------------------------------
def main() -> None:
    print("\nBiteBot: Hi! Welcome in. What can I get started for you today?\n")

    # In a real app you'd generate a unique session per user. For a local CLI,
    # a single fixed session id is enough to preserve conversation memory.
    session_id = "cli-session"

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBiteBot: Thanks for visiting—goodbye!")
            return

        if not user_text:
            continue

        # Simple manual exit commands (separate from "done/ready to pay",
        # which should be handled in-conversation by the model).
        if user_text.lower() in {"quit", "exit"}:
            print("BiteBot: Thanks for visiting—goodbye!")
            return

        # Invoke the chain. The "configurable" block is how we pass session_id
        # into RunnableWithMessageHistory.
        response_text: str = chain_with_memory.invoke(
            {"input": user_text},
            config={"configurable": {"session_id": session_id}},
        )

        print(f"\nBiteBot: {response_text}\n")


if __name__ == "__main__":
    main()
