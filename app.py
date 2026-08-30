
import uuid
import streamlit as st

from src.agents.orchestrator import run_pipeline


st.set_page_config(
    page_title="AI Research Analyst",
    page_icon="🔎",
    layout="wide"
)


if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


st.title("🔎 AI Research Analyst")
st.write("Enter a user ID and research topic to run the AI research pipeline.")


user_id = st.text_input(
    "User ID",
    placeholder="e.g. ashar"
)

topic = st.text_input(
    "Research Topic",
    placeholder="e.g. Latest developments in AI agents"
)


if st.button("Run Research", type="primary"):

    if not user_id.strip():
        st.warning("Please enter a user ID.")

    elif not topic.strip():
        st.warning("Please enter a research topic.")

    else:
        with st.spinner("Researching, analyzing, and writing..."):

            try:
                final_answer = run_pipeline(
                    topic,
                    st.session_state.thread_id,
                    user_id
                )

                st.subheader("Final Answer")
                st.markdown(final_answer)

            except Exception as e:
                st.error(f"Something went wrong: {e}")

