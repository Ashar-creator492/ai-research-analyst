import uuid
import streamlit as st

from src.agents.orchestrator import run_pipeline



if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

st.set_page_config(
    page_title="AI Research Analyst",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 AI Research Analyst")
st.write("Enter a topic and let the AI research, analyze, and write the final answer.")

topic = st.text_input(
    "Research Topic",
    placeholder="e.g. Latest developments in AI agents"
)

if st.button("Run Research", type="primary"):
    if not topic.strip():
        st.warning("Please enter a research topic.")
    else:
        with st.spinner("Researching, analyzing, and writing..."):
            try:
                final_answer = run_pipeline(
                topic,
                st.session_state.thread_id
            )

                st.subheader("Final Answer")
                st.markdown(final_answer)

            except Exception as e:
                st.error(f"Something went wrong: {e}")

