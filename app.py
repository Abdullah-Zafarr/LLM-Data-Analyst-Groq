"""
app.py — Streamlit frontend for the Natural Language Data Analyst.

Design: Dark Mode OLED · Fira Code / Fira Sans · Blue #1E40AF + Amber #F59E0B
"""

import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv

load_dotenv()

from agent import run_agent
from tools import set_dataset

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="DataMind AI — Natural Language Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# SVG icons (Lucide — no emojis as UI icons)
# ---------------------------------------------------------------------------
ICONS = {
    "upload":   '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
    "database": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    "search":   '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    "chart":    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "calc":     '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="20" x="4" y="2" rx="2"/><line x1="8" x2="16" y1="6" y2="6"/><line x1="16" x2="16" y1="14" y2="18"/><path d="M16 10h.01"/><path d="M12 10h.01"/><path d="M8 10h.01"/><path d="M12 14h.01"/><path d="M8 14h.01"/><path d="M12 18h.01"/><path d="M8 18h.01"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    "bolt":     '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "message":  '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "check":    '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "folder":   '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
    "sparkles": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>',
}

# ---------------------------------------------------------------------------
# CSS — OLED Dark Design System
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-deep: #050910; --bg-primary: #070B14; --bg-secondary: #0C1220;
        --bg-card: #0F1629; --bg-card-hover: #141D35;
        --border: rgba(30,64,175,0.20); --border-hover: rgba(59,130,246,0.35);
        --primary: #1E40AF; --secondary: #3B82F6; --accent: #60A5FA;
        --cta: #F59E0B; --success: #10B981; --error: #EF4444;
        --text: #E2E8F0; --text-muted: #94A3B8; --text-dim: #64748B;
        --glow-blue: 0 0 20px rgba(59,130,246,0.15);
    }

    .stApp {
        background: var(--bg-deep) !important;
        font-family: 'Fira Sans', system-ui, sans-serif !important;
        color: var(--text) !important;
    }
    .main .block-container { padding-top: 1.5rem !important; max-width: 1100px; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--bg-primary) !important;
        border-right: 1px solid var(--border) !important;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Fira Sans', sans-serif !important;
        color: var(--text) !important;
    }

    /* Header */
    .dm-header { text-align: center; padding: 1.5rem 0 0.75rem; margin-bottom: 1.5rem; }
    .dm-title {
        font-family: 'Fira Code', monospace; font-size: 2.4rem; font-weight: 700;
        color: #fff; text-shadow: 0 0 40px rgba(59,130,246,0.3); letter-spacing: -1px; margin-bottom: 0.4rem;
    }
    .dm-title-accent { color: var(--cta); }
    .dm-subtitle { font-family: 'Fira Sans', sans-serif; font-size: 0.9rem; color: var(--text-muted); letter-spacing: 0.5px; }
    .dm-subtitle code {
        font-family: 'Fira Code', monospace; font-size: 0.8rem; color: var(--accent);
        background: rgba(59,130,246,0.1); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(59,130,246,0.2);
    }

    /* Feature Cards */
    .dm-features { display: grid; grid-template-columns: repeat(4,1fr); gap: 0.75rem; margin-bottom: 2rem; }
    .dm-feature-card {
        background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
        padding: 1.25rem 1rem; text-align: center; transition: all 200ms ease;
    }
    .dm-feature-card:hover {
        border-color: var(--border-hover); background: var(--bg-card-hover);
        box-shadow: var(--glow-blue); transform: translateY(-2px);
    }
    .dm-feature-icon {
        display: inline-flex; align-items: center; justify-content: center;
        width: 40px; height: 40px; border-radius: 10px; margin-bottom: 0.6rem;
    }
    .dm-feature-icon.blue  { background: rgba(59,130,246,0.12); color: var(--secondary); }
    .dm-feature-icon.amber { background: rgba(245,158,11,0.12); color: var(--cta); }
    .dm-feature-icon.green { background: rgba(16,185,129,0.12); color: var(--success); }
    .dm-feature-icon.cyan  { background: rgba(96,165,250,0.12); color: var(--accent); }
    .dm-feature-title { font-family: 'Fira Code', monospace; font-size: 0.85rem; font-weight: 600; color: var(--text); margin-bottom: 0.2rem; }
    .dm-feature-desc { font-size: 0.78rem; color: var(--text-dim); line-height: 1.4; }

    /* Chat Messages */
    .dm-user-msg {
        background: linear-gradient(135deg, var(--primary), #2563EB); color: #fff;
        padding: 0.9rem 1.15rem; border-radius: 16px 16px 4px 16px;
        margin: 0.6rem 0; max-width: 80%; margin-left: auto;
        font-size: 0.92rem; line-height: 1.55; box-shadow: 0 4px 20px rgba(30,64,175,0.35);
    }
    .dm-assistant-msg {
        background: var(--bg-card); color: var(--text);
        padding: 1.1rem 1.3rem; border-radius: 16px 16px 16px 4px;
        margin: 0.6rem 0; border: 1px solid var(--border);
        font-size: 0.92rem; line-height: 1.65; white-space: pre-wrap;
    }
    .dm-assistant-msg code {
        font-family: 'Fira Code', monospace; font-size: 0.82rem;
        background: rgba(59,130,246,0.08); padding: 1px 6px; border-radius: 4px; color: var(--accent);
    }
    .dm-error-msg { border-color: rgba(239,68,68,0.3) !important; }

    /* Tool Badge */
    .dm-tool-badge {
        display: inline-flex; align-items: center; gap: 5px;
        background: rgba(16,185,129,0.10); border: 1px solid rgba(16,185,129,0.25); color: var(--success);
        padding: 3px 10px; border-radius: 6px;
        font-family: 'Fira Code', monospace; font-size: 0.72rem; font-weight: 500; margin: 2px 4px 2px 0;
    }

    /* Status Badges */
    .dm-status-loaded {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(16,185,129,0.10); color: var(--success);
        padding: 5px 12px; border-radius: 6px;
        font-family: 'Fira Code', monospace; font-size: 0.78rem; font-weight: 500;
        border: 1px solid rgba(16,185,129,0.25);
    }
    .dm-status-empty {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(100,116,139,0.10); color: var(--text-dim);
        padding: 5px 12px; border-radius: 6px;
        font-family: 'Fira Code', monospace; font-size: 0.78rem; font-weight: 500;
        border: 1px solid rgba(100,116,139,0.15);
    }

    /* Sample Query Pills */
    .dm-query-pill {
        display: flex; align-items: center; gap: 8px; width: 100%;
        padding: 0.5rem 0.75rem; background: rgba(30,64,175,0.06);
        border: 1px solid rgba(30,64,175,0.15); border-radius: 8px;
        color: var(--text-muted); font-size: 0.8rem; margin-bottom: 0.35rem; transition: all 200ms ease;
    }
    .dm-query-pill:hover { background: rgba(59,130,246,0.10); border-color: var(--secondary); color: var(--text); }

    /* Misc */
    .dm-divider { border: none; border-top: 1px solid var(--border); margin: 1rem 0; }
    .dm-section-label {
        font-family: 'Fira Code', monospace; font-size: 0.7rem; font-weight: 600;
        color: var(--text-dim); letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 0.6rem;
    }
    .stDataFrame { border: 1px solid var(--border) !important; border-radius: 8px !important; overflow: hidden; }
    .stChatInput > div {
        background: var(--bg-secondary) !important; border-color: var(--border) !important;
        border-radius: 12px !important; font-family: 'Fira Sans', sans-serif !important;
    }
    .stMarkdown, .stMarkdown p, .stText { color: var(--text) !important; }
    .streamlit-expanderHeader {
        background: var(--bg-card) !important; border: 1px solid var(--border) !important;
        border-radius: 8px !important; color: var(--text) !important;
        font-family: 'Fira Code', monospace !important; font-size: 0.82rem !important;
    }
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: var(--bg-deep) !important;
        border-bottom: 1px solid var(--border) !important;
    }
    .stDeployButton { display: none !important; }

    @media (prefers-reduced-motion: reduce) {
        .dm-feature-card, .dm-query-pill { transition: none !important; }
        .dm-feature-card:hover { transform: none !important; }
    }
    @media (max-width: 768px) {
        .dm-features { grid-template-columns: repeat(2,1fr); }
        .dm-title { font-size: 1.8rem; }
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
for key, default in {
    "messages": [],
    "agent_messages": None,
    "dataset_loaded": False,
    "dataset_path": None,
    "dataset_name": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------------------------
# Helpers — render assistant artifacts once (not duplicated)
# ---------------------------------------------------------------------------
def _render_artifacts(msg: dict):
    """Render charts, exports, and tool activity for an assistant message."""
    for path in msg.get("charts", []):
        if os.path.exists(path):
            st.image(path, width="stretch")

    for path in msg.get("exports", []):
        if os.path.exists(path):
            with open(path, "rb") as f:
                st.download_button(
                    f"Download {os.path.basename(path)}",
                    f.read(),
                    file_name=os.path.basename(path),
                    mime="text/csv",
                )

    tool_calls = msg.get("tool_calls", [])
    if tool_calls:
        with st.expander("Tool Activity", expanded=False):
            for tc in tool_calls:
                st.markdown(
                    f'<span class="dm-tool-badge">{ICONS["bolt"]} {tc["tool"]}</span>',
                    unsafe_allow_html=True,
                )
                if "args" in tc:
                    st.code(json.dumps(tc["args"], indent=2), language="json")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
        <span style="color:var(--secondary);">{ICONS['database']}</span>
        <span style="font-family:'Fira Code',monospace; font-size:1.1rem; font-weight:700; color:#fff;">
            DataMind<span style="color:var(--cta);">AI</span>
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="dm-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="dm-section-label">{ICONS["upload"]} &nbsp;Dataset</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, uploaded_file.name)

        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            df = pd.read_csv(filepath) if uploaded_file.name.endswith(".csv") else pd.read_excel(filepath)
            set_dataset(df)
            st.session_state.dataset_loaded = True
            st.session_state.dataset_path = filepath
            st.session_state.dataset_name = uploaded_file.name

            st.markdown(f'<span class="dm-status-loaded">{ICONS["check"]} {uploaded_file.name}</span>', unsafe_allow_html=True)
            st.markdown(f"**{df.shape[0]}** rows · **{df.shape[1]}** columns")

            with st.expander("Preview Data", expanded=False):
                st.dataframe(df.head(10), width="stretch", height=250)

            with st.expander("Column Info", expanded=False):
                st.dataframe(
                    pd.DataFrame({"Type": df.dtypes.astype(str), "Non-Null": df.count(), "Unique": df.nunique()}),
                    width="stretch",
                )
        except Exception as e:
            st.error(f"Error loading file: {e}")
    else:
        st.markdown(f'<span class="dm-status-empty">{ICONS["folder"]} No dataset</span>', unsafe_allow_html=True)
        st.caption("Upload a CSV or Excel file to get started.")

    # Sample data
    st.markdown('<hr class="dm-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="dm-section-label">{ICONS["database"]} &nbsp;Sample Data</div>', unsafe_allow_html=True)

    if st.button("Load Sales Dataset", use_container_width=True):
        sample_path = "sample_data/sales_data.csv"
        if os.path.exists(sample_path):
            df = pd.read_csv(sample_path)
            set_dataset(df)
            st.session_state.dataset_loaded = True
            st.session_state.dataset_path = sample_path
            st.session_state.dataset_name = "sales_data.csv"
            st.rerun()
        else:
            st.error("Sample data not found.")

    # Sample queries
    st.markdown('<hr class="dm-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="dm-section-label">{ICONS["sparkles"]} &nbsp;Try These</div>', unsafe_allow_html=True)

    for q in [
        "Show me a summary of the dataset",
        "What's the average revenue by region?",
        "Create a bar chart of revenue by product",
        "Which region has the highest total sales?",
        "Show the correlation between units and revenue",
        "Create a pie chart of sales by category",
        "Export the top 10 revenue entries to CSV",
    ]:
        st.markdown(f'<div class="dm-query-pill">{ICONS["message"]} {q}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="dm-header">
    <div class="dm-title">DataMind<span class="dm-title-accent">AI</span></div>
    <div class="dm-subtitle">Natural Language Data Analyst · powered by <code>groq.tool_calling</code></div>
</div>
""", unsafe_allow_html=True)

# Feature cards (only on empty chat)
if not st.session_state.messages:
    st.markdown(f"""
    <div class="dm-features">
        <div class="dm-feature-card">
            <div class="dm-feature-icon blue">{ICONS['search']}</div>
            <div class="dm-feature-title">Smart Queries</div>
            <div class="dm-feature-desc">Ask questions in plain English</div>
        </div>
        <div class="dm-feature-card">
            <div class="dm-feature-icon amber">{ICONS['chart']}</div>
            <div class="dm-feature-title">Auto Charts</div>
            <div class="dm-feature-desc">Generate visualizations instantly</div>
        </div>
        <div class="dm-feature-card">
            <div class="dm-feature-icon green">{ICONS['calc']}</div>
            <div class="dm-feature-title">Data Analysis</div>
            <div class="dm-feature-desc">Stats, grouping, filtering</div>
        </div>
        <div class="dm-feature-card">
            <div class="dm-feature-icon cyan">{ICONS['download']}</div>
            <div class="dm-feature-title">Export</div>
            <div class="dm-feature-desc">Save results as CSV files</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="dm-user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        css_class = "dm-assistant-msg dm-error-msg" if msg["content"].startswith("Error:") else "dm-assistant-msg"
        st.markdown(f'<div class="{css_class}">{msg["content"]}</div>', unsafe_allow_html=True)
        _render_artifacts(msg)


# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
placeholder = "Ask a question about your data..." if st.session_state.dataset_loaded else "Upload a dataset first, then ask away..."

if prompt := st.chat_input(placeholder):
    if not os.getenv("GROQ_API_KEY") and not os.path.exists(".env"):
        st.error("Set your GROQ_API_KEY in a .env file. See .env.example for the template.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="dm-user-msg">{prompt}</div>', unsafe_allow_html=True)

    with st.spinner("Analyzing your data..."):
        try:
            result = run_agent(
                user_message=prompt,
                messages=st.session_state.agent_messages,
                dataset_path=st.session_state.dataset_path if st.session_state.dataset_loaded else None,
            )
            st.session_state.agent_messages = result["messages"]

            assistant_msg = {
                "role": "assistant",
                "content": result["response"],
                "charts": result.get("charts", []),
                "exports": result.get("exports", []),
                "tool_calls": result.get("tool_calls_log", []),
            }
            st.session_state.messages.append(assistant_msg)

            st.markdown(f'<div class="dm-assistant-msg">{result["response"]}</div>', unsafe_allow_html=True)
            _render_artifacts(assistant_msg)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.markdown(f'<div class="dm-assistant-msg dm-error-msg">{error_msg}</div>', unsafe_allow_html=True)

    st.rerun()
