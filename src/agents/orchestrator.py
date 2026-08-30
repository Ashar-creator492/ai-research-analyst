from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

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


checkpointer = InMemorySaver()

app = graph.compile(
    checkpointer=checkpointer
)

def check_state(state: State):
    print("\n--- STATE ---")
    print("Topic:", state["topic"])
    print("Research:", state["research"])
    print("Analysis:", state["analysis"])
    print("Final Answer:", state["final_answer"])

def run_pipeline(topic: str, thread_id: str):
    result = app.invoke(
        {
            "topic": topic,
            "research": "",
            "analysis": "",
            "final_answer": ""
        },
        {
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return result["final_answer"]


def inspect_thread(thread_id: str):
    state = app.get_state(
        {
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    print("\n=== SAVED STATE ===")
    print("Topic:", state.values["topic"])
    print("Research:", state.values["research"][:300])
    print("Analysis:", state.values["analysis"][:300])
    print("Final Answer:", state.values["final_answer"][:300])


def inspect_history(thread_id: str):
    history = list(
        app.get_state_history(
            {
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )
    )

    print("\n=== CHECKPOINT HISTORY ===")

    for i, snapshot in enumerate(history, start=1):
        print(f"\nCheckpoint {i}")
        print("Topic:", snapshot.values.get("topic"))
        print("Research:", snapshot.values.get("research", "")[:100])
        print("Analysis:", snapshot.values.get("analysis", "")[:100])
        print("Final Answer:", snapshot.values.get("final_answer", "")[:100])


if __name__ == "__main__":
    thread_id = "test-thread"

    topic_1 = "Research the latest developments in AI agents."

    print("\n========== RUN 1 ==========")

    run_pipeline(
        topic_1,
        thread_id
    )

    topic_2 = "Research the latest developments in MCP."

    print("\n========== RUN 2 ==========")

    run_pipeline(
        topic_2,
        thread_id
    )

    inspect_thread(thread_id)

    inspect_history(thread_id)