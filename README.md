# DataMind AI — Autonomous Conversational Data Analyst

> **Autonomous conversational data analyst translating natural language queries to sandboxed Pandas execution containers powered by Groq LPU inference and self-correcting debug loops.**

<p align="center">
  <a href="https://llm-data-analyst-groq.vercel.app"><img src="https://img.shields.io/badge/Live_Deployment-llm--data--analyst--groq.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Live on Vercel" /></a>
  <img src="https://img.shields.io/badge/Next.js_15-App_Router-000000?style=for-the-badge&logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-LPU_Inference-F55036?style=for-the-badge&logo=groq&logoColor=white" />
  <img src="https://img.shields.io/badge/REPL_Fix_Rate-91%25_Benchmark-10B981?style=for-the-badge" />
</p>

---

## ⚡ Architectural Overview

DataMind AI is engineered for production-grade data reasoning, combining **sub-second Groq LPU function calling** with a **sandboxed self-correcting REPL execution environment**.

```
User Query: "Identify top churn risk factors and plot monthly charges distribution"
  ↓
Groq LPU Engine (Llama 3.3 70B) → Emits tool call: run_query(code="...")
  ↓
Sandboxed REPL Container → Executes with restricted globals
  ├── [On Exception]: Intercepts traceback → Prompts self-correction diff loop (91% repair rate)
  └── [On Success]: Emits structured JSON + execution metrics
  ↓
Dual Visualizer Engine → Renders Plotly Interactive Graph + Telemetry Ribbon
```

---

## 🚀 Key Production Capabilities

### 1. 💬 Autonomous Copilot & Self-Correcting REPL
- **Dynamic Contextual Chips**: Generates dataset-specific quick queries automatically upon ingestion.
- **Traceback Self-Repair**: When code execution fails due to schema drift or syntax mismatches, the agent introspects the error, auto-repairs the query, and surfaces the before/after diff.
- **Full LPU Telemetry**: Displays per-turn latency (ms), token generation rate (tok/s), and sandbox execution overhead.

### 2. 🔬 Automated EDA & Health Profiler
- **Instant Health Scorecard**: Row counts, dimensions, completeness rate, duplicate records, and memory footprint.
- **Interactive Nulls Radar & Correlation Matrix**: Visual heatmap and missing value distributions powered by Plotly.
- **Distribution & Outlier Inspector**: Marginal box plots, histograms, IQR bounds, and skewness calculations.

### 3. 📑 Data Explorer Studio
- Full-text search and regex filtering across all columns simultaneously.
- Dynamic schema inspector showing inferred types, null counts, and distinct value cardinality.

### 4. 🛠️ One-Click Cleaning Recipes
- Automated visual transformations: Imputation (mean, median, mode), duplicate removal, 3-sigma outlier filtering, and column dropping.

### 5. 📊 Executive Intelligence Report Generator
- One-click synthesis of an executive briefing summarizing dataset architecture, statistical indicators, segment anomalies, and strategic actions.
- Downloadable in both **Markdown (.md)** and **HTML** formats.

---

## 🛠️ Tool Registry

| Tool | Engine | Description |
|------|--------|-------------|
| `load_dataset` | Pandas | Intelligent sampling (>50k rows), schema profiling, and memory storage |
| `run_query` | Sandboxed REPL | Vectorized Pandas execution with timing and traceback introspection |
| `create_interactive_chart` | Plotly Express | Responsive, zoomable charts with hover tooltips and custom themes |
| `create_chart` | Matplotlib | High-res 180-DPI publication graphics saved to disk |
| `export_results` | CSV / Series | Filtered dataset exports with download buttons |
| `clean_data` | Pipeline | In-place data transformations and schema remodeling |
| `get_data_profile` | NumPy / Stats | Statistical distributions, correlation matrix, and skewness metrics |
| `generate_executive_report` | Markdown / HTML | Strategic executive data intelligence summary |

---

## 📂 Project Structure

```
├── app.py                  # Streamlit Mission Control frontend (5 workspace tabs)
├── agent.py                # Groq LPU orchestration loop & self-correcting REPL
├── tools.py                # Sandboxed execution tools & Plotly/Matplotlib engines
├── tool_schemas.py         # JSON schema specifications for Groq function calling
├── sample_data/
│   ├── sales_data.csv      # Retail E-Commerce demo dataset
│   ├── saas_churn.csv      # B2B SaaS subscription & churn telemetry
│   └── clinical_trials.csv # Healthcare patient trial & biomarker telemetry
├── pyproject.toml          # uv package configuration
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone & Install Dependencies

```bash
uv sync
# Or with pip:
# pip install groq streamlit pandas plotly matplotlib openpyxl python-dotenv numpy
```

### 2. Configure Groq API Key

Copy `.env.example` to `.env` or enter your key directly in the sidebar UI:
```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
```
*(Get a free API key at [console.groq.com/keys](https://console.groq.com/keys))*

### 3. Launch Mission Control

```bash
uv run streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📄 License

MIT © [Abdullah Zafar](https://github.com/Abdullah-Zafarr)
