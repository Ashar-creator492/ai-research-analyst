from mcp.server.fastmcp import FastMCP
import os
from tavily import TavilyClient
from dotenv import load_dotenv

mcp = FastMCP("Research Analyst MCP Server")

load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

@mcp.tool()
def search_web(query: str):
    """Search the web for current information."""

    results = tavily.search(
        query=query,
        max_results=3
    )

    return results["results"]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    
