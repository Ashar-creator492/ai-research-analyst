from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]
    research: str


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

def call_llm(state: State):
    research = state["research"]

    response = llm.invoke([
        HumanMessage(
            content=f"""
            Here are the research findings collected by the Researcher:

            {research}

            Analyze these findings and explain which development
            is likely to have the biggest impact.
            """
        )
    ])

    return {
        "messages": [response]
    }


graph = StateGraph(State)


graph.add_node("analyst", call_llm)

graph.set_entry_point("analyst")

graph.set_finish_point("analyst")

app = graph.compile()





def run_analyst(research: str):
    result = app.invoke({
        "messages": [],
        "research": research
    })

    return result["messages"][-1].content

if __name__ == "__main__":
    research_findings = """
    1. AI agents are increasingly being used for autonomous software testing.
    2. MCP is becoming an important standard for connecting agents to tools.
    3. Companies are developing agents for drug discovery.
    """

    analysis = run_analyst(research_findings)

    print("\n=== ANALYSIS ===")
    print(analysis)

    