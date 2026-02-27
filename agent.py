"""
agent.py — Agentic orchestration loop for the Natural Language Data Analyst.

Implements the Groq tool calling loop:
1. Send user message + tool schemas to Groq
2. Check if model returns tool_calls
3. Execute each tool call locally
4. Append results to messages
5. Loop until model returns a final text response (max 10 iterations)
"""

import json
import logging
import os
from groq import Groq
from dotenv import load_dotenv

from tools import load_dataset, run_query, create_chart, export_results, clean_data
from tool_schemas import TOOL_SCHEMAS

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL = "llama-3.3-70b-versatile"
MAX_ITERATIONS = 10

SYSTEM_PROMPT = """You are an expert data analyst AI assistant. You help users explore, analyze, and visualize datasets through natural language conversation.

**Your workflow:**
1. When a user uploads a dataset, use `load_dataset` to examine it first.
2. Use `run_query` to perform data analysis by writing Pandas code. Always assign results to `result`.
3. Use `create_chart` to create visualizations when asked. Use the `ax` object for plotting. Do NOT call `plt.show()`.
4. Use `export_results` to save analysis results as CSV files when requested.

**Rules:**
- Always load the dataset before querying or charting.
- Write clean, efficient Pandas code.
- When creating charts, use vibrant colors like '#00d4ff', '#ff6b6b', '#00ff88', '#ffd700', '#ff69b4'.
- Explain your analysis results clearly after using tools.
- If a query fails, explain the error and try a different approach.
- For numeric analysis, round values to 2 decimal places.
- When grouping data, use meaningful aggregations (mean, sum, count as appropriate).
"""

# ---------------------------------------------------------------------------
# Function registry — maps tool names to implementations
# ---------------------------------------------------------------------------
AVAILABLE_FUNCTIONS = {
    "load_dataset": load_dataset,
    "run_query": run_query,
    "create_chart": create_chart,
    "export_results": export_results,
    "clean_data": clean_data,
}


# ---------------------------------------------------------------------------
# Core agent loop
# ---------------------------------------------------------------------------
def run_agent(user_message: str, messages: list | None = None, dataset_path: str | None = None) -> dict:
    """
    Run the agentic tool calling loop.

    Args:
        user_message: The user's natural language question.
        messages: Existing conversation history (list of message dicts).
                  If None, starts a fresh conversation.
        dataset_path: Optional path to auto-load a dataset.

    Returns:
        dict with keys:
            - "response": The final assistant text response
            - "messages": Updated conversation history
            - "charts": List of chart file paths generated
            - "exports": List of exported file paths
            - "tool_calls_log": List of tool calls made (for UI display)
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Initialize conversation
    if messages is None:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # If a dataset path is provided and it's the first load, inject context
    if dataset_path:
        context = f"\n[System: The user has uploaded a dataset at path '{dataset_path}'. Load it before answering questions about it.]"
        user_message_with_context = user_message + context
    else:
        user_message_with_context = user_message

    messages.append({"role": "user", "content": user_message_with_context})

    # Track artifacts generated
    charts = []
    exports = []
    tool_calls_log = []

    # ---------------------------------------------------------------------------
    # Agentic loop
    # ---------------------------------------------------------------------------
    iteration = 0
    while iteration < MAX_ITERATIONS:
        iteration += 1
        logger.debug("Agent loop iteration %d/%d", iteration, MAX_ITERATIONS)
        logger.debug("Agent loop iteration %d/%d", iteration, MAX_ITERATIONS)

        # Call Groq with tool schemas
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                max_tokens=4096,
            )
        except Exception as api_err:
            err_str = str(api_err)
            # Groq returns tool_use_failed when the LLM generates malformed tool JSON
            if "tool_use_failed" in err_str:
                logger.warning("Malformed tool call from LLM, asking for retry (iteration %d)", iteration)
                messages.append({
                    "role": "user",
                    "content": "[System: Your previous tool call was malformed. Please try again with valid arguments, or respond directly without using tools.]",
                })
                continue
            # Other API errors — return gracefully
            logger.error("Groq API error: %s", err_str)
            logger.error("Groq API error: %s", err_str)
            return {
                "response": f"API error: {err_str}",
                "messages": messages,
                "charts": charts,
                "exports": exports,
                "tool_calls_log": tool_calls_log,
            }

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # If no tool calls, we have our final response
        if not tool_calls:
            # Append the final assistant message
            messages.append({
                "role": "assistant",
                "content": response_message.content or ""
            })
            return {
                "response": response_message.content or "",
                "messages": messages,
                "charts": charts,
                "exports": exports,
                "tool_calls_log": tool_calls_log,
            }

        # Append assistant message with tool calls
        messages.append(response_message)

        # Execute each tool call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            try:
                function_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                function_args = {}

            logger.info("Calling tool '%s' with args: %s", function_name, function_args)

            logger.info("Calling tool '%s' with args: %s", function_name, function_args)

            # Log the tool call
            log_entry = {
                "tool": function_name,
                "args": function_args,
                "iteration": iteration,
            }

            # Execute the function
            if function_name in AVAILABLE_FUNCTIONS:
                function_to_call = AVAILABLE_FUNCTIONS[function_name]
                try:
                    function_response = function_to_call(**function_args)
                except TypeError as e:
                    function_response = json.dumps({"error": f"Invalid arguments: {str(e)}"})
                except Exception as e:
                    logger.exception("Tool '%s' raised an exception", function_name)
                    logger.exception("Tool '%s' raised an exception", function_name)
                    function_response = json.dumps({"error": f"Tool execution error: {str(e)}"})
            else:
                function_response = json.dumps({"error": f"Unknown tool: {function_name}"})

            log_entry["result"] = function_response
            tool_calls_log.append(log_entry)

            # Track generated artifacts
            try:
                result_data = json.loads(function_response)
                if "chart_path" in result_data:
                    charts.append(result_data["chart_path"])
                if "filepath" in result_data:
                    exports.append(result_data["filepath"])
            except (json.JSONDecodeError, TypeError):
                pass

            # Append tool result to messages
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })

    # If we hit max iterations, return what we have
    logger.warning("Agent hit MAX_ITERATIONS (%d) — returning partial results", MAX_ITERATIONS)
    final_msg = "I've reached the maximum number of analysis steps. Here's what I found so far."
    messages.append({"role": "assistant", "content": final_msg})
    return {
        "response": final_msg,
        "messages": messages,
        "charts": charts,
        "exports": exports,
        "tool_calls_log": tool_calls_log,
    }
