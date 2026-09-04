import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

MCP_URL = os.getenv("MCP_URL")

client = MultiServerMCPClient(
    {
        "research_server": {
            "transport": "streamable_http",
            "url": MCP_URL
        }
    }
)