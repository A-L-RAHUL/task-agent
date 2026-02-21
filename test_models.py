import os
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

MODELS_TO_TEST = [
    "gemini-2.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.0-pro",
    "gemini-pro"
]

for m in MODELS_TO_TEST:
    print(f"Testing {m}...")
    try:
        # Disable retries to fail fast
        llm = ChatGoogleGenerativeAI(model=m, temperature=0.2, max_retries=0)
        resp = llm.invoke([HumanMessage(content="Hi")])
        print(f"Success with {m}: {resp.content}")
        # If one works, we are good to use it in our agent!
        break
    except Exception as e:
        print(f"Failed {m}: {e}\n")
