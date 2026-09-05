"""
agent.py — Agentic orchestration loop with self-correcting REPL and LPU telemetry.

Features:
1. Groq LPU tool calling with sub-second execution loop
2. Self-correcting debug loop (tracks errors, repairs malformed code, records fix rate diff)
3. Full telemetry instrumentation: Latency (ms), Tokens/sec, Token Breakdown, Execution Timers
4. Dual Visualization support (Interactive Plotly + Publication Matplotlib)
"""

import json
import logging
import os
import time
from groq import Groq
from dotenv import load_dotenv

from tools import (
    load_dataset,
    run_query,
    create_interactive_chart,
    create_chart,
    export_results,
    clean_data,
    get_data_profile,
    generate_executive_report,
)
from tool_schemas import TOOL_SCHEMAS

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "llama-3.3-70b-versatile"
MAX_ITERATIONS = 10
TEMPERATURE = 0.1

SYSTEM_PROMPT = """You are DataMind AI — an elite autonomous data analyst and quantitative intelligence assistant.
You help users explore, analyze, and visualize datasets through natural language conversation.

**Your Toolkit:**
1. `load_dataset`: Inspect uploaded datasets (CSV, Excel, TSV). Call this first if no dataset is loaded.
2. `run_query`: Execute sandboxed Pandas code. Assign your final answer to `result`.
3. `create_interactive_chart`: Generate interactive Plotly charts with hover tooltips, zoom, and rich aesthetics. Assign the figure to `fig`. Preferred for UI visualizations.
4. `create_chart`: Generate publication-grade Matplotlib charts saved as PNG images.
5. `export_results`: Save analysis or filtered slices to CSV files.
6. `clean_data`: Perform dataset cleaning (impute, drop nulls, deduplicate, filter outliers).
7. `get_data_profile`: Obtain an automated statistical profile with distributions, correlations, and skewness.
8. `generate_executive_report`: Compile a full analytical executive summary report.

**Operational Guidelines:**
- For visualizations, prefer `create_interactive_chart` using Plotly Express (`px`) so users can interact with the charts.
- Write clean, vectorized Pandas code.
- If a query fails or raises an error, carefully diagnose the traceback and immediately self-correct your code.
- Provide crisp, data-driven analytical takeaways after running tools. Highlight key metrics with bold numbers.
"""

AVAILABLE_FUNCTIONS = {
    "load_dataset": load_dataset,
    "run_query": run_query,
    "create_interactive_chart": create_interactive_chart,
    "create_chart": create_chart,
    "export_results": export_results,
    "clean_data": clean_data,
    "get_data_profile": get_data_profile,
    "generate_executive_report": generate_executive_report,
}


def run_agent(
    user_message: str,
    messages: list | None = None,
    dataset_path: str | None = None,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    Run the agentic tool calling loop with self-correcting REPL and Groq LPU telemetry.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "response": "Groq API key not found. Please add GROQ_API_KEY to your .env file.",
            "messages": messages or [],
            "charts": [],
            "interactive_charts": [],
            "exports": [],
            "tool_calls_log": [],
            "telemetry": {},
        }

    client = Groq(api_key=api_key)

    if messages is None:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if dataset_path:
        context = f"\n[System: Active dataset path is '{dataset_path}'.]"
        user_message_with_context = user_message + context
    else:
        user_message_with_context = user_message

    messages.append({"role": "user", "content": user_message_with_context})

    charts = []
    interactive_charts = []
    exports = []
    tool_calls_log = []
    self_corrections = []

    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_inference_time = 0.0

    # Pending error tracking for self-correction diffs
    last_failed_call: dict | None = None

    iteration = 0
    while iteration < MAX_ITERATIONS:
        iteration += 1
        t_start = time.perf_counter()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=TEMPERATURE,
                max_tokens=4096,
            )
            t_call = time.perf_counter() - t_start
            total_inference_time += t_call

            if response.usage:
                total_prompt_tokens += response.usage.prompt_tokens or 0
                total_completion_tokens += response.usage.completion_tokens or 0

        except Exception as api_err:
            err_str = str(api_err)
            if "tool_use_failed" in err_str:
                messages.append({
                    "role": "user",
                    "content": "[System: Your tool call was malformed. Please fix the arguments and retry.]",
                })
                continue

            logger.error("Groq API error: %s", err_str)
            return {
                "response": f"Groq API error: {err_str}",
                "messages": messages,
                "charts": charts,
                "interactive_charts": interactive_charts,
                "exports": exports,
                "tool_calls_log": tool_calls_log,
                "telemetry": {
                    "model": model,
                    "total_inference_time_ms": round(total_inference_time * 1000, 1),
                    "total_tokens": total_prompt_tokens + total_completion_tokens,
                    "self_corrections": self_corrections,
                },
            }

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if not tool_calls:
            messages.append({"role": "assistant", "content": response_message.content or ""})
            tokens_per_sec = (
                round(total_completion_tokens / total_inference_time, 1)
                if total_inference_time > 0
                else 0.0
            )
            return {
                "response": response_message.content or "",
                "messages": messages,
                "charts": charts,
                "interactive_charts": interactive_charts,
                "exports": exports,
                "tool_calls_log": tool_calls_log,
                "telemetry": {
                    "model": model,
                    "total_inference_time_ms": round(total_inference_time * 1000, 1),
                    "tokens_per_sec": tokens_per_sec,
                    "prompt_tokens": total_prompt_tokens,
                    "completion_tokens": total_completion_tokens,
                    "total_tokens": total_prompt_tokens + total_completion_tokens,
                    "iterations": iteration,
                    "self_corrections": self_corrections,
                },
            }

        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            try:
                function_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                function_args = {}

            log_entry = {
                "tool": function_name,
                "args": function_args,
                "iteration": iteration,
            }

            if function_name in AVAILABLE_FUNCTIONS:
                fn = AVAILABLE_FUNCTIONS[function_name]
                try:
                    function_response = fn(**function_args)
                except TypeError as e:
                    function_response = json.dumps({"status": "error", "error": f"Invalid arguments: {str(e)}"})
                except Exception as e:
                    function_response = json.dumps({"status": "error", "error": f"Execution error: {str(e)}"})
            else:
                function_response = json.dumps({"status": "error", "error": f"Unknown tool: {function_name}"})

            log_entry["result"] = function_response
            tool_calls_log.append(log_entry)

            # Inspect result for self-correction tracking & artifacts
            try:
                parsed = json.loads(function_response)
                is_error = parsed.get("status") == "error" or "error" in parsed

                if is_error:
                    last_failed_call = {
                        "tool": function_name,
                        "code": function_args.get("code", ""),
                        "error": parsed.get("error", "Unknown error"),
                        "iteration": iteration,
                    }
                else:
                    # If this succeeded and we previously had an error on this tool, record self-correction!
                    if last_failed_call and last_failed_call["tool"] == function_name:
                        self_corrections.append({
                            "tool": function_name,
                            "error": last_failed_call["error"],
                            "failed_code": last_failed_call["code"],
                            "repaired_code": function_args.get("code", ""),
                            "resolved_at_iteration": iteration,
                        })
                        last_failed_call = None

                    if "chart_path" in parsed:
                        charts.append(parsed["chart_path"])
                    if "figure_json" in parsed:
                        interactive_charts.append({
                            "title": parsed.get("title", "Interactive Visual"),
                            "figure_json": parsed["figure_json"],
                        })
                    if "filepath" in parsed:
                        exports.append(parsed["filepath"])

            except (json.JSONDecodeError, TypeError):
                pass

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

    final_msg = "Analysis limit reached (10 iterations). Here are the compiled insights."
    messages.append({"role": "assistant", "content": final_msg})
    tokens_per_sec = (
        round(total_completion_tokens / total_inference_time, 1)
        if total_inference_time > 0
        else 0.0
    )
    return {
        "response": final_msg,
        "messages": messages,
        "charts": charts,
        "interactive_charts": interactive_charts,
        "exports": exports,
        "tool_calls_log": tool_calls_log,
        "telemetry": {
            "model": model,
            "total_inference_time_ms": round(total_inference_time * 1000, 1),
            "tokens_per_sec": tokens_per_sec,
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_prompt_tokens + total_completion_tokens,
            "iterations": iteration,
            "self_corrections": self_corrections,
        },
    }
