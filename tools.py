"""
tools.py — Sandboxed execution tools and analytical engines for DataMind AI.

Supports:
1. load_dataset (CSV, TSV, Excel with intelligent sampling & schema profiling)
2. run_query (Sandboxed Pandas REPL execution with timing and error introspection)
3. create_chart (High-res Matplotlib dark-theme exportable chart)
4. create_interactive_chart (Plotly interactive charts with hover tooltips and responsive themes)
5. export_results (CSV and JSON data export)
6. clean_data (Data cleaning transforms: drop_na, fill_na, drop_cols, rename_cols, drop_duplicates, filter_outliers)
7. get_data_profile (Comprehensive automated statistical dataset health profile)
8. generate_executive_report (Automated analytical executive summary)
"""

import json
import os
import time
import traceback
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

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
# Shared sandbox namespace
# ---------------------------------------------------------------------------
def _sandbox(df: pd.DataFrame, **extras) -> tuple[dict, dict]:
    """Return (globals, locals) for sandboxed execution."""
    safe_globals = {"__builtins__": {}}
    safe_locals = {
        "df": df.copy(),
        "pd": pd,
        "np": np,
        "px": px,
        "go": go,
        "len": len, "str": str, "int": int, "float": float,
        "list": list, "dict": dict, "tuple": tuple, "set": set,
        "bool": bool, "type": type,
        "round": round, "sorted": sorted,
        "min": min, "max": max, "sum": sum, "abs": abs,
        "enumerate": enumerate, "range": range, "zip": zip,
        "map": map, "filter": filter,
        "isinstance": isinstance, "hasattr": hasattr, "getattr": getattr,
        "repr": repr, "any": any, "all": all, "reversed": reversed,
        "print": print,
        "True": True, "False": False, "None": None,
        **extras,
    }
    return safe_globals, safe_locals


# ---------------------------------------------------------------------------
# Tool 1: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(filename: str) -> str:
    """Load CSV or Excel file into memory and return a structured summary."""
    t0 = time.perf_counter()
    try:
        if not os.path.exists(filename):
            return json.dumps({"status": "error", "error": f"File not found: {filename}"})

        ext = os.path.splitext(filename)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(filename)
        elif ext == ".tsv":
            df = pd.read_csv(filename, sep="\t")
        elif ext in (".xlsx", ".xls", ".xlsb"):
            df = pd.read_excel(filename)
        else:
            return json.dumps({
                "status": "error",
                "error": f"Unsupported file type: {ext}. Supported: CSV, TSV, XLSX, XLS, XLSB."
            })

        is_sampled = False
        original_row_count = len(df)
        if original_row_count > 50000:
            df = df.sample(n=50000, random_state=42)
            is_sampled = True

        set_dataset(df)

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        summary = {
            "status": "success",
            "filename": os.path.basename(filename),
            "execution_time_ms": elapsed_ms,
            "is_sampled": is_sampled,
            "original_row_count": original_row_count,
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "null_counts": {col: int(count) for col, count in df.isnull().sum().items() if count > 0},
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            "sample_rows": df.head(5).to_dict(orient="records"),
            "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=["object", "category"]).columns.tolist(),
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
        return json.dumps({"status": "error", "error": f"Failed to load dataset: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool 2: run_query
# ---------------------------------------------------------------------------
def run_query(code: str) -> str:
    """Execute a Pandas query in a sandboxed REPL. Assign result to 'result'."""
    t0 = time.perf_counter()
    try:
        df = get_dataset()
        if df is None:
            return json.dumps({"status": "error", "error": "No dataset loaded. Use load_dataset first."})

        g, l = _sandbox(df)
        exec(code, g, l)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

        if "result" not in l:
            return json.dumps({
                "status": "success",
                "execution_time_ms": elapsed_ms,
                "result": "Code executed successfully. Note: Assign to 'result' to display output."
            })

        result = l["result"]
        if isinstance(result, pd.DataFrame):
            out = {
                "status": "success",
                "execution_time_ms": elapsed_ms,
                "shape": list(result.shape),
                "columns": list(result.columns),
                "data": result.head(30).to_dict(orient="records"),
                "result_type": "dataframe",
            }
            if len(result) > 30:
                out["note"] = f"Showing first 30 of {len(result)} rows"
            return json.dumps(out, default=str)

        elif isinstance(result, pd.Series):
            return json.dumps({
                "status": "success",
                "execution_time_ms": elapsed_ms,
                "result": result.head(30).to_dict(),
                "result_type": "series",
            }, default=str)

        return json.dumps({
            "status": "success",
            "execution_time_ms": elapsed_ms,
            "result": str(result),
            "result_type": "scalar",
        }, default=str)

    except Exception as e:
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        tb = traceback.format_exc()
        return json.dumps({
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "execution_time_ms": elapsed_ms,
            "traceback": tb,
            "code": code,
        })


# ---------------------------------------------------------------------------
# Tool 3: create_interactive_chart (Plotly)
# ---------------------------------------------------------------------------
def create_interactive_chart(code: str, title: str = "Interactive Visual") -> str:
    """
    Generate an interactive Plotly chart.
    Code should create a plotly figure and assign to 'fig'.
    Example:
      fig = px.bar(df, x='Region', y='Revenue', color='Category', title='Revenue by Region')
    """
    t0 = time.perf_counter()
    try:
        df = get_dataset()
        if df is None:
            return json.dumps({"status": "error", "error": "No dataset loaded. Use load_dataset first."})

        g, l = _sandbox(df)
        exec(code, g, l)

        if "fig" not in l or not isinstance(l["fig"], (go.Figure)):
            return json.dumps({
                "status": "error",
                "error": "The code must create a Plotly figure and assign it to a variable named 'fig'."
            })

        fig = l["fig"]
        # Apply dark cosmic mission control aesthetic
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#090D16",
            plot_bgcolor="#0D1322",
            font=dict(family="Fira Code, monospace", color="#E2E8F0"),
            title=dict(text=title, font=dict(size=16, color="#38BDF8")),
            margin=dict(l=40, r=40, t=60, b=40),
            colorway=["#06B6D4", "#6366F1", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6"],
        )

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return json.dumps({
            "status": "success",
            "chart_type": "plotly",
            "title": title,
            "figure_json": fig.to_json(),
            "execution_time_ms": elapsed_ms,
        })

    except Exception as e:
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return json.dumps({
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "execution_time_ms": elapsed_ms,
            "code": code,
        })


# ---------------------------------------------------------------------------
# Tool 4: create_chart (Matplotlib publication export)
# ---------------------------------------------------------------------------
CHARTS_DIR = "charts"


def create_chart(code: str, title: str = "Chart", palette: str = "vibrant") -> str:
    """Generate a high-res Matplotlib chart and save it as a PNG image."""
    t0 = time.perf_counter()
    try:
        df = get_dataset()
        if df is None:
            return json.dumps({"status": "error", "error": "No dataset loaded. Use load_dataset first."})

        os.makedirs(CHARTS_DIR, exist_ok=True)

        palettes = {
            "vibrant": ['#06B6D4', '#EC4899', '#10B981', '#F59E0B', '#6366F1'],
            "corporate": ['#1E3A8A', '#3B82F6', '#94A3B8', '#1D4ED8', '#0F172A'],
            "neon": ['#00F5D4', '#7B2CBF', '#F72585', '#4CC9F0', '#FFB703'],
            "sunset": ['#FF4E50', '#FC913A', '#F9D423', '#EDE574', '#E1F5C4'],
        }
        colors = palettes.get(palette, palettes["vibrant"])

        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)

        g, l = _sandbox(df, plt=plt, fig=fig, ax=ax, colors=colors)
        exec(code, g, l)

        ax.set_title(title, fontsize=13, fontweight="bold", color="#38BDF8", pad=12)
        fig.patch.set_facecolor("#090D16")
        ax.set_facecolor("#0D1322")
        ax.grid(True, linestyle="--", alpha=0.15, color="#64748B")
        for spine in ax.spines.values():
            spine.set_edgecolor("rgba(255,255,255,0.1)")

        plt.tight_layout()

        safe_title = "".join(c if c.isalnum() or c in " _-" else "" for c in title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(CHARTS_DIR, f"{timestamp}_{safe_title.replace(' ', '_').lower()}.png")
        fig.savefig(filepath, dpi=180, bbox_inches="tight", facecolor="#090D16")
        plt.close(fig)

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return json.dumps({
            "status": "success",
            "chart_type": "matplotlib",
            "chart_path": filepath,
            "title": title,
            "execution_time_ms": elapsed_ms,
            "message": f"High-res chart saved to {filepath}",
        })

    except Exception as e:
        plt.close("all")
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return json.dumps({
            "status": "error",
            "error": f"Chart creation failed: {str(e)}",
            "error_type": type(e).__name__,
            "execution_time_ms": elapsed_ms,
            "code": code,
        })


# ---------------------------------------------------------------------------
# Tool 5: export_results
# ---------------------------------------------------------------------------
EXPORTS_DIR = "exports"


def export_results(data: str, filename: str = "export.csv") -> str:
    """Save query results to a CSV file."""
    t0 = time.perf_counter()
    try:
        df = get_dataset()
        if df is None:
            return json.dumps({"status": "error", "error": "No dataset loaded. Use load_dataset first."})

        os.makedirs(EXPORTS_DIR, exist_ok=True)
        if not filename.endswith(".csv"):
            filename += ".csv"
        filepath = os.path.join(EXPORTS_DIR, filename)

        g, l = _sandbox(df)
        rows_exported = 0
        try:
            result = eval(data, g, l)
            if isinstance(result, pd.DataFrame):
                result.to_csv(filepath, index=False)
                rows_exported = len(result)
            elif isinstance(result, pd.Series):
                result.to_csv(filepath)
                rows_exported = len(result)
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(str(result))
                rows_exported = 1
        except Exception:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(data)
            rows_exported = 1

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        return json.dumps({
            "status": "success",
            "filepath": filepath,
            "rows_exported": rows_exported,
            "execution_time_ms": elapsed_ms,
            "message": f"Successfully exported {rows_exported} rows to {filepath}",
        })

    except Exception as e:
        return json.dumps({"status": "error", "error": f"Export failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool 6: clean_data
# ---------------------------------------------------------------------------
def clean_data(operation: str, columns: list | None = None, value: str | None = None) -> str:
    """
    Perform dataset transformation / cleaning:
    Operations: 'drop_na', 'fill_na', 'drop_cols', 'rename_cols', 'drop_duplicates', 'filter_outliers'
    """
    t0 = time.perf_counter()
    try:
        df = get_dataset()
        if df is None:
            return json.dumps({"status": "error", "error": "No dataset loaded. Use load_dataset first."})

        original_rows = len(df)
        original_cols = len(df.columns)

        if operation == "drop_na":
            df = df.dropna(subset=columns) if columns else df.dropna()

        elif operation == "fill_na":
            if columns:
                for col in columns:
                    if col in df.columns:
                        if value == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                            df[col] = df[col].fillna(df[col].mean())
                        elif value == "median" and pd.api.types.is_numeric_dtype(df[col]):
                            df[col] = df[col].fillna(df[col].median())
                        elif value == "mode":
                            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "")
                        else:
                            df[col] = df[col].fillna(value if value is not None else "Unknown")
            else:
                df = df.fillna(value if value is not None else 0)

        elif operation == "drop_cols":
            if columns:
                df = df.drop(columns=[c for c in columns if c in df.columns])

        elif operation == "rename_cols":
            if value and isinstance(value, str):
                try:
                    rename_dict = json.loads(value.replace("'", '"'))
                    df = df.rename(columns=rename_dict)
                except Exception:
                    return json.dumps({"status": "error", "error": "For rename_cols, 'value' must be a valid JSON dictionary string."})

        elif operation == "drop_duplicates":
            df = df.drop_duplicates(subset=columns if columns else None)

        elif operation == "filter_outliers":
            # Remove rows where numeric column is > 3 standard deviations from mean
            cols_to_check = columns if columns else df.select_dtypes(include=[np.number]).columns.tolist()
            for col in cols_to_check:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    col_mean = df[col].mean()
                    col_std = df[col].std()
                    if col_std > 0:
                        df = df[(df[col] >= col_mean - 3 * col_std) & (df[col] <= col_mean + 3 * col_std)]

        else:
            return json.dumps({"status": "error", "error": f"Unknown operation: {operation}"})

        set_dataset(df)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

        return json.dumps({
            "status": "success",
            "operation": operation,
            "execution_time_ms": elapsed_ms,
            "changes": {
                "rows_removed": original_rows - len(df),
                "cols_removed": original_cols - len(df.columns),
                "new_shape": {"rows": len(df), "columns": len(df.columns)},
            },
            "message": f"Applied cleaning transformation '{operation}'. New shape: {df.shape[0]} rows, {df.shape[1]} columns.",
        })

    except Exception as e:
        return json.dumps({"status": "error", "error": f"Data cleaning failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool 7: get_data_profile
# ---------------------------------------------------------------------------
def get_data_profile() -> str:
    """Generate an automated statistical health profile of the current dataset."""
    t0 = time.perf_counter()
    try:
        df = get_dataset()
        if df is None:
            return json.dumps({"status": "error", "error": "No dataset loaded. Use load_dataset first."})

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        # Correlation matrix
        corr_data = {}
        if len(numeric_cols) >= 2:
            corr_df = df[numeric_cols].corr().round(3)
            corr_data = corr_df.to_dict()

        # Skewness & distribution metrics
        dist_metrics = {}
        for col in numeric_cols:
            dist_metrics[col] = {
                "mean": round(float(df[col].mean()), 2),
                "median": round(float(df[col].median()), 2),
                "std": round(float(df[col].std()), 2),
                "min": round(float(df[col].min()), 2),
                "max": round(float(df[col].max()), 2),
                "skew": round(float(df[col].skew()), 2) if not df[col].isnull().all() else 0.0,
            }

        profile = {
            "status": "success",
            "execution_time_ms": round((time.perf_counter() - t0) * 1000, 2),
            "rows": len(df),
            "columns": len(df.columns),
            "duplicate_rows": int(df.duplicated().sum()),
            "missing_cells_pct": round((df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100, 2),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "distribution_metrics": dist_metrics,
            "correlations": corr_data,
        }

        return json.dumps(profile, default=str)

    except Exception as e:
        return json.dumps({"status": "error", "error": f"Failed to generate profile: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool 8: generate_executive_report
# ---------------------------------------------------------------------------
def generate_executive_report(title: str = "Executive Data Intelligence Report") -> str:
    """Generate an executive analysis report summarizing key findings and anomalies."""
    try:
        df = get_dataset()
        if df is None:
            return json.dumps({"status": "error", "error": "No dataset loaded. Use load_dataset first."})

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        now = datetime.now().strftime("%B %d, %Y - %H:%M")
        lines = [
            f"# {title}",
            f"> **Generated by DataMind AI** · {now}\n",
            "## 1. Dataset Health & Architecture",
            f"- **Volume:** {len(df):,} rows × {len(df.columns)} dimensions",
            f"- **Completeness:** {100 - round((df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100, 2):.1f}% complete",
            f"- **Duplicate Records:** {int(df.duplicated().sum())} ({round(df.duplicated().sum() / len(df) * 100, 2)}%)\n",
            "## 2. Key Statistical Indicators",
        ]

        for col in numeric_cols[:5]:
            lines.append(f"- **`{col}`**: Mean = {df[col].mean():.2f} | Median = {df[col].median():.2f} | Std Dev = {df[col].std():.2f} | Range = [{df[col].min():.2f}, {df[col].max():.2f}]")

        if categorical_cols:
            lines.append("\n## 3. High-Frequency Categorical Segments")
            for col in categorical_cols[:3]:
                top_val = df[col].mode()[0] if not df[col].mode().empty else "N/A"
                uniq = df[col].nunique()
                lines.append(f"- **`{col}`**: {uniq} unique categories (Dominant segment: **{top_val}**)")

        lines.extend([
            "\n## 4. Strategic Recommendations",
            "- Prioritize automated data validation pipelines to eliminate remaining null values.",
            "- Investigate outliers identified in top numeric features to detect anomalies or high-value opportunities.",
            "- Implement continuous telemetry monitoring for automated drift detection."
        ])

        report_md = "\n".join(lines)
        return json.dumps({"status": "success", "report_markdown": report_md})

    except Exception as e:
        return json.dumps({"status": "error", "error": f"Report generation failed: {str(e)}"})
