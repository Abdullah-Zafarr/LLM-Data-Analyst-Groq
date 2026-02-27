# Contributing to DataMind AI

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/Abdullah-Zafarr/LLM-Data-Analyst-Groq.git
   cd LLM-Data-Analyst-Groq
   ```

2. **Install dependencies** (using [uv](https://docs.astral.sh/uv/))
   ```bash
   uv sync
   ```

3. **Set up your API key**
   ```bash
   cp .env.example .env
   # Add your Groq API key to .env
   ```

4. **Run the app**
   ```bash
   uv run streamlit run app.py
   ```

## Project Structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit frontend (OLED dark theme) |
| `agent.py` | Agentic orchestration loop |
| `tools.py` | Sandboxed tool implementations |
| `tool_schemas.py` | Groq JSON tool definitions |

## Making Changes

1. **Create a branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow the existing code style**
   - Functions return JSON strings (Groq requirement for tools)
   - Use type hints for function signatures
   - Keep the sandbox restricted — only expose safe builtins

3. **Test your changes** by running the app and trying different queries

4. **Submit a PR** with a clear description of what changed and why

## Adding a New Tool

1. Implement the function in `tools.py` (must return a JSON string)
2. Add the JSON schema in `tool_schemas.py`
3. Register it in `AVAILABLE_FUNCTIONS` in `agent.py`
4. Update the system prompt in `agent.py` if needed

## Reporting Issues

Open an issue with:
- What you expected vs. what happened
- Steps to reproduce
- Your Python version and OS
