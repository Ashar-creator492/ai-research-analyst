import uuid
import html
from datetime import datetime

import streamlit as st

import asyncio

from src.agents.orchestrator import run_pipeline


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Research Analyst",
    page_icon="◆",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "result" not in st.session_state:
    st.session_state.result = None
if "result_topic" not in st.session_state:
    st.session_state.result_topic = None
if "result_user" not in st.session_state:
    st.session_state.result_user = None
if "result_time" not in st.session_state:
    st.session_state.result_time = None


# ---------------------------------------------------------------------------
# Style
#
# Light, glassy theme: near-white base with a few soft blurred colour
# shapes fixed behind the content, and frosted (backdrop-blur) panels
# with black/near-black text on top.
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --bg: #F6F5F1;
        --panel: rgba(255, 255, 255, 0.55);
        --panel-strong: rgba(255, 255, 255, 0.72);
        --input-bg: rgba(255, 255, 255, 0.65);
        --border: rgba(17, 15, 12, 0.10);
        --border-soft: rgba(17, 15, 12, 0.07);
        --text: #14120F;
        --text-dim: #55504A;
        --text-faint: #8B8579;
        --accent: #B3392C;
        --accent-soft: rgba(179, 57, 44, 0.10);
        --accent-line: rgba(179, 57, 44, 0.35);
        --shadow: 0 8px 30px rgba(20, 18, 15, 0.07);
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }
    #MainMenu, footer, [data-testid="stToolbar"] {
        visibility: hidden;
    }

    .block-container {
        max-width: 760px;
        padding-top: 2.5rem;
        padding-bottom: 5rem;
    }

    * {
        font-family: 'Inter', sans-serif;
    }

    /* ---------------- Ambient background ---------------- */

    .ambient {
        position: fixed;
        inset: 0;
        overflow: hidden;
        z-index: -1;
        pointer-events: none;
    }
    .ambient .blob {
        position: absolute;
        border-radius: 50%;
        filter: blur(120px);
        opacity: 0.55;
    }
    .ambient .blob-1 {
        width: 480px; height: 480px;
        top: -140px; left: -100px;
        background: #F4CBB8;
    }
    .ambient .blob-2 {
        width: 440px; height: 440px;
        bottom: -160px; right: -80px;
        background: #CDE1D2;
    }
    .ambient .blob-3 {
        width: 380px; height: 380px;
        top: 32%; left: 58%;
        background: #F1E3BC;
        opacity: 0.4;
    }

    /* ---------------- Top bar ---------------- */

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        border-bottom: 1px solid var(--border-soft);
        padding-bottom: 14px;
        margin-bottom: 56px;
    }
    .topbar-mark {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--text-dim);
    }
    .topbar-mark span {
        color: var(--accent);
    }
    .topbar-session {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: var(--text-faint);
    }

    /* ---------------- Hero ---------------- */

    .kicker {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 18px;
    }
    .hero-title {
        font-family: 'Newsreader', serif;
        font-weight: 500;
        font-size: 44px;
        line-height: 1.18;
        color: var(--text);
        margin: 0 0 22px 0;
    }
    .hero-sub {
        font-size: 16px;
        line-height: 1.65;
        color: var(--text-dim);
        max-width: 480px;
        margin-bottom: 44px;
    }

    /* ---------------- Glass panel base ---------------- */

    .st-key-command_panel,
    .st-key-brief_container {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 18px;
        box-shadow: var(--shadow), inset 0 1px 0 rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(22px) saturate(160%);
        -webkit-backdrop-filter: blur(22px) saturate(160%);
    }

    /* ---------------- Command panel ---------------- */

    .st-key-command_panel {
        padding: 34px 34px 26px 34px;
        margin-bottom: 10px;
    }

    .field-label {
        font-size: 13px;
        font-weight: 500;
        color: var(--text-dim);
        margin-bottom: 6px;
    }
    .field-label.query {
        margin-top: 22px;
    }

    .st-key-command_panel [data-testid="stTextInput"] input,
    .st-key-command_panel [data-testid="stTextArea"] textarea {
        background: var(--input-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        color: var(--text);
        font-family: 'Inter', sans-serif;
        font-size: 15px;
        padding: 11px 13px;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    .st-key-command_panel [data-testid="stTextArea"] textarea {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 14.5px;
        line-height: 1.55;
        min-height: 96px;
    }
    .st-key-command_panel [data-testid="stTextInput"] input:focus,
    .st-key-command_panel [data-testid="stTextArea"] textarea:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 1px var(--accent-line);
    }
    .st-key-command_panel [data-testid="stTextInput"] input::placeholder,
    .st-key-command_panel [data-testid="stTextArea"] textarea::placeholder {
        color: var(--text-faint);
    }

    .st-key-command_panel [data-testid="stWidgetLabel"] {
        display: none;
    }

    .stButton > button,
    .stButton > button[kind="primary"] {
        background: var(--accent);
        color: #FBF3EC;
        border: none;
        border-radius: 10px;
        font-size: 14.5px;
        font-weight: 600;
        padding: 10px 24px;
        margin-top: 22px;
        box-shadow: 0 4px 14px rgba(179, 57, 44, 0.25);
        transition: filter 0.15s ease;
    }
    .stButton > button:hover {
        filter: brightness(1.08);
    }
    .stButton > button:focus:not(:active) {
        border: none;
        box-shadow: 0 0 0 2px var(--accent-line);
    }

    [data-testid="stAlert"] {
        background: var(--panel-strong);
        border: 1px solid var(--border);
        border-radius: 10px;
        color: var(--text-dim);
        font-size: 14px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }

    /* ---------------- Pipeline stepper ---------------- */

    .pipeline {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 22px 2px 30px 2px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12.5px;
        letter-spacing: 0.4px;
        color: var(--text-faint);
    }
    .pipeline .stage {
        display: flex;
        align-items: center;
        gap: 7px;
    }
    .pipeline .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--text-faint);
    }
    .pipeline .rule {
        flex: 0 0 26px;
        height: 1px;
        background: var(--border);
    }
    .pipeline.running .dot {
        background: var(--accent);
        animation: pulse 1.6s ease-in-out infinite;
    }
    .pipeline.running .stage:nth-child(1) .dot { animation-delay: 0s; }
    .pipeline.running .stage:nth-child(3) .dot { animation-delay: 0.35s; }
    .pipeline.running .stage:nth-child(5) .dot { animation-delay: 0.7s; }
    .pipeline.running .stage {
        color: var(--text-dim);
    }
    .pipeline.done .dot {
        background: var(--accent);
    }
    .pipeline.done .stage {
        color: var(--text-dim);
    }
    @keyframes pulse {
        0%, 100% { opacity: 0.35; }
        50% { opacity: 1; }
    }

    [data-testid="stSpinner"] {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        color: var(--text-faint);
    }

    /* ---------------- Research brief ---------------- */

    .st-key-brief_container {
        padding: 38px 40px 44px 40px;
        margin-top: 34px;
    }
    .brief-kicker {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11.5px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 14px;
    }
    .brief-title {
        font-family: 'Newsreader', serif;
        font-weight: 500;
        font-size: 28px;
        line-height: 1.3;
        color: var(--text);
        margin-bottom: 22px;
    }
    .brief-meta {
        display: flex;
        gap: 40px;
        padding-bottom: 22px;
        margin-bottom: 26px;
        border-bottom: 1px solid var(--border-soft);
    }
    .brief-meta-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .brief-meta-label {
        font-size: 11.5px;
        color: var(--text-faint);
    }
    .brief-meta-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12.5px;
        color: var(--text-dim);
    }

    .st-key-brief_container [data-testid="stMarkdownContainer"] {
        font-size: 15.5px;
        line-height: 1.75;
        color: var(--text);
    }
    .st-key-brief_container [data-testid="stMarkdownContainer"] h1,
    .st-key-brief_container [data-testid="stMarkdownContainer"] h2,
    .st-key-brief_container [data-testid="stMarkdownContainer"] h3 {
        font-family: 'Newsreader', serif;
        font-weight: 500;
        color: var(--text);
        margin-top: 30px;
        margin-bottom: 12px;
    }
    .st-key-brief_container [data-testid="stMarkdownContainer"] h2 {
        font-size: 20px;
    }
    .st-key-brief_container [data-testid="stMarkdownContainer"] h3 {
        font-size: 17px;
    }
    .st-key-brief_container [data-testid="stMarkdownContainer"] p {
        margin-bottom: 14px;
    }
    .st-key-brief_container [data-testid="stMarkdownContainer"] ul,
    .st-key-brief_container [data-testid="stMarkdownContainer"] ol {
        margin-bottom: 14px;
        padding-left: 22px;
    }
    .st-key-brief_container [data-testid="stMarkdownContainer"] li {
        margin-bottom: 6px;
    }
    .st-key-brief_container [data-testid="stMarkdownContainer"] code {
        background: rgba(17, 15, 12, 0.05);
        border: 1px solid var(--border-soft);
        border-radius: 4px;
        padding: 1px 5px;
        font-size: 13.5px;
        color: var(--text-dim);
    }
    .st-key-brief_container [data-testid="stMarkdownContainer"] a {
        color: var(--accent);
    }
    .st-key-brief_container [data-testid="stMarkdownContainer"] hr {
        border-color: var(--border-soft);
        margin: 26px 0;
    }
    .st-key-brief_container [data-testid="stMarkdownContainer"] blockquote {
        border-left: 2px solid var(--accent-line);
        padding-left: 16px;
        color: var(--text-dim);
        margin: 16px 0;
    }

    /* ---------------- Sidebar ---------------- */

    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.45);
        border-right: 1px solid var(--border-soft);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }
    .sidebar-kicker {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--text-faint);
        margin-bottom: 16px;
    }
    .sidebar-row {
        margin-bottom: 16px;
    }
    .sidebar-label {
        font-size: 12px;
        color: var(--text-faint);
        margin-bottom: 3px;
    }
    .sidebar-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12.5px;
        color: var(--text-dim);
        word-break: break-all;
    }
    </style>

    <div class="ambient">
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="blob blob-3"></div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Sidebar — session info
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="sidebar-kicker">Session</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="sidebar-row">
            <div class="sidebar-label">Thread</div>
            <div class="sidebar-value">{html.escape(st.session_state.thread_id[:8])}</div>
        </div>
        <div class="sidebar-row">
            <div class="sidebar-label">Status</div>
            <div class="sidebar-value">{"Brief on file" if st.session_state.result else "Idle"}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Top bar
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="topbar">
        <div class="topbar-mark">Research <span>Analyst</span></div>
        <div class="topbar-session">Thread {html.escape(st.session_state.thread_id[:8])}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="kicker">Research workspace</div>
    <div class="hero-title">Find the signal.<br>Skip the noise.</div>
    <div class="hero-sub">
        Give it a topic. It researches the web, weighs what it finds,
        and returns a concise, sourced brief you can actually act on.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Command panel
# ---------------------------------------------------------------------------

with st.container(key="command_panel"):
    st.markdown('<div class="field-label">Analyst</div>', unsafe_allow_html=True)
    user_id = st.text_input(
        "Analyst",
        placeholder="Your user ID",
        label_visibility="collapsed",
    )

    st.markdown('<div class="field-label query">Research query</div>', unsafe_allow_html=True)
    topic = st.text_area(
        "Research query",
        placeholder="e.g. Latest developments in AI agents",
        label_visibility="collapsed",
        height=110,
    )

    run_clicked = st.button("Run research", type="primary")


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

def render_pipeline_status(mode: str) -> str:
    """mode: 'running' or 'done' — purely visual, not tied to real progress."""
    stages = ["Researching", "Analyzing", "Writing"]
    parts = []
    for i, stage in enumerate(stages):
        parts.append(f'<div class="stage"><div class="dot"></div>{stage}</div>')
        if i < len(stages) - 1:
            parts.append('<div class="rule"></div>')
    return f'<div class="pipeline {mode}">{"".join(parts)}</div>'


if run_clicked:
    if not user_id.strip():
        st.warning("Enter an analyst ID to continue.")
    elif not topic.strip():
        st.warning("Enter a research query to continue.")
    else:
        stage_placeholder = st.empty()
        stage_placeholder.markdown(render_pipeline_status("running"), unsafe_allow_html=True)

        try:
            with st.spinner("Running the research pipeline"):
                final_answer = asyncio.run(
                    run_pipeline(
                        topic,
                        st.session_state.thread_id,
                        user_id
                    )
)

            stage_placeholder.markdown(render_pipeline_status("done"), unsafe_allow_html=True)

            st.session_state.result = final_answer
            st.session_state.result_topic = topic
            st.session_state.result_user = user_id
            st.session_state.result_time = datetime.now()

        except Exception as e:
            stage_placeholder.empty()
            st.error(f"The pipeline ran into a problem: {e}")


# ---------------------------------------------------------------------------
# Research brief
# ---------------------------------------------------------------------------

if st.session_state.result:
    with st.container(key="brief_container"):
        filed_at = st.session_state.result_time.strftime("%d %b %Y, %H:%M") \
            if st.session_state.result_time else ""

        st.markdown(
            f"""
            <div class="brief-kicker">Research brief</div>
            <div class="brief-title">{html.escape(st.session_state.result_topic)}</div>
            <div class="brief-meta">
                <div class="brief-meta-item">
                    <div class="brief-meta-label">Analyst</div>
                    <div class="brief-meta-value">{html.escape(st.session_state.result_user)}</div>
                </div>
                <div class="brief-meta-item">
                    <div class="brief-meta-label">Filed</div>
                    <div class="brief-meta-value">{html.escape(filed_at)}</div>
                </div>
                <div class="brief-meta-item">
                    <div class="brief-meta-label">Reference</div>
                    <div class="brief-meta-value">{html.escape(st.session_state.thread_id[:8])}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(st.session_state.result)
