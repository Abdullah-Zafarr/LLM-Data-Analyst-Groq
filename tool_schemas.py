"""
tool_schemas.py — Groq tool JSON schemas for DataMind AI.

Definitions for all callable tools exposed to Groq LLM tool calling.
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "load_dataset",
            "description": (
                "Load a CSV or Excel file into memory for analysis. "
                "Returns a detailed summary including columns, data types, row counts, "
                "missing values, and sample data. Call this first if no dataset is loaded."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Path to the CSV/Excel file, e.g. 'sample_data/sales_data.csv'",
                    }
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_query",
            "description": (
                "Execute Python/Pandas code in a sandboxed execution container. "
                "The DataFrame is available as 'df'. 'pd' and 'np' are pre-imported. "
                "Assign the primary result to variable 'result'.\n"
                "Examples:\n"
                "  result = df.groupby('Region')['Revenue'].sum().reset_index()\n"
                "  result = df[df['MonthlyCharges'] > 75].sort_values('TenureMonths', ascending=False)\n"
                "  result = df.describe()\n"
                "  result = df.corr(numeric_only=True)"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python Pandas code to execute. Always assign final output to 'result'.",
                    }
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_interactive_chart",
            "description": (
                "Generate a rich, interactive Plotly visualization with hover tooltips, zoom, and panning. "
                "The code MUST assign the Plotly figure to a variable named 'fig'. "
                "Plotly Express is available as 'px' and Graph Objects as 'go'. 'df' is the DataFrame.\n"
                "Examples:\n"
                "  fig = px.bar(df, x='Region', y='Revenue', color='Category', title='Revenue by Region', barmode='group')\n"
                "  fig = px.scatter(df, x='MonthlyCharges', y='TotalCharges', color='Churn', hover_data=['CustomerID'])\n"
                "  fig = px.pie(df, names='ContractType', values='MonthlyCharges', title='Revenue by Contract')"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code using 'px' or 'go' to create the figure. Must assign to 'fig'.",
                    },
                    "title": {
                        "type": "string",
                        "description": "Title for the interactive chart.",
                    },
                },
                "required": ["code", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_chart",
            "description": (
                "Generate a high-resolution static Matplotlib chart saved to disk as a PNG image. "
                "Use 'ax' for the pre-configured axes object and 'df' for the data. "
                "Do NOT call plt.show(). 'colors' list is available."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python Matplotlib code. Plot onto axes 'ax'. Do NOT call plt.show().",
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the chart.",
                    },
                    "palette": {
                        "type": "string",
                        "enum": ["vibrant", "corporate", "neon", "sunset"],
                        "description": "Color palette theme.",
                    },
                },
                "required": ["code", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "export_results",
            "description": "Export query results or filtered datasets to a CSV file for download.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "Python expression evaluating to a DataFrame or Series using 'df'.",
                    },
                    "filename": {
                        "type": "string",
                        "description": "Target CSV filename (e.g. 'high_risk_churn.csv').",
                    },
                },
                "required": ["data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "clean_data",
            "description": "Perform data transformation/cleaning operations on the active dataset.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["drop_na", "fill_na", "drop_cols", "rename_cols", "drop_duplicates", "filter_outliers"],
                        "description": "Cleaning transformation to apply.",
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of columns affected by this operation.",
                    },
                    "value": {
                        "type": "string",
                        "description": "Fill value or JSON mapping string for column renaming.",
                    },
                },
                "required": ["operation"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_data_profile",
            "description": "Compute an automated statistical health profile, distribution metrics, and correlations for the active dataset.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_executive_report",
            "description": "Generate a structured Executive Data Intelligence Report summarizing findings and strategic recommendations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Report title header.",
                    }
                },
            },
        },
    },
]
