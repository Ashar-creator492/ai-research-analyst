from typing import TypedDict

import sqlite3

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from src.agents.researcher import run_researcher
from src.agents.analyst import run_analyst
from src.agents.writer import run_writer

from dataclasses import dataclass
from langgraph.store.sqlite import SqliteStore
from langgraph.runtime import Runtime
import uuid

from src.memory import extract_memory, get_relevant_memories


class State(TypedDict):
    topic: str
    research: str
    analysis: str
    final_answer: str



@dataclass
class UserContext:
    user_id: str


async def researcher_node(
    state: State,
    runtime: Runtime[UserContext]
):
    user_id = runtime.context.user_id

    namespace = (
        "user_memories",
        user_id
    )

    memories = runtime.store.search(namespace)

    relevant_memories = get_relevant_memories(
        state["topic"],
        memories
    )

    memory_text = "\n".join(
        memory.value["memory"]
        for memory in relevant_memories
    )

    print("\n=== RELEVANT MEMORIES ===")

    for memory in relevant_memories:
        print(memory.value["memory"][:300])

    research = await run_researcher(
    state["topic"],
    memory_text
)

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


def memory_node(
    state: State,
    runtime: Runtime[UserContext]
):
    memory = extract_memory(
        state["topic"],
        state["final_answer"]
    )

    if memory != "NONE":
        user_id = runtime.context.user_id

        namespace = (
            "user_memories",
            user_id
        )

        runtime.store.put(
            namespace,
            str(uuid.uuid4()),
            {
                "memory": memory
            }
        )

    return {}



graph = StateGraph(
    State,
    context_schema=UserContext
)

graph.add_node("researcher", researcher_node)
graph.add_node("analyst", analyst_node)
graph.add_node("writer", writer_node)
graph.add_node("memory", memory_node)

graph.add_edge(START, "researcher")
graph.add_edge("researcher", "analyst")
graph.add_edge("analyst", "writer")
graph.add_edge("writer", "memory")
graph.add_edge("memory", END)





memory_conn = sqlite3.connect(
    "long_term_memory.db",
    check_same_thread=False,
    isolation_level=None
)

long_term_store = SqliteStore(memory_conn)





def check_state(state: State):
    print("\n--- STATE ---")
    print("Topic:", state["topic"])
    print("Research:", state["research"])
    print("Analysis:", state["analysis"])
    print("Final Answer:", state["final_answer"])

async def run_pipeline(topic: str, thread_id: str, user_id: str):

    async with AsyncSqliteSaver.from_conn_string(
        "checkpoints.db"
    ) as checkpointer:

        app = graph.compile(
            checkpointer=checkpointer,
            store=long_term_store
        )

        result = await app.ainvoke(
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
            },
            context=UserContext(
                user_id=user_id
            )
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

def inspect_long_term_memory(user_id: str):
    namespace = (
        "user_memories",
        user_id
    )

    memories = long_term_store.search(namespace)

    print("\n=== LONG-TERM MEMORIES ===")

    for memory in memories:
        print(memory.value)


# if __name__ == "__main__":
#     thread_id = "test-thread"

#     topic_1 = "Research the latest developments in AI agents."

#     print("\n========== RUN 1 ==========")

#     run_pipeline(
#     topic_1,
#     thread_id,
#     "ashar"
#     )

#     topic_2 = "Research the latest developments in MCP."

#     print("\n========== RUN 2 ==========")

#     run_pipeline(
#     topic_2,
#     thread_id,
#     "ashar"
#     )

#     inspect_thread(thread_id)

#     inspect_history(thread_id)
#     inspect_long_term_memory("ashar")

if __name__ == "__main__":
    import asyncio

    result = asyncio.run(
        run_pipeline(
            "Research the latest developments in AI agents.",
            "test-thread",
            "ashar"
        )
    )

    print("\n=== FINAL ANSWER ===")
    print(result)