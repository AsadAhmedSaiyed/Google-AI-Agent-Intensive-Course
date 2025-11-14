import uuid
import base64
from PIL import Image
import io
import base64
from dotenv import load_dotenv
import os
import asyncio
load_dotenv()
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from google.adk.apps.app import App, ResumabilityConfig
from google.adk.tools.function_tool import FunctionTool

print("✅ ADK components imported successfully.")

 # Get API key from .env file
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
print(GOOGLE_API_KEY)
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in environment variables.")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
print("✅ Gemini API key setup complete.")
   

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# MCP integration with Everything Server
mcp_image_server = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",  # Run MCP server via npx
            args=[
                "-y",  # Argument for npx to auto-confirm install
                "@modelcontextprotocol/server-everything",
            ],
            tool_filter=["getTinyImage"],
        ),
        timeout=30,
    )
)

print("✅ MCP Tool created")

# Create image agent with MCP integration
image_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="image_agent",
    instruction="Use the MCP Tool to generate images for user queries",
    tools=[mcp_image_server],
)

runner = InMemoryRunner(agent=image_agent)

response = asyncio.run(
    runner.run_debug("Provide a sample tiny image", verbose=True)
)

for event in response:
    if not event.content:
        continue

    for part in event.content.parts:
        if not hasattr(part, "function_response"):
            continue

        fn = part.function_response
        content_list = fn.response.get("content", [])

        for item in content_list:
            if item.get("type") == "image":
                raw = item["data"]

                import base64, io
                from PIL import Image

                img_bytes = base64.b64decode(raw)
                img = Image.open(io.BytesIO(img_bytes))
                img.show()
