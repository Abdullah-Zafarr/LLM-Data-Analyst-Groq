"""
tool_schemas.py — Groq tool JSON schemas for the Natural Language Data Analyst.

These schemas tell the LLM what tools are available, what they do,
and what parameters they accept. The model uses these to decide
which tools to call and with what arguments.
"""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "load_dataset",
            "description": (
                "Load a CSV or Excel file into memory for analysis. "
                "Returns a summary including column names, data types, shape, "
                "and the first 5 rows of data. Always call this first before "
                "running queries or creating charts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": (
                            "The file path of the CSV or Excel file to load. "
                            "Example: 'sample_data/sales_data.csv'"
                        ),
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
                "Execute a Pandas query or operation on the loaded dataset. "
                "The code should reference the DataFrame as 'df'. "
                "You MUST assign the final result to a variable named 'result'. "
                "Examples:\n"
                "  result = df.groupby('Region')['Revenue'].mean()\n"
                "  result = df[df['Revenue'] > 1000]\n"
                "  result = df.describe()\n"
                "  result = df['Revenue'].sum()\n"
                "  result = df.corr(numeric_only=True)"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": (
                            "Python code using Pandas to query the dataset. "
                            "The DataFrame is available as 'df'. "
                            "pandas is available as 'pd' and numpy as 'np'. "
                            "Always assign the final answer to 'result'."
                        ),
                    }
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_chart",
            "description": (
                "Generate a Matplotlib chart from the loaded dataset and save it as a PNG image. "
                "The code should reference the DataFrame as 'df' and use 'ax' for plotting "
                "(a pre-configured matplotlib axes object). "
                "Do NOT call plt.show(). The chart will be saved automatically. "
                "Examples:\n"
                "  df.groupby('Region')['Revenue'].mean().plot(kind='bar', ax=ax, color='#00d4ff')\n"
                "  ax.scatter(df['Units'], df['Revenue'], color='#ff6b6b', alpha=0.7)\n"
                "  df['Category'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": (
                            "Python code using matplotlib to create the chart. "
                            "Use 'ax' for the axes object and 'df' for the data. "
                            "'plt', 'pd', and 'np' are also available. "
                            "Do NOT call plt.show()."
                        ),
                    },
                    "title": {
                        "type": "string",
                        "description": "The title for the chart.",
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
            "description": (
                "Export query results or a filtered dataset to a CSV file for download. "
                "The 'data' parameter should be a valid Python expression that uses 'df' "
                "(the loaded DataFrame). "
                "Examples:\n"
                "  df.groupby('Region')['Revenue'].sum().reset_index()\n"
                "  df[df['Revenue'] > 5000]\n"
                "  df.describe()"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": (
                            "A Python expression that evaluates to a DataFrame or Series "
                            "using the loaded dataset 'df'. "
                            "Example: \"df.groupby('Region')['Revenue'].mean().reset_index()\""
                        ),
                    },
                    "filename": {
                        "type": "string",
                        "description": (
                            "The output filename for the exported CSV. "
                            "Default: 'export.csv'. Example: 'revenue_by_region.csv'"
                        ),
                    },
                },
                "required": ["data"],
            },
        },
    },
]
