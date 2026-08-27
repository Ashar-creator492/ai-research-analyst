from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from src.agents.researcher import run_researcher
from src.agents.analyst import run_analyst
from src.agents.writer import run_writer


class State(TypedDict):
    topic: str
    research: str
    analysis: str
    final_answer: str


def researcher_node(state: State):
    research = run_researcher(state["topic"])

    return {
        "research": research
    }


def analyst_node(state: State):
    analysis = run_analyst(state["research"])

    return {
        "analysis": analysis
    }

def writer_node(state: State):
    final_answer = run_writer(
        state["research"],
        state["analysis"]
    )

    return {
        "final_answer": final_answer
    }


graph = StateGraph(State)

graph.add_node("researcher", researcher_node)
graph.add_node("analyst", analyst_node)
graph.add_node("writer", writer_node)

graph.add_edge(START, "researcher")
graph.add_edge("researcher", "analyst")
graph.add_edge("analyst", "writer")
graph.add_edge("writer", END)


app = graph.compile()

def check_state(state: State):
    print("\n--- STATE ---")
    print("Topic:", state["topic"])
    print("Research:", state["research"])
    print("Analysis:", state["analysis"])
    print("Final Answer:", state["final_answer"])

def run_pipeline(topic: str):
    result = app.invoke({
        "topic": topic,
        "research": "",
        "analysis": "",
        "final_answer": ""
    })

    return result["final_answer"]


if __name__ == "__main__":
    topic = "Research the latest developments in AI agents and compare at least 3 major developments."

    final_answer = run_pipeline(topic)

    print("\n=== FINAL ANSWER ===")
    print(final_answer)