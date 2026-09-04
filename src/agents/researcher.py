from langchain_groq import ChatGroq
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage

from src.mcp.client import client


class State(TypedDict):
    messages: Annotated[list, add_messages]
    research: str
    search_count: int


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


def should_continue(state: State):

    print("\n--- ROUTER ---")

    last_message = state["messages"][-1]

    search_count = sum(
        1
        for message in state["messages"]
        if hasattr(message, "tool_calls") and message.tool_calls
    )

    print("Messages in state:", len(state["messages"]))
    print("Last message type:", type(last_message).__name__)
    print("Tool calls:", last_message.tool_calls)
    print("Search count:", search_count)

    if last_message.tool_calls and search_count < 2:
        return "tools"

    if last_message.tool_calls and search_count >= 2:
        return "final"

    return "end"


async def create_researcher():

    # Get tools from MCP server
    tools = await client.get_tools()

    print("\n=== MCP TOOLS LOADED ===")

    for tool in tools:
        print(tool.name)

    # Give MCP tools to the LLM
    llm_with_tools = llm.bind_tools(tools)

    # Final LLM has NO tools
    final_llm = llm

    async def call_llm(state: State):

        print("\n--- LLM NODE ---")

        response = await llm_with_tools.ainvoke(
            state["messages"]
        )

        if response.tool_calls:
            return {
                "messages": [response]
            }

        return {
            "messages": [response],
            "research": response.content
        }

    async def final_answer(state: State):

        print("\n--- FINAL RESEARCH NODE ---")

        # Get the original research request
        original_request = next(
            message.content
            for message in state["messages"]
            if isinstance(message, HumanMessage)
        )

        # Collect results returned by MCP tools
        combined_research = "\n\n".join(
            str(item)
            for message in state["messages"]
            if message.type == "tool"
            for item in message.content
        )

        final_prompt = f"""
You are a research analyst.

The web searches have already been completed.

Original research request:
{original_request}

Research collected from the web:
{combined_research}

Based on the research above, provide a clear, accurate, and useful
answer to the original research request.

Do NOT use any tools.
Do NOT search again.

Synthesize the findings into a coherent research answer.
"""

        response = await final_llm.ainvoke(
            [
                HumanMessage(content=final_prompt)
            ]
        )

        return {
            "messages": [response],
            "research": response.content
        }

    # Create LangGraph
    graph = StateGraph(State)

    graph.add_node("llm", call_llm)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node("final", final_answer)

    graph.set_entry_point("llm")

    graph.add_conditional_edges(
        "llm",
        should_continue,
        {
            "tools": "tools",
            "final": "final",
            "end": "__end__"
        }
    )

    graph.add_edge("tools", "llm")
    graph.add_edge("final", "__end__")

    return graph.compile()


async def run_researcher(
    query: str,
    memory_text: str = ""
):

    prompt = f"""
You are a research agent.

Previous useful research memory:
{memory_text}

Current research request:
{query}

Use the previous memory if it is relevant.
Do not blindly trust it.
Search the web for current information.
"""

    researcher = await create_researcher()

    result = await researcher.ainvoke(
        {
            "messages": [
                HumanMessage(content=prompt)
            ],
            "research": "",
            "search_count": 0
        }
    )

    return result["research"]


async def main():

    research = await run_researcher(
        "Research the latest developments in AI agents and compare at least 3 major developments."
    )

    print("\n=== RESEARCH ===")
    print(research)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())