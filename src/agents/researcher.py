from langchain_groq import ChatGroq
from typing import TypedDict
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from dotenv import load_dotenv
from pathlib import Path
from tavily import TavilyClient
import os



env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)



class State(TypedDict):
    messages: Annotated[list, add_messages]
    research: str


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# response = llm.invoke("What is an AI agent?")

# print(response.content)

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# results = tavily.search(
#     query="latest developments in AI agents",
#     max_results=3
# )

# for result in results["results"]:
#     print("\nTITLE:", result["title"])
#     print("URL:", result["url"])
#     print("CONTENT:", result["content"][:500])


@tool
def search_web(query):
    """Search the web for current information."""
    results = tavily.search(
        query=query,
        max_results=3
    )

    return results["results"]





tools = [search_web]
llm_with_tools = llm.bind_tools(tools)


def call_llm(state: State):
    print("\n--- LLM NODE ---")

    response = llm_with_tools.invoke(state["messages"])

    if response.tool_calls:
        return {
            "messages": [response]
        }

    return {
        "messages": [response],
        "research": response.content
    }


def should_continue(state: State):
    print("\n--- ROUTER ---")
    print("Messages in state:", len(state["messages"]))

    last_message = state["messages"][-1]

    print("Last message type:", type(last_message).__name__)
    print("Tool calls:", last_message.tool_calls)

    if last_message.tool_calls:
        return "tools"

    return "end"



graph = StateGraph(State)

graph.add_node("llm", call_llm) 
graph.add_node("tools", ToolNode(tools))


graph.set_entry_point("llm")

graph.add_conditional_edges(
    "llm",
    should_continue,
    {
        "tools": "tools",
        "end": "__end__"
    }
)

graph.add_edge("tools", "llm")

app = graph.compile()


def run_researcher(query: str):
    result = app.invoke({
        "messages": [
            HumanMessage(content=query)
        ]
    })

    return result["research"]

if __name__ == "__main__":
    research = run_researcher(
        "Research the latest developments in AI agents and compare at least 3 major developments."
    )

    print("\n=== RESEARCH ===")
    print(research)
