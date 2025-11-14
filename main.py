from dotenv import load_dotenv
import os
import asyncio
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

# Load environment variables
load_dotenv()
print("✅ ADK components imported successfully.")

try:
    # Get API key from .env file
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    print(GOOGLE_API_KEY)
    if not GOOGLE_API_KEY:
        raise ValueError("Missing GOOGLE_API_KEY in environment variables.")

    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    print("✅ Gemini API key setup complete.")
    
    # Define agent
    root_agent = Agent(
        name="helpful_assistant",
        model="gemini-2.5-flash",
        description="A simple agent that can answer general questions.",
        instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
        tools=[google_search],
    )
    print("✅ Root Agent defined.")

    # Create runner (in-memory execution)
    runner = InMemoryRunner(agent=root_agent)
    print("✅ Runner created.")

    # Run query
    response = asyncio.run(
     runner.run_debug("What is Agent Development Kit from Google? What languages is the SDK available in?")
    )

    print(response)

except Exception as e:
    print(f"🔑 Error : {e}")
