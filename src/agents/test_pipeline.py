from src.agents.researcher import run_researcher
from src.agents.analyst import run_analyst
from src.agents.writer import run_writer

# Runs the complete research -> analysis -> writing pipeline
def run_pipeline(query):
    research = run_researcher(query)

    analysis = run_analyst(research)

    final_answer = run_writer(research, analysis)

    return final_answer


if __name__ == "__main__":
    query = "Research the latest developments in AI agents and compare at least 3 major developments."

    final_answer = run_pipeline(query)

    print("\n=== FINAL ANSWER ===")
    print(final_answer)