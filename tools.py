"""
tools.py — Tool implementations for the Natural Language Data Analyst.

Each tool function returns a JSON string (Groq requirement).
Tools: load_dataset, run_query, create_chart, export_results
"""

import json
import os

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Global dataset store
# ---------------------------------------------------------------------------
_datasets: dict[str, pd.DataFrame] = {}


def get_dataset(name: str = "default") -> pd.DataFrame | None:
    """Retrieve a loaded dataset by name."""
    return _datasets.get(name)


def set_dataset(df: pd.DataFrame, name: str = "default") -> None:
    """Store a dataset in memory."""
    _datasets[name] = df


def clear_dataset(name: str = "default") -> None:
    """Remove a dataset from memory."""
    _datasets.pop(name, None)


# ---------------------------------------------------------------------------
# Shared sandbox namespace (used by run_query, create_chart, export_results)
# ---------------------------------------------------------------------------
def _sandbox(df: pd.DataFrame, **extras) -> tuple[dict, dict]:
    """Return (globals, locals) for sandboxed exec/eval."""
    safe_globals = {"__builtins__": {}}
    safe_locals = {
        "df": df.copy(),
        "pd": pd,
        "np": np,
        "len": len, "str": str, "int": int, "float": float,
        "list": list, "dict": dict, "tuple": tuple, "set": set,
        "bool": bool, "type": type,
        "round": round, "sorted": sorted,
        "min": min, "max": max, "sum": sum, "abs": abs,
        "enumerate": enumerate, "range": range, "zip": zip,
        "map": map, "filter": filter,
        "isinstance": isinstance, "hasattr": hasattr,
        "print": print,
        "True": True, "False": False, "None": None,
        **extras,
    }
    return safe_globals, safe_locals


# ---------------------------------------------------------------------------
# Tool 1: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(filename: str) -> str:
    """Load a CSV or Excel file into memory and return a summary."""
    try:
        if not os.path.exists(filename):
            return json.dumps({"error": f"File not found: {filename}"})

        ext = os.path.splitext(filename)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(filename)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(filename)
        else:
            return json.dumps({"error": f"Unsupported file type: {ext}. Use CSV or Excel."})

        set_dataset(df)

        summary = {
            "status": "success",
            "filename": os.path.basename(filename),
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample_rows": df.head(5).to_dict(orient="records"),
            "numeric_summary": {},
        }

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            stats = df[numeric_cols].describe().to_dict()
            summary["numeric_summary"] = {
                col: {k: round(float(v), 2) for k, v in col_stats.items()}
                for col, col_stats in stats.items()
            }

        return json.dumps(summary, default=str)

    except Exception as e:
        return json.dumps({"error": f"Failed to load dataset: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool 2: run_query
# ---------------------------------------------------------------------------
def run_query(code: str) -> str:
    """Execute a Pandas query on the loaded dataset. Code should assign to 'result'."""
    try:
        df = get_dataset()
        if df is None:
            return json.dumps({"error": "No dataset loaded. Use load_dataset first."})

        g, l = _sandbox(df)
        exec(code, g, l)

        if "result" not in l:
            return json.dumps({
                "status": "success",
                "result": "Code executed. Assign your result to 'result' to see output."
            })

        result = l["result"]
        if isinstance(result, (pd.DataFrame, pd.Series)):
            text = result.head(50).to_string() if len(result) > 50 else result.to_string()
            out = {"status": "success", "result": text}
            if isinstance(result, pd.DataFrame) and len(result) > 50:
                out["note"] = f"Showing first 50 of {len(result)} rows"
            return json.dumps(out)

        return json.dumps({"status": "success", "result": str(result)}, default=str)

    except Exception as e:
        return json.dumps({"error": f"Query execution failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool 3: create_chart
# ---------------------------------------------------------------------------
CHARTS_DIR = "charts"


def create_chart(code: str, title: str = "Chart") -> str:
    """Generate a Matplotlib chart and save as PNG."""
    try:
        df = get_dataset()
        if df is None:
            return json.dumps({"error": "No dataset loaded. Use load_dataset first."})

        os.makedirs(CHARTS_DIR, exist_ok=True)

        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(10, 6))

        g, l = _sandbox(df, plt=plt, fig=fig, ax=ax)
        exec(code, g, l)

        ax.set_title(title, fontsize=14, fontweight="bold", color="white", pad=15)
        fig.patch.set_facecolor("#0e1117")
        ax.set_facecolor("#0e1117")
        plt.tight_layout()

        safe_title = "".join(c if c.isalnum() or c in " _-" else "" for c in title)
        filepath = os.path.join(CHARTS_DIR, f"{safe_title.replace(' ', '_').lower()}.png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="#0e1117")
        plt.close(fig)

        return json.dumps({
            "status": "success",
            "chart_path": filepath,
            "title": title,
            "message": f"Chart saved to {filepath}",
        })

    except Exception as e:
        plt.close("all")
        return json.dumps({"error": f"Chart creation failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool 4: export_results
# ---------------------------------------------------------------------------
EXPORTS_DIR = "exports"


def export_results(data: str, filename: str = "export.csv") -> str:
    """Save query results to a CSV file."""
    try:
        df = get_dataset()
        if df is None:
            return json.dumps({"error": "No dataset loaded. Use load_dataset first."})

        os.makedirs(EXPORTS_DIR, exist_ok=True)
        filepath = os.path.join(EXPORTS_DIR, filename)

        g, l = _sandbox(df)
        try:
            result = eval(data, g, l)
            if isinstance(result, pd.DataFrame):
                result.to_csv(filepath, index=False)
            elif isinstance(result, pd.Series):
                result.to_csv(filepath)
            else:
                with open(filepath, "w") as f:
                    f.write(str(result))
        except (SyntaxError, NameError, TypeError, ValueError):
            with open(filepath, "w") as f:
                f.write(data)

        return json.dumps({
            "status": "success",
            "filepath": filepath,
            "message": f"Results exported to {filepath}",
        })

    except Exception as e:
        return json.dumps({"error": f"Export failed: {str(e)}"})
