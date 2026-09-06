# DataMind

### Ask better questions of your data.

DataMind is a conversational data workspace that turns a CSV into an explorable analysis desk. Ask questions in plain language, inspect the dataset's structure, search raw records, prepare a clean working copy, and turn findings into a concise decision brief.

![DataMind workbench with file import, example datasets, and a retail sales preview](public/assets/user%20interface%20for%20readme.png)

## Why DataMind

Most "chat with your CSV" demos stop at a message box. DataMind treats analysis as a full workflow:

| Workspace | What it does |
| --- | --- |
| **Ask DataMind** | Runs conversational analysis with dataset-aware prompt starters, charts, execution traces, and inference telemetry. |
| **Overview** | Profiles rows, fields, numeric features, missing cells, duplicates, schema types, and column completeness. |
| **Records** | Provides full-dataset search, adjustable row views, sticky table navigation, and CSV export. |
| **Prepare** | Applies transparent in-memory cleaning recipes for duplicate and incomplete rows without touching the source file. |
| **Brief** | Generates and downloads an executive-ready Markdown readout. |

Three embedded benchmark datasets make the full product testable without setup: retail sales, SaaS churn, and clinical trials.

## Product highlights

- Natural-language analysis backed by Groq LPU models
- Dataset context sent with every analytical request
- AI-generated bar, line, scatter, pie, and box-compatible visual responses
- Self-correction visibility when an execution step needs repair
- Per-response latency, token, and throughput telemetry
- Automatic structural profiling and field-level completeness
- Instant full-record search and prepared CSV export
- Responsive workspace navigation for desktop and mobile
- Local API-key persistence in the browser
- Serverless Next.js API routes, ready for Vercel

## Architecture

```text
CSV / TSV upload
      |
      v
Papa Parse (client-side parsing + type inference)
      |
      +--------> Overview / Records / Prepare
      |
      v
Next.js API route
      |
      v
Groq tool-calling loop
      |
      +--------> analytical response
      +--------> chart specification
      +--------> execution trace
      +--------> inference telemetry
```

The browser owns the working dataset. Analysis requests send a bounded sample to the serverless API, where the selected Groq model can reason over the schema and invoke the supported analysis tools. Structured results return to the React workspace for rendering.

## Run locally

### 1. Install

```bash
git clone https://github.com/Abdullah-Zafarr/LLM-Data-Analyst-Groq.git
cd LLM-Data-Analyst-Groq
npm install
```

### 2. Configure

Create `.env.local`:

```bash
GROQ_API_KEY=gsk_your_key_here
```

You can also enter a Groq key directly in the workspace. The key is stored in browser local storage for that device.

### 3. Start

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Project structure

```text
src/
  app/
    api/
      chat/route.ts       # conversational analysis and tool loop
      report/route.ts     # executive brief generation
    globals.css           # complete responsive product design system
    layout.tsx            # metadata and root layout
    page.tsx              # five-view analysis workspace
  components/
    ChartRenderer.tsx     # dependency-free interactive SVG charts
sample_data/
  sales_data.csv
  saas_churn.csv
  clinical_trials.csv
```

## Production build

```bash
npm run build
npm start
```

## Data and key handling

- Uploaded files are parsed in the browser.
- The frontend caps the dataset payload sent for an analysis request.
- A key entered in the interface is stored only in browser local storage.
- For a public deployment, prefer a server-side `GROQ_API_KEY` environment variable.

## License

MIT License. See [LICENSE](LICENSE).
