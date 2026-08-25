from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    research: str
    analysis: str


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

def call_llm(state: State):

    research = state["research"]
    analysis = state["analysis"]

    response = llm.invoke([
        HumanMessage(
            content=f"""
            Here is the research:

            {research}

            Here is the analysis:

            {analysis}

            Write a clear, concise final answer for the user.
            """
        )
    ])

    return {
        "messages": [response]
    }


graph = StateGraph(State)

graph.add_node("writer", call_llm)

graph.set_entry_point("writer")

graph.set_finish_point("writer")

app = graph.compile()

def run_writer(research: str, analysis: str):

    result = app.invoke({
        "messages": [],
        "research": research,
        "analysis": analysis
    })

    return result["messages"][-1].content

if __name__ == "__main__":

    research = """
    AI agents are increasingly being used for autonomous software testing.
    MCP is becoming an important standard for connecting agents to tools.
    Companies are developing agents for drug discovery.
    """

    analysis = """
    AI agents for drug discovery may have the greatest long-term impact
    because of their potential effect on healthcare and medicine.
    """

    final_answer = run_writer(research, analysis)

    print("\n=== FINAL ANSWER ===")
    print(final_answer)