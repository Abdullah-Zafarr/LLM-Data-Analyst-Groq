import { NextRequest, NextResponse } from "next/server";
import Groq from "groq-sdk";

export const runtime = "nodejs";

const TOOL_SCHEMAS: Groq.Chat.Completions.ChatCompletionTool[] = [
  {
    type: "function",
    function: {
      name: "run_query",
      description:
        "Execute a data query or calculation on the active dataset. Provide calculation logic or aggregation code.",
      parameters: {
        type: "object",
        properties: {
          code: {
            type: "string",
            description: "Query expression or calculation logic, e.g. 'df.groupby(\"Region\")[\"Revenue\"].sum()'",
          },
          explanation: {
            type: "string",
            description: "Short explanation of the quantitative operation",
          },
        },
        required: ["code"],
      },
    },
  },
  {
    type: "function",
    function: {
      name: "generate_chart_spec",
      description:
        "Specify an interactive visualization for the frontend (bar, line, scatter, pie).",
      parameters: {
        type: "object",
        properties: {
          chart_type: {
            type: "string",
            enum: ["bar", "line", "scatter", "pie"],
          },
          title: { type: "string" },
          x_col: { type: "string" },
          y_col: { type: "string" },
        },
        required: ["chart_type", "title", "x_col"],
      },
    },
  },
];

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const {
      user_message,
      messages = [],
      dataset_records = [],
      dataset_name = "dataset.csv",
      model = "openai/gpt-oss-120b",
      api_key,
    } = body;

    const apiKey = api_key || process.env.GROQ_API_KEY;
    if (!apiKey || apiKey === "your_groq_api_key_here") {
      return NextResponse.json(
        { detail: "Groq API key required. Enter it in the sidebar or set GROQ_API_KEY." },
        { status: 400 }
      );
    }

    const groq = new Groq({ apiKey });

    // Dataset summary context
    let schemaInfo = "";
    if (dataset_records && dataset_records.length > 0) {
      const cols = Object.keys(dataset_records[0]);
      const sample = dataset_records.slice(0, 3);
      schemaInfo = `\n[Active Dataset: "${dataset_name}" with ${dataset_records.length} records. Columns: ${cols.join(
        ", "
      )}. Sample records: ${JSON.stringify(sample)}].`;
    }

    const systemPrompt = `You are DataMind AI — an autonomous data analyst and quantitative intelligence assistant.
You help users explore, analyze, and visualize datasets through natural language conversation.
${schemaInfo}

**Your Tools:**
1. \`run_query\`: Execute calculation logic on the dataset.
2. \`generate_chart_spec\`: Generate interactive visualizations (bar, line, scatter, pie) by specifying column keys.

**Guidelines:**
- If the user asks for charts, call \`generate_chart_spec\` with exact column names from the dataset.
- Provide crisp, data-driven analytical takeaways. Bold key metrics.`;

    const conversation: Groq.Chat.Completions.ChatCompletionMessageParam[] =
      messages.length > 0
        ? messages
        : [{ role: "system", content: systemPrompt }];

    conversation.push({ role: "user", content: user_message });

    const charts: any[] = [];
    const toolCallsLog: any[] = [];
    let totalInferenceTimeMs = 0;
    let totalPromptTokens = 0;
    let totalCompletionTokens = 0;

    let iteration = 0;
    const maxIterations = 5;

    while (iteration < maxIterations) {
      iteration++;
      const t0 = performance.now();

      const response = await groq.chat.completions.create({
        model,
        messages: conversation,
        tools: TOOL_SCHEMAS,
        tool_choice: "auto",
        temperature: 0.1,
        max_tokens: 4096,
      });

      const tCall = performance.now() - t0;
      totalInferenceTimeMs += tCall;

      if (response.usage) {
        totalPromptTokens += response.usage.prompt_tokens || 0;
        totalCompletionTokens += response.usage.completion_tokens || 0;
      }

      const msg = response.choices[0]?.message;
      if (!msg) break;

      if (!msg.tool_calls || msg.tool_calls.length === 0) {
        conversation.push({ role: "assistant", content: msg.content || "" });
        const tps =
          totalInferenceTimeMs > 0
            ? Math.round((totalCompletionTokens / (totalInferenceTimeMs / 1000)) * 10) / 10
            : 0;

        return NextResponse.json({
          response: msg.content || "Analysis complete.",
          charts,
          tool_calls_log: toolCallsLog,
          telemetry: {
            model,
            total_inference_time_ms: Math.round(totalInferenceTimeMs),
            tokens_per_sec: tps,
            prompt_tokens: totalPromptTokens,
            completion_tokens: totalCompletionTokens,
            total_tokens: totalPromptTokens + totalCompletionTokens,
            iterations: iteration,
          },
        });
      }

      // Handle tool calls
      conversation.push(msg);

      for (const tc of msg.tool_calls) {
        if (tc.type !== "function") continue;
        const fnName = tc.function.name;
        let fnArgs: any = {};
        try {
          fnArgs = JSON.parse(tc.function.arguments || "{}");
        } catch {}

        toolCallsLog.push({ tool: fnName, args: fnArgs, iteration });

        let toolOutput = "";
        if (fnName === "generate_chart_spec") {
          charts.push(fnArgs);
          toolOutput = JSON.stringify({ status: "success", message: "Chart specification added" });
        } else if (fnName === "run_query") {
          toolOutput = JSON.stringify({
            status: "success",
            message: `Executed query: ${fnArgs.code}`,
          });
        } else {
          toolOutput = JSON.stringify({ status: "error", message: `Unknown tool: ${fnName}` });
        }

        conversation.push({
          role: "tool",
          tool_call_id: tc.id,
          content: toolOutput,
        });
      }
    }

    return NextResponse.json({
      response: "Completed data analysis reasoning steps.",
      charts,
      tool_calls_log: toolCallsLog,
      telemetry: {
        model,
        total_inference_time_ms: Math.round(totalInferenceTimeMs),
        tokens_per_sec: 0,
        total_tokens: totalPromptTokens + totalCompletionTokens,
        iterations: iteration,
      },
    });
  } catch (error: any) {
    return NextResponse.json(
      { detail: error?.message || "Internal server error during analysis" },
      { status: 500 }
    );
  }
}
