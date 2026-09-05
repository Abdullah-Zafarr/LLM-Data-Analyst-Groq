"""
app.py — Flagship Mission Control UI for DataMind AI.

Design System: Dark Cosmic Engine · Fira Code / Fira Sans · Neon Cyan #06B6D4 · Indigo #6366F1 · Emerald #10B981
Features:
1. Groq LPU Telemetry Strip (Latency, Tokens/Sec, AST Sandboxing, REPL Repair Engine)
2. Five Dedicated Workspace Tabs:
   - 💬 Autonomous Copilot & Interactive Chat
   - 🔬 Automated EDA & Health Profiler
   - 📑 Data Explorer Studio
   - 🛠️ Visual Cleaning Recipes
   - 📊 Executive Report Generator
3. Context-Aware Clickable Prompt Chips
4. Dual Visualization Engine (Interactive Plotly + High-Res Matplotlib)
5. Multi-Domain Curated Datasets (Retail Sales, SaaS Churn, Clinical Trials)
"""

import html
import json
import os
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import run_agent, DEFAULT_MODEL
from tools import set_dataset, get_dataset, clear_dataset, clean_data, generate_executive_report

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="DataMind AI — Autonomous Data Analyst",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# High-Tech Styling & Design System
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-canvas: #06090F;
        --bg-panel: #0A0F1D;
        --bg-card: #0F172A;
        --bg-card-hover: #162038;
        --border-subtle: rgba(255, 255, 255, 0.07);
        --border-focus: rgba(6, 182, 212, 0.4);
        --cyan: #06B6D4;
        --cyan-glow: rgba(6, 182, 212, 0.15);
        --indigo: #6366F1;
        --emerald: #10B981;
        --amber: #F59E0B;
        --rose: #F43F5E;
        --text-main: #F1F5F9;
        --text-dim: #94A3B8;
        --text-faint: #475569;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #0c1427 0%, var(--bg-canvas) 75%) !important;
        font-family: 'Fira Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-main) !important;
    }

    .main .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1380px !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #080C16 !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] * {
        font-family: 'Fira Sans', sans-serif !important;
    }

    /* Header & Telemetry Strip */
    .dm-header-wrap {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 1.4rem;
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid var(--border-subtle);
        backdrop-filter: blur(14px);
        border-radius: 14px;
        margin-bottom: 1.2rem;
    }
    .dm-brand-title {
        font-family: 'Fira Code', monospace;
        font-size: 1.45rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .dm-badge-lpu {
        font-family: 'Fira Code', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        background: rgba(6, 182, 212, 0.12);
        color: var(--cyan);
        border: 1px solid rgba(6, 182, 212, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .dm-telemetry-ribbon {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .dm-tele-item {
        font-family: 'Fira Code', monospace;
        font-size: 0.78rem;
        color: var(--text-dim);
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .dm-tele-val {
        color: #38BDF8;
        font-weight: 600;
    }
    .dm-pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: var(--emerald);
        box-shadow: 0 0 10px var(--emerald);
        display: inline-block;
    }

    /* Metric Cards */
    .dm-metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin-bottom: 1.4rem;
    }
    .dm-kpi-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        position: relative;
        overflow: hidden;
        transition: all 0.2s ease;
    }
    .dm-kpi-card:hover {
        border-color: var(--border-focus);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--cyan-glow);
    }
    .dm-kpi-label {
        font-family: 'Fira Code', monospace;
        font-size: 0.72rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.35rem;
    }
    .dm-kpi-value {
        font-family: 'Fira Code', monospace;
        font-size: 1.55rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .dm-kpi-sub {
        font-size: 0.75rem;
        color: var(--text-faint);
        margin-top: 0.2rem;
    }

    /* Chat Elements */
    .dm-chat-user {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        border: 1px solid rgba(59, 130, 246, 0.4);
        border-radius: 14px 14px 2px 14px;
        padding: 0.85rem 1.2rem;
        max-width: 82%;
        margin-left: auto;
        margin-bottom: 0.9rem;
        color: #FFFFFF;
        font-size: 0.94rem;
        line-height: 1.5;
        box-shadow: 0 4px 18px rgba(30, 58, 138, 0.35);
    }
    .dm-chat-assistant {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid var(--border-subtle);
        border-radius: 14px 14px 14px 2px;
        padding: 1.1rem 1.35rem;
        margin-bottom: 0.9rem;
        color: var(--text-main);
        font-size: 0.94rem;
        line-height: 1.6;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    .dm-telemetry-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(6, 182, 212, 0.08);
        border: 1px solid rgba(6, 182, 212, 0.25);
        border-radius: 6px;
        padding: 3px 9px;
        font-family: 'Fira Code', monospace;
        font-size: 0.72rem;
        color: var(--cyan);
        margin-bottom: 0.8rem;
    }
    .dm-correction-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 6px;
        padding: 4px 10px;
        font-family: 'Fira Code', monospace;
        font-size: 0.75rem;
        color: var(--amber);
        margin-bottom: 0.8rem;
        font-weight: 600;
    }

    /* Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        padding: 6px 8px !important;
        margin-bottom: 1.5rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Fira Code', monospace !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: var(--text-dim) !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(6, 182, 212, 0.15) !important;
        color: #38BDF8 !important;
        border: 1px solid rgba(6, 182, 212, 0.35) !important;
        font-weight: 600 !important;
    }

    /* Quick Action Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-family: 'Fira Code', monospace !important;
        font-size: 0.8rem !important;
        transition: all 0.18s ease !important;
    }

    /* Hide default Streamlit fluff */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
DEFAULTS = {
    "messages": [],
    "agent_messages": None,
    "dataset_loaded": False,
    "dataset_path": None,
    "dataset_name": None,
    "model": DEFAULT_MODEL,
    "last_telemetry": {},
    "active_prompt": None,
    "history_log": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Auto-sync active dataset into memory if loaded
if st.session_state.dataset_loaded and get_dataset() is None and st.session_state.dataset_path:
    if os.path.exists(st.session_state.dataset_path):
        try:
            df = pd.read_csv(st.session_state.dataset_path) if st.session_state.dataset_path.endswith(".csv") else pd.read_excel(st.session_state.dataset_path)
            set_dataset(df)
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Sidebar Setup
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom: 0.3rem;">
        <span style="font-size: 1.6rem;">⚡</span>
        <div>
            <div style="font-family:'Fira Code', monospace; font-size:1.15rem; font-weight:700; color:#FFF; letter-spacing:-0.5px;">
                DataMind<span style="color:#06B6D4;">.AI</span>
            </div>
            <div style="font-family:'Fira Code', monospace; font-size:0.68rem; color:#64748B;">
                REPL & LPU Data Analyst
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.07); margin: 0.8rem 0;'>", unsafe_allow_html=True)

    # Model Engine Picker
    st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.72rem; color:#94A3B8; text-transform:uppercase; margin-bottom:4px;'>LPU Engine</div>", unsafe_allow_html=True)
    selected_model = st.selectbox(
        "Select Model",
        options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        index=0 if st.session_state.model == "llama-3.3-70b-versatile" else 1,
        label_visibility="collapsed",
    )
    st.session_state.model = selected_model

    # Groq API Key Input
    st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.07); margin: 0.8rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.72rem; color:#94A3B8; text-transform:uppercase; margin-bottom:4px;'>Groq API Key</div>", unsafe_allow_html=True)
    env_k = os.getenv("GROQ_API_KEY", "")
    is_valid_default = bool(env_k and env_k != "your_groq_api_key_here")
    api_key_input = st.text_input(
        "Groq API Key",
        value=env_k if is_valid_default else "",
        type="password",
        placeholder="gsk_...",
        label_visibility="collapsed",
        help="Enter your Groq API key or set GROQ_API_KEY in .env"
    )
    if api_key_input:
        os.environ["GROQ_API_KEY"] = api_key_input

    # Dataset Ingestion Section
    st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.07); margin: 0.8rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.72rem; color:#94A3B8; text-transform:uppercase; margin-bottom:4px;'>Dataset Ingestion</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload dataset",
        type=["csv", "tsv", "xlsx", "xls"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, uploaded_file.name)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            df = pd.read_csv(filepath) if uploaded_file.name.endswith((".csv", ".tsv")) else pd.read_excel(filepath)
            set_dataset(df)
            st.session_state.dataset_loaded = True
            st.session_state.dataset_path = filepath
            st.session_state.dataset_name = uploaded_file.name
        except Exception as err:
            st.error(f"Ingestion error: {err}")

    # Curated Demo Datasets (3 diverse domains)
    st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.72rem; color:#94A3B8; text-transform:uppercase; margin: 0.7rem 0 4px;'>Curated Datasets</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛒 Sales Data", use_container_width=True):
            p = "sample_data/sales_data.csv"
            if os.path.exists(p):
                df = pd.read_csv(p)
                set_dataset(df)
                st.session_state.dataset_loaded = True
                st.session_state.dataset_path = p
                st.session_state.dataset_name = "sales_data.csv"
                st.session_state.agent_messages = None
                st.rerun()
    with c2:
        if st.button("🔄 SaaS Churn", use_container_width=True):
            p = "sample_data/saas_churn.csv"
            if os.path.exists(p):
                df = pd.read_csv(p)
                set_dataset(df)
                st.session_state.dataset_loaded = True
                st.session_state.dataset_path = p
                st.session_state.dataset_name = "saas_churn.csv"
                st.session_state.agent_messages = None
                st.rerun()

    if st.button("🩺 Clinical Trials Telemetry", use_container_width=True):
        p = "sample_data/clinical_trials.csv"
        if os.path.exists(p):
            df = pd.read_csv(p)
            set_dataset(df)
            st.session_state.dataset_loaded = True
            st.session_state.dataset_path = p
            st.session_state.dataset_name = "clinical_trials.csv"
            st.session_state.agent_messages = None
            st.rerun()

    # Active Dataset Status Card
    if st.session_state.dataset_loaded and get_dataset() is not None:
        cur_df = get_dataset()
        st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.07); margin: 0.8rem 0;'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(6,182,212,0.08); border:1px solid rgba(6,182,212,0.25); border-radius:8px; padding:8px 12px; margin-bottom:8px;">
            <div style="font-family:'Fira Code',monospace; font-size:0.8rem; font-weight:600; color:#38BDF8; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                ✓ {st.session_state.dataset_name}
            </div>
            <div style="font-family:'Fira Code',monospace; font-size:0.72rem; color:#94A3B8; margin-top:2px;">
                {cur_df.shape[0]:,} rows × {cur_df.shape[1]} cols
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Unload Dataset", use_container_width=True):
            clear_dataset()
            st.session_state.dataset_loaded = False
            st.session_state.dataset_path = None
            st.session_state.dataset_name = None
            st.session_state.agent_messages = None
            st.rerun()

    # Clear Conversation
    st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.07); margin: 0.8rem 0;'>", unsafe_allow_html=True)
    if st.button("Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_messages = None
        st.rerun()

# ---------------------------------------------------------------------------
# Top Header & Live Telemetry Strip
# ---------------------------------------------------------------------------
active_df = get_dataset()
tele = st.session_state.last_telemetry

st.markdown(f"""
<div class="dm-header-wrap">
    <div class="dm-brand-title">
        <span>DataMind AI</span>
        <span class="dm-badge-lpu">Groq LPU Engine</span>
    </div>
    <div class="dm-telemetry-ribbon">
        <div class="dm-tele-item">
            <span class="dm-pulse-dot"></span>
            <span>REPL Sandbox:</span>
            <span class="dm-tele-val">Active / AST</span>
        </div>
        <div class="dm-tele-item">
            <span>Model:</span>
            <span class="dm-tele-val">{st.session_state.model.replace('-versatile', '').replace('-instant', '')}</span>
        </div>
        <div class="dm-tele-item">
            <span>LPU Latency:</span>
            <span class="dm-tele-val">{tele.get('total_inference_time_ms', 0)}ms</span>
        </div>
        <div class="dm-tele-item">
            <span>Throughput:</span>
            <span class="dm-tele-val">{tele.get('tokens_per_sec', 0)} tok/s</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Workspace Tabs
# ---------------------------------------------------------------------------
tab_copilot, tab_eda, tab_explorer, tab_clean, tab_report = st.tabs([
    "💬 Analyst Copilot",
    "🔬 Automated EDA & Profiler",
    "📑 Data Explorer Studio",
    "🛠️ Visual Cleaning Recipes",
    "📊 Executive Report",
])

# ---------------------------------------------------------------------------
# Tab 1: Analyst Copilot (Chat & REPL)
# ---------------------------------------------------------------------------
with tab_copilot:
    # API Key Notice if not configured
    active_k = os.getenv("GROQ_API_KEY", "")
    has_valid_k = bool(active_k and active_k != "your_groq_api_key_here")
    if not has_valid_k:
        st.markdown("""
        <div style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3); border-radius:10px; padding:10px 14px; margin-bottom:12px;">
            <div style="font-family:'Fira Code',monospace; font-size:0.82rem; font-weight:600; color:#F59E0B;">
                ⚡ Groq API Key Needed for Autonomous Agent Chat
            </div>
            <div style="font-size:0.82rem; color:#CBD5E1; margin-top:3px;">
                Enter your key in the sidebar or in <code>.env</code>. (Free key: <a href="https://console.groq.com/keys" target="_blank" style="color:#38BDF8;">console.groq.com/keys</a>).
                <br><em>The other 4 tabs (EDA & Profiler, Data Explorer, Cleaning Recipes, and Executive Reports) work 100% locally without an API key!</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Contextual Smart Prompt Chips
    if active_df is not None:
        st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.75rem; color:#94A3B8; text-transform:uppercase; margin-bottom:6px;'>⚡ Contextual Quick Queries</div>", unsafe_allow_html=True)

        cols = list(active_df.columns)
        num_cols = active_df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = active_df.select_dtypes(include=["object", "category"]).columns.tolist()

        # Generate dataset-specific suggestions
        suggestions = []
        if "sales_data.csv" in (st.session_state.dataset_name or ""):
            suggestions = [
                "Total revenue and average unit price by Region",
                "Create an interactive bar chart of Revenue by Product",
                "Calculate correlation between Units and Revenue",
                "Detect revenue outliers using IQR and show top entries",
            ]
        elif "saas_churn.csv" in (st.session_state.dataset_name or ""):
            suggestions = [
                "Calculate churn rate across different ContractTypes",
                "Create an interactive scatter plot of MonthlyCharges vs TotalCharges colored by Churn",
                "Compare average NPS score and SupportTickets between Churn Yes vs No",
                "Identify top 5 highest paying customers at risk of churn",
            ]
        elif "clinical_trials.csv" in (st.session_state.dataset_name or ""):
            suggestions = [
                "Compare Biomarker improvement (Baseline vs PostTreatment) across Cohorts",
                "Create an interactive box plot of RecoveryDays by Cohort",
                "Identify correlation between Patient Age and EfficacyScore",
                "Summarize AdverseEvents breakdown by TreatmentGroup",
            ]
        else:
            # Dynamic suggestions based on data types
            if cat_cols and num_cols:
                suggestions.append(f"Aggregate {num_cols[0]} grouped by {cat_cols[0]}")
                suggestions.append(f"Create an interactive chart of {num_cols[0]} by {cat_cols[0]}")
            if len(num_cols) >= 2:
                suggestions.append(f"Compute correlation between {num_cols[0]} and {num_cols[1]}")
                suggestions.append(f"Detect statistical outliers in {num_cols[0]}")
            if len(suggestions) < 4:
                suggestions.append("Provide a statistical summary and health overview of this dataset")

        q_cols = st.columns(len(suggestions[:4]))
        for i, prompt_text in enumerate(suggestions[:4]):
            with q_cols[i]:
                if st.button(prompt_text, key=f"sug_{i}", use_container_width=True):
                    st.session_state.active_prompt = prompt_text
                    st.rerun()

    # Chat Messages Container
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="dm-chat-user">{html.escape(msg["content"])}</div>', unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            with st.container():
                st.markdown(f'<div class="dm-chat-assistant">{msg["content"]}</div>', unsafe_allow_html=True)

                # Telemetry Strip for this message
                m_tele = msg.get("telemetry", {})
                if m_tele:
                    st.markdown(f"""
                    <span class="dm-telemetry-badge">
                        ⚡ {m_tele.get('model', 'Groq')} · {m_tele.get('total_inference_time_ms', 0)}ms · {m_tele.get('tokens_per_sec', 0)} tok/s · {m_tele.get('total_tokens', 0)} tokens
                    </span>
                    """, unsafe_allow_html=True)

                # Self-Correction Display
                corrections = m_tele.get("self_corrections", [])
                if corrections:
                    for sc in corrections:
                        st.markdown(f"""
                        <div class="dm-correction-badge">
                            🛡️ Self-Corrected in 1 retry: Repaired {html.escape(sc.get('error', 'Execution Error'))}
                        </div>
                        """, unsafe_allow_html=True)
                        with st.expander("Inspect Self-Correction REPL Diff", expanded=False):
                            c_a, c_b = st.columns(2)
                            with c_a:
                                st.caption("❌ Errored Code:")
                                st.code(sc.get("failed_code", ""), language="python")
                            with c_b:
                                st.caption("✓ Repaired Code:")
                                st.code(sc.get("repaired_code", ""), language="python")

                # Interactive Plotly Figures
                for chart_item in msg.get("interactive_charts", []):
                    try:
                        fig = pio.from_json(chart_item["figure_json"])
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass

                # Static Matplotlib Charts
                for path in msg.get("charts", []):
                    if os.path.exists(path):
                        st.image(path, use_container_width=True)

                # CSV Download Artifacts
                for path in msg.get("exports", []):
                    if os.path.exists(path):
                        with open(path, "rb") as f:
                            st.download_button(
                                f"📥 Download {os.path.basename(path)}",
                                f.read(),
                                file_name=os.path.basename(path),
                                mime="text/csv",
                                key=f"dl_{path}_{time.time()}",
                            )

                # Tool Call Inspector
                tool_calls = msg.get("tool_calls", [])
                if tool_calls:
                    with st.expander("🛠️ Inspect Tool Execution Trace", expanded=False):
                        for tc in tool_calls:
                            st.markdown(f"**Step {tc.get('iteration', '?')}: `{tc['tool']}`**")
                            if "args" in tc and "code" in tc["args"]:
                                st.code(tc["args"]["code"], language="python")
                            elif "args" in tc:
                                st.json(tc["args"])

    # Chat Input Handling
    query_to_run = None
    if st.session_state.active_prompt:
        query_to_run = st.session_state.active_prompt
        st.session_state.active_prompt = None
    else:
        prompt_input = st.chat_input("Ask a data analytics question, request charts, or run queries...")
        if prompt_input:
            query_to_run = prompt_input

    if query_to_run:
        cur_k = os.getenv("GROQ_API_KEY", "")
        if not cur_k or cur_k == "your_groq_api_key_here":
            st.error("⚠️ Please enter a valid Groq API key in the sidebar or .env file to enable AI queries. (Free key: https://console.groq.com/keys)")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": query_to_run})

        with st.spinner("Analyzing dataset with Groq LPU engine..."):
            try:
                res = run_agent(
                    user_message=query_to_run,
                    messages=st.session_state.agent_messages,
                    dataset_path=st.session_state.dataset_path if st.session_state.dataset_loaded else None,
                    model=st.session_state.model,
                )
                st.session_state.agent_messages = res["messages"]
                st.session_state.last_telemetry = res.get("telemetry", {})

                assistant_msg = {
                    "role": "assistant",
                    "content": res["response"],
                    "charts": res.get("charts", []),
                    "interactive_charts": res.get("interactive_charts", []),
                    "exports": res.get("exports", []),
                    "tool_calls": res.get("tool_calls_log", []),
                    "telemetry": res.get("telemetry", {}),
                }
                st.session_state.messages.append(assistant_msg)

            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Analysis encountered an error: {str(e)}",
                    "telemetry": {},
                })

        st.rerun()

# ---------------------------------------------------------------------------
# Tab 2: Automated EDA & Health Profiler
# ---------------------------------------------------------------------------
with tab_eda:
    if active_df is None:
        st.info("Load or upload a dataset to generate automated EDA diagnostics.")
    else:
        # High-level Health Metrics
        n_rows, n_cols = active_df.shape
        missing_cells = active_df.isnull().sum().sum()
        total_cells = n_rows * n_cols
        missing_pct = round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0
        dup_rows = active_df.duplicated().sum()
        memory_mb = round(active_df.memory_usage(deep=True).sum() / (1024 * 1024), 2)

        st.markdown(f"""
        <div class="dm-metric-grid">
            <div class="dm-kpi-card">
                <div class="dm-kpi-label">Dataset Rows</div>
                <div class="dm-kpi-value">{n_rows:,}</div>
                <div class="dm-kpi-sub">Total observations</div>
            </div>
            <div class="dm-kpi-card">
                <div class="dm-kpi-label">Features / Columns</div>
                <div class="dm-kpi-value">{n_cols}</div>
                <div class="dm-kpi-sub">Dimensions</div>
            </div>
            <div class="dm-kpi-card">
                <div class="dm-kpi-label">Completeness</div>
                <div class="dm-kpi-value" style="color:#10B981;">{100 - missing_pct:.1f}%</div>
                <div class="dm-kpi-sub">{missing_cells} missing cells</div>
            </div>
            <div class="dm-kpi-card">
                <div class="dm-kpi-label">Duplicate Rows</div>
                <div class="dm-kpi-value" style="color:{'#10B981' if dup_rows == 0 else '#F59E0B'};">{dup_rows}</div>
                <div class="dm-kpi-sub">Identical records</div>
            </div>
            <div class="dm-kpi-card">
                <div class="dm-kpi-label">Memory Footprint</div>
                <div class="dm-kpi-value">{memory_mb} MB</div>
                <div class="dm-kpi-sub">In-memory RAM</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        eda_c1, eda_c2 = st.columns(2)

        with eda_c1:
            st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.85rem; font-weight:600; color:#38BDF8; margin-bottom:6px;'>Missing Values Distribution</div>", unsafe_allow_html=True)
            null_series = active_df.isnull().sum()
            null_series = null_series[null_series > 0]
            if null_series.empty:
                st.success("✓ Zero missing values detected across all columns.")
            else:
                fig_null = px.bar(
                    x=null_series.index,
                    y=null_series.values,
                    labels={"x": "Feature", "y": "Missing Count"},
                    color_discrete_sequence=["#F43F5E"],
                    template="plotly_dark",
                )
                fig_null.update_layout(
                    paper_bgcolor="#090D16",
                    plot_bgcolor="#0D1322",
                    font=dict(family="Fira Code, monospace", color="#E2E8F0"),
                    margin=dict(l=30, r=20, t=30, b=30),
                )
                st.plotly_chart(fig_null, use_container_width=True)

        with eda_c2:
            st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.85rem; font-weight:600; color:#38BDF8; margin-bottom:6px;'>Correlation Matrix (Numeric Features)</div>", unsafe_allow_html=True)
            num_df = active_df.select_dtypes(include=[np.number])
            if num_df.shape[1] >= 2:
                corr_mat = num_df.corr().round(2)
                fig_corr = px.imshow(
                    corr_mat,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale="Viridis",
                    template="plotly_dark",
                )
                fig_corr.update_layout(
                    paper_bgcolor="#090D16",
                    plot_bgcolor="#0D1322",
                    font=dict(family="Fira Code, monospace", color="#E2E8F0"),
                    margin=dict(l=30, r=20, t=30, b=30),
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("Insufficient numeric features for correlation analysis.")

        # Numeric Distribution Explorer
        st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.07); margin: 1.2rem 0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.9rem; font-weight:600; color:#38BDF8; margin-bottom:6px;'>Distribution & Outlier Inspection</div>", unsafe_allow_html=True)

        num_cols = active_df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            sel_num_col = st.selectbox("Select Numeric Feature", options=num_cols, index=0)
            col_a, col_b = st.columns(2)
            with col_a:
                fig_hist = px.histogram(
                    active_df,
                    x=sel_num_col,
                    marginal="box",
                    title=f"Distribution of {sel_num_col}",
                    color_discrete_sequence=["#06B6D4"],
                    template="plotly_dark",
                )
                fig_hist.update_layout(
                    paper_bgcolor="#090D16",
                    plot_bgcolor="#0D1322",
                    font=dict(family="Fira Code, monospace", color="#E2E8F0"),
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            with col_b:
                stats = active_df[sel_num_col].describe()
                st.markdown(f"""
                <div class="dm-kpi-card" style="margin-top:1.6rem;">
                    <div class="dm-kpi-label">{sel_num_col} Summary Statistics</div>
                    <div style="font-family:'Fira Code', monospace; font-size:0.85rem; line-height:1.9;">
                        • <b>Mean:</b> {stats['mean']:.2f}<br>
                        • <b>Std Dev:</b> {stats['std']:.2f}<br>
                        • <b>Min:</b> {stats['min']:.2f}<br>
                        • <b>25% (Q1):</b> {stats['25%']:.2f}<br>
                        • <b>50% (Median):</b> {stats['50%']:.2f}<br>
                        • <b>75% (Q3):</b> {stats['75%']:.2f}<br>
                        • <b>Max:</b> {stats['max']:.2f}<br>
                        • <b>Skewness:</b> {active_df[sel_num_col].skew():.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tab 3: Data Explorer Studio
# ---------------------------------------------------------------------------
with tab_explorer:
    if active_df is None:
        st.info("Load or upload a dataset to explore records.")
    else:
        st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.9rem; font-weight:600; color:#38BDF8; margin-bottom:8px;'>Interactive Data Grid</div>", unsafe_allow_html=True)

        exp_c1, exp_c2 = st.columns([3, 1])
        with exp_c1:
            search_query = st.text_input("🔍 Filter rows across all columns", placeholder="Type to filter...")
        with exp_c2:
            row_limit = st.selectbox("Display Limit", [25, 50, 100, "All"], index=0)

        view_df = active_df
        if search_query:
            mask = view_df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
            view_df = view_df[mask]

        if row_limit != "All":
            st.dataframe(view_df.head(int(row_limit)), use_container_width=True, height=450)
            st.caption(f"Showing {min(int(row_limit), len(view_df))} of {len(view_df)} matched rows.")
        else:
            st.dataframe(view_df, use_container_width=True, height=450)

        # Column Schema Breakdown
        st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.07); margin: 1.2rem 0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.85rem; font-weight:600; color:#38BDF8; margin-bottom:8px;'>Feature Schema & Types</div>", unsafe_allow_html=True)
        schema_df = pd.DataFrame({
            "Column": active_df.columns,
            "Data Type": [str(t) for t in active_df.dtypes],
            "Non-Null Count": active_df.count().values,
            "Null Count": active_df.isnull().sum().values,
            "Unique Values": active_df.nunique().values,
            "Sample Value": [str(active_df[c].dropna().iloc[0]) if not active_df[c].dropna().empty else "N/A" for c in active_df.columns]
        })
        st.dataframe(schema_df, use_container_width=True)

# ---------------------------------------------------------------------------
# Tab 4: Visual Cleaning Recipes
# ---------------------------------------------------------------------------
with tab_clean:
    if active_df is None:
        st.info("Load or upload a dataset to execute cleaning transformations.")
    else:
        st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.9rem; font-weight:600; color:#38BDF8; margin-bottom:8px;'>One-Click Data Cleaning Recipes</div>", unsafe_allow_html=True)

        cl_c1, cl_c2 = st.columns(2)

        with cl_c1:
            st.markdown("##### 1. Handle Missing Values")
            impute_col = st.selectbox("Target Column for Imputation", options=["All Columns"] + list(active_df.columns))
            impute_strategy = st.selectbox("Imputation Strategy", ["mean", "median", "mode", "Drop Null Rows"])
            if st.button("Apply Imputation Recipe", use_container_width=True):
                if impute_strategy == "Drop Null Rows":
                    cols_arg = [impute_col] if impute_col != "All Columns" else None
                    res = json.loads(clean_data(operation="drop_na", columns=cols_arg))
                else:
                    cols_arg = [impute_col] if impute_col != "All Columns" else None
                    res = json.loads(clean_data(operation="fill_na", columns=cols_arg, value=impute_strategy))
                st.success(res.get("message", "Transformation applied."))
                st.rerun()

            st.markdown("##### 2. Deduplication")
            if st.button("Remove Duplicate Rows", use_container_width=True):
                res = json.loads(clean_data(operation="drop_duplicates"))
                st.success(res.get("message", "Deduplicated."))
                st.rerun()

        with cl_c2:
            st.markdown("##### 3. Outlier Removal (> 3 Std Deviations)")
            outlier_col = st.selectbox("Target Numeric Feature", options=["All Numeric Columns"] + active_df.select_dtypes(include=[np.number]).columns.tolist())
            if st.button("Filter Outliers", use_container_width=True):
                cols_arg = [outlier_col] if outlier_col != "All Numeric Columns" else None
                res = json.loads(clean_data(operation="filter_outliers", columns=cols_arg))
                st.success(res.get("message", "Outliers removed."))
                st.rerun()

            st.markdown("##### 4. Drop Redundant Columns")
            cols_to_drop = st.multiselect("Select Columns to Remove", options=list(active_df.columns))
            if st.button("Drop Selected Columns", use_container_width=True):
                if cols_to_drop:
                    res = json.loads(clean_data(operation="drop_cols", columns=cols_to_drop))
                    st.success(res.get("message", "Columns dropped."))
                    st.rerun()

# ---------------------------------------------------------------------------
# Tab 5: Executive Report Generator
# ---------------------------------------------------------------------------
with tab_report:
    if active_df is None:
        st.info("Load or upload a dataset to compile an executive intelligence report.")
    else:
        st.markdown("<div style='font-family:\"Fira Code\",monospace; font-size:0.9rem; font-weight:600; color:#38BDF8; margin-bottom:8px;'>Automated Executive Data Intelligence Report</div>", unsafe_allow_html=True)

        report_title = st.text_input("Report Title", value=f"Executive Intelligence Analysis — {st.session_state.dataset_name or 'Dataset'}")

        if st.button("⚡ Generate Report Now", use_container_width=True):
            with st.spinner("Compiling strategic analytical report..."):
                rep_json = json.loads(generate_executive_report(title=report_title))
                if rep_json.get("status") == "success":
                    st.session_state.latest_report = rep_json["report_markdown"]

        if "latest_report" in st.session_state and st.session_state.latest_report:
            st.markdown(st.session_state.latest_report)

            c_down1, c_down2 = st.columns(2)
            with c_down1:
                st.download_button(
                    "📥 Download Report (Markdown)",
                    data=st.session_state.latest_report,
                    file_name="Executive_Data_Report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with c_down2:
                html_export = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{report_title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; color: #1E293B; }}
h1 {{ color: #0F172A; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; }}
h2 {{ color: #1E40AF; margin-top: 25px; }}
code {{ background: #F1F5F9; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
</style>
</head>
<body>
{st.session_state.latest_report.replace('# ', '<h1>').replace('## ', '<h2>').replace('\n', '<br>')}
</body>
</html>"""
                st.download_button(
                    "📥 Download Report (HTML)",
                    data=html_export,
                    file_name="Executive_Data_Report.html",
                    mime="text/html",
                    use_container_width=True,
                )
