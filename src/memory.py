from langchain_groq import ChatGroq


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


def extract_memory(topic: str, final_answer: str):
    prompt = f"""
You are a long-term memory extractor.

Look at the research topic and final answer below.

Decide whether there is any useful information that should be
remembered for this user in future research sessions.

Topic:
{topic}

Final Answer:
{final_answer}

Rules:
- Only save information that could be useful in future sessions.
- Do not save temporary details.
- Do not save the entire answer.
- If there is nothing useful, return exactly: NONE
- Otherwise, return a short memory.
"""

    response = llm.invoke(prompt)

    return response.content


def get_relevant_memories(topic: str, memories):

    if not memories:
        return []

    memory_text = "\n\n".join(
        f"MEMORY {i+1}:\n{memory.value['memory']}"
        for i, memory in enumerate(memories)
    )

    prompt = f"""
You are a memory retrieval system.

Current topic:
{topic}

Stored memories:
{memory_text}

Select only the memories that are relevant to the current topic.

Return the numbers of the relevant memories only.
For example:
1, 3

If none are relevant, return:
NONE
"""

    response = llm.invoke(prompt)

    result = response.content.strip()

    if result == "NONE":
        return []

    selected = []

    for number in result.split(","):
        number = number.strip()

        if number.isdigit():
            index = int(number) - 1

            if 0 <= index < len(memories):
                selected.append(memories[index])

    return selected