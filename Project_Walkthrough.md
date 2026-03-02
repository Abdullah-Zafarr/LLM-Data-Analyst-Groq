# Natural Language Data Analyst: Internal Workings & Blueprint

This document explains the internal logic of the Tool-Calling project, designed to act as a senior engineer's guide for rebuilding the system from scratch.

---

## 1. High-Level Architecture
The project follows a **Modular Agentic Architecture**. It separates the UI, the AI's "Brain," the "Menu" of capabilities, and the "Execution" of those capabilities into four distinct layers.

- **`app.py`**: User Interface (Streamlit).
- **`agent.py`**: The Orchestrator (Groq API Connection).
- **`tool_schemas.py`**: Configuration (JSON descriptions of tools).
- **`tools.py`**: Backend Logic (Pandas, Matplotlib, Sandbox).

---

## 2. Defining AI Capabilities (`tool_schemas.py`)
This file defines the **Interface** between the AI and your local machine.
- **Tool Calling**: We provide the LLM with a JSON "menu" of functions.
- **Embedded Prompting**: We use descriptive strings inside the JSON to guide the AI’s behavior (e.g., *"You MUST assign the final result to a variable named 'result'"*).
- **Constraint Management**: Using `enums` for data cleaning operations limits "hallucinations" by forcing the AI to pick from a list.

---

## 3. The Execution Muscle (`tools.py`)
This file handles the actual data manipulation.
- **The Sandbox (`_sandbox`)**: A critical security layer. It creates a restricted Python environment that removes unsafe "built-ins" (like `open` or `import os`) to prevent the AI from executing malicious system commands.
- **Dynamic Execution**: It uses `exec(code, globals, locals)` to run the AI-generated code string. The result is then "plucked" from the local variable dictionary and returned to the AI as a JSON string.
- **Matplotlib Agg Backend**: `matplotlib.use("Agg")` ensures charts are rendered as images in background memory rather than trying to open a desktop GUI window.

---

## 4. The Orchestration Loop (`agent.py`)
This is the **"Agentic"** part of the code. Instead of a single API call, it uses a `while` loop to process multi-step tasks.
- **Loop Logic**:
    1. Ask Groq: "What should I do to answer the user?"
    2. If Groq says "Use tool X," execute function X in `tools.py`.
    3. Update Groq: "I ran tool X and here is the output."
    4. Repeat until Groq says "I have the final answer."
- **Context Injection**: On initial load, we silently tell the AI about the file path so it proactively uses the `load_dataset` tool.

---

## 5. UI & State Management (`app.py`)
Streamlit uses a **Top-Down Execution** model, meaning the script runs from scratch on every user action.
- **`st.session_state`**: This is the only way to store "memory" (chat history, data paths) between those re-runs.
- **Chat Loop**: Every time the user types a prompt, the UI:
    1. Appends the message to state.
    2. Calls `run_agent()` and waits for the loop to finish.
    3. Saves the results and calls `st.rerun()` to refresh the screen with the new content.

---

## Summary of Patterns
- **Role-Based Separation**: Decoupling the LLM's "decision logic" from the system's "execution logic."
- **Security-First Execution**: Never running LLM code without a sandbox.
- **State Persistence**: Using persistent containers (`session_state`) for stateless UI frameworks (Streamlit).

---

*Notes compiled by Antigravity AI for Abdullah Zafarr.*
