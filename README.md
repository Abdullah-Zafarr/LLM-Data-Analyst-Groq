# DataMind AI — Natural Language Data Analyst

> **Chat with your data using AI.** Upload any CSV/Excel file and ask questions in plain English. The AI writes and executes Pandas code, creates charts, and exports results — all powered by **Groq Tool Calling**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)

### Interface

![DataMind AI Interface](assets/interface%201.PNG)

### Analysis Output

![DataMind AI Output](assets/output%202.PNG)

---

## How It Works

This project demonstrates **Groq's local tool calling (function calling)** — the AI model decides which tools to call, generates the arguments, and our code executes them locally.

```
User: "What's the average revenue by region?"
  ↓
Groq LLM → calls run_query(code="result = df.groupby('Region')['Revenue'].mean()")
  ↓
Tool executes Pandas code → returns JSON result
  ↓
Groq LLM → formats a natural language answer
```

### Tools

| Tool | Description |
|------|-------------|
| `load_dataset` | Load CSV/Excel files and return a data summary |
| `run_query` | Execute Pandas queries on the loaded data |
| `create_chart` | Generate Matplotlib visualizations |
| `export_results` | Save analysis results to CSV |

---

## Project Structure

```
├── app.py              # Streamlit frontend (OLED dark theme)
├── agent.py            # Agentic orchestration loop (max 10 iterations)
├── tools.py            # Tool implementations (sandboxed execution)
├── tool_schemas.py     # Groq JSON tool definitions
├── pyproject.toml      # Dependencies (managed by uv)
├── .env.example        # API key template
├── sample_data/
│   └── sales_data.csv  # 50-row demo dataset
└── README.md
```

---

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

Or with pip:
```bash
pip install groq streamlit pandas matplotlib openpyxl python-dotenv numpy
```

### 2. Set Up API Key

```bash
cp .env.example .env
# Edit .env and add your Groq API key
# Get one free at https://console.groq.com/keys
```

### 3. Run

```bash
uv run streamlit run app.py
```

### 4. Try It

1. Upload a CSV/Excel file (or click **Load Sales Dataset** for the demo)
2. Ask questions like:
   - *"Show me a summary of the dataset"*
   - *"What's the average revenue by region?"*
   - *"Create a bar chart of revenue by product"*
   - *"Export the top 10 revenue entries to CSV"*

---

## Key Concepts

- **Tool Schemas** — JSON definitions telling the LLM what tools exist
- **Agentic Loop** — Multi-turn tool calling where the AI chains tools
- **Sandboxed Execution** — Safe `exec/eval` with restricted namespace
- **Structured Outputs** — Tools return JSON the model can interpret

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Groq (`llama-3.3-70b-versatile`) |
| Backend | Python, Pandas, NumPy |
| Charts | Matplotlib (dark theme) |
| Frontend | Streamlit + custom CSS |
| Package Manager | uv |

----

## License

MIT  use it, learn from it, build on it.
