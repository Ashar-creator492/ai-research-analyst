import asyncio
from src.mcp.client import client


async def main():
    tools = await client.get_tools()

    print("\n=== MCP TOOLS ===")

    for tool in tools:
        print(tool.name)


if __name__ == "__main__":
    asyncio.run(main())