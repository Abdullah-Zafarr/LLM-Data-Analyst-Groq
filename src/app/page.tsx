"use client";

import React, { useState, useEffect, useMemo } from "react";
import Papa from "papaparse";
import {
  Sparkles,
  Database,
  BarChart3,
  Search,
  Wrench,
  FileText,
  Zap,
  Terminal,
  Download,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  Upload,
  ArrowRight,
  RefreshCw,
  Copy,
  Layers,
} from "lucide-react";
import ChartRenderer from "@/components/ChartRenderer";

// Default Sample Datasets embedded for zero-latency instant loading
const SAMPLE_SALES_CSV = `OrderDate,Region,Product,Category,Units,UnitPrice,Revenue,Discount,Profit,PaymentMethod
2024-01-05,East,Widget Pro,Hardware,45,29.99,1349.55,0.05,404.87,Credit Card
2024-01-08,West,DataSync Enterprise,Software,12,249.99,2999.88,0.10,1499.94,Wire Transfer
2024-01-12,Central,CloudBackup Annual,Software,30,89.99,2699.70,0.00,1079.88,Credit Card
2024-01-15,South,SmartSensor X,IoT,80,15.50,1240.00,0.15,310.00,Credit Card
2024-01-18,East,Widget Pro,Hardware,60,29.99,1799.40,0.00,539.82,Credit Card
2024-01-22,West,CyberShield,Software,8,499.99,3999.92,0.05,2399.95,Wire Transfer
2024-01-25,Central,SmartSensor X,IoT,110,15.50,1705.00,0.20,341.00,PayPal
2024-01-28,South,Widget Basic,Hardware,150,9.99,1498.50,0.00,299.70,Credit Card
2024-02-02,East,CloudBackup Annual,Software,25,89.99,2249.75,0.10,899.90,Credit Card
2024-02-06,West,Widget Pro,Hardware,70,29.99,2099.30,0.05,629.79,Credit Card
2024-02-10,Central,CyberShield,Software,5,499.99,2499.95,0.00,1499.97,Wire Transfer
2024-02-14,South,DataSync Enterprise,Software,15,249.99,3749.85,0.15,1874.93,Wire Transfer
2024-02-18,East,SmartSensor X,IoT,95,15.50,1472.50,0.00,368.13,PayPal
2024-02-22,West,Widget Basic,Hardware,200,9.99,1998.00,0.10,399.60,Credit Card
2024-02-26,Central,CloudBackup Annual,Software,40,89.99,3599.60,0.05,1439.84,Credit Card`;

const SAMPLE_CHURN_CSV = `CustomerID,TenureMonths,ContractType,MonthlyCharges,TotalCharges,SupportTickets,PaymentMethod,NPS_Score,Churn
CUST-1001,1,Month-to-Month,78.50,78.50,4,Electronic Check,3,Yes
CUST-1002,34,One Year,56.95,1936.30,1,Mailed Check,8,No
CUST-1003,2,Month-to-Month,53.85,107.70,3,Mailed Check,4,Yes
CUST-1004,45,One Year,42.30,1903.50,0,Bank Transfer,9,No
CUST-1005,8,Month-to-Month,70.70,565.60,5,Electronic Check,2,Yes
CUST-1006,22,Month-to-Month,89.10,1960.20,2,Credit Card,6,Yes
CUST-1007,60,Two Year,105.65,6339.00,0,Bank Transfer,10,No
CUST-1008,12,Month-to-Month,20.75,249.00,1,Mailed Check,7,No
CUST-1009,30,One Year,64.80,1944.00,1,Bank Transfer,8,No
CUST-1010,4,Month-to-Month,95.45,381.80,6,Electronic Check,1,Yes
CUST-1011,58,Two Year,24.95,1447.10,0,Credit Card,9,No
CUST-1012,16,Month-to-Month,74.40,1190.40,2,Credit Card,5,No
CUST-1013,64,Two Year,111.30,7123.20,1,Bank Transfer,9,No
CUST-1014,3,Month-to-Month,80.85,242.55,4,Electronic Check,3,Yes
CUST-1015,38,One Year,69.90,2656.20,0,Credit Card,8,No`;

const SAMPLE_CLINICAL_CSV = `PatientID,Age,Gender,Cohort,BiomarkerBaseline,BiomarkerPostTreatment,AdverseEvents,RecoveryDays,EfficacyScore,Status
PT-201,45,Female,Treatment A,182.4,94.2,0,14,92.5,Resolved
PT-202,62,Male,Treatment A,210.8,112.5,1,19,84.0,Resolved
PT-203,54,Female,Control,175.1,168.9,0,38,32.4,Active
PT-204,39,Male,Treatment B,198.3,88.7,0,12,95.1,Resolved
PT-205,71,Female,Control,245.0,239.2,2,45,18.9,Active
PT-206,58,Male,Treatment A,189.6,98.1,0,16,89.3,Resolved
PT-207,49,Female,Treatment B,204.2,91.0,1,15,91.8,Resolved
PT-208,67,Male,Control,220.5,214.0,1,42,24.6,Active
PT-209,42,Female,Treatment A,168.9,82.4,0,11,96.2,Resolved
PT-210,51,Male,Treatment B,195.0,85.6,0,13,94.0,Resolved
PT-211,63,Female,Control,231.4,228.1,3,50,15.2,Active
PT-212,38,Male,Treatment A,177.2,89.3,0,12,93.7,Resolved
PT-213,74,Female,Treatment B,250.6,120.4,2,22,81.5,Resolved
PT-214,56,Male,Control,192.8,188.5,1,36,29.0,Active
PT-215,48,Female,Treatment A,184.1,92.0,0,14,91.4,Resolved`;

interface Message {
  role: "user" | "assistant";
  content: string;
  charts?: any[];
  telemetry?: Record<string, any>;
  toolCalls?: any[];
  selfCorrections?: any[];
}

export default function MissionControl() {
  const [activeTab, setActiveTab] = useState<"copilot" | "eda" | "explorer" | "clean" | "report">("copilot");
  const [records, setRecords] = useState<Record<string, any>[]>([]);
  const [datasetName, setDatasetName] = useState<string | null>(null);
  const [model, setModel] = useState("llama-3.3-70b-versatile");
  const [apiKey, setApiKey] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [telemetry, setTelemetry] = useState<Record<string, any>>({
    total_inference_time_ms: 0,
    tokens_per_sec: 0,
  });

  // Table Search and Pagination
  const [searchFilter, setSearchFilter] = useState("");
  const [rowLimit, setRowLimit] = useState(25);

  // Executive Report State
  const [reportMarkdown, setReportMarkdown] = useState<string | null>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  // Load API key from localStorage
  useEffect(() => {
    const savedKey = localStorage.getItem("datamind_groq_key");
    if (savedKey) setApiKey(savedKey);
  }, []);

  const handleApiKeyChange = (val: string) => {
    setApiKey(val);
    localStorage.setItem("datamind_groq_key", val);
  };

  // Helper: parse CSV into records
  const parseAndLoadCsv = (csvString: string, name: string) => {
    Papa.parse(csvString, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results) => {
        setRecords(results.data as Record<string, any>[]);
        setDatasetName(name);
        setReportMarkdown(null);
      },
    });
  };

  // Upload Custom CSV
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      if (text) parseAndLoadCsv(text, file.name);
    };
    reader.readAsText(file);
  };

  // Dynamic Suggestion Chips
  const suggestions = useMemo(() => {
    if (!datasetName) return [];
    if (datasetName.includes("sales")) {
      return [
        "Revenue and profit breakdown grouped by Region",
        "Create a bar chart of Revenue by Product",
        "Calculate correlation between Units and Revenue",
        "Detect revenue outliers using IQR and list top rows",
      ];
    }
    if (datasetName.includes("churn")) {
      return [
        "Calculate churn rate across ContractType segments",
        "Plot scatter of MonthlyCharges vs TotalCharges by Churn",
        "Compare average NPS score and SupportTickets by Churn",
        "Identify top 5 highest paying customers with Churn Yes",
      ];
    }
    if (datasetName.includes("clinical")) {
      return [
        "Compare Biomarker improvement across Cohorts",
        "Plot a chart of RecoveryDays by Cohort",
        "Find correlation between Age and EfficacyScore",
        "Summarize AdverseEvents and recovery status",
      ];
    }
    const cols = records.length > 0 ? Object.keys(records[0]) : [];
    return [
      `Summarize key statistics for ${cols.slice(0, 3).join(", ")}`,
      `Find distributions and missing values in this dataset`,
      `Detect statistical outliers across primary numeric features`,
    ];
  }, [datasetName, records]);

  // Execute Agent Chat
  const runChatQuery = async (queryText: string) => {
    if (!queryText.trim() || isLoading) return;

    const userMsg: Message = { role: "user", content: queryText };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setIsLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_message: queryText,
          dataset_records: records.length > 0 ? records.slice(0, 300) : null,
          dataset_name: datasetName || "dataset.csv",
          model,
          api_key: apiKey || undefined,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to process chat query");
      }

      const data = await res.json();
      setTelemetry(data.telemetry || {});

      const assistantMsg: Message = {
        role: "assistant",
        content: data.response,
        charts: data.charts || [],
        telemetry: data.telemetry || {},
        toolCalls: data.tool_calls_log || [],
        selfCorrections: data.telemetry?.self_corrections || [],
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `⚠️ Error: ${err.message || "Failed to communicate with Groq LPU engine. Check API key."}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Filtered Records for Data Grid
  const filteredRecords = useMemo(() => {
    if (!searchFilter) return records;
    return records.filter((r) =>
      Object.values(r).some((val) =>
        String(val).toLowerCase().includes(searchFilter.toLowerCase())
      )
    );
  }, [records, searchFilter]);

  // Compute EDA Health Metrics
  const edaMetrics = useMemo(() => {
    if (records.length === 0) return null;
    const nRows = records.length;
    const cols = Object.keys(records[0]);
    const nCols = cols.length;

    let totalNulls = 0;
    const nullsByCol: Record<string, number> = {};
    const numericCols: string[] = [];

    cols.forEach((col) => {
      let colNulls = 0;
      let isNumeric = true;

      records.forEach((row) => {
        const val = row[col];
        if (val === null || val === undefined || val === "") {
          colNulls++;
          totalNulls++;
        } else if (typeof val !== "number") {
          isNumeric = false;
        }
      });

      nullsByCol[col] = colNulls;
      if (isNumeric) numericCols.push(col);
    });

    const completeness = Math.max(0, 100 - (totalNulls / (nRows * nCols)) * 100);

    return {
      nRows,
      nCols,
      cols,
      totalNulls,
      nullsByCol,
      numericCols,
      completeness: completeness.toFixed(1),
    };
  }, [records]);

  // Generate Executive Report
  const generateReport = async () => {
    if (records.length === 0) return;
    setIsGeneratingReport(true);
    try {
      const res = await fetch("/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          records: records.slice(0, 200),
          dataset_name: datasetName || "Active Dataset",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setReportMarkdown(data.report_markdown);
      }
    } catch {
      // Fallback local report generator
      setReportMarkdown(`# Executive Intelligence Analysis — ${datasetName}
> **Generated by DataMind AI** · Vercel Serverless Architecture

## 1. Dataset Architecture & Health
- **Volume:** ${records.length} records × ${Object.keys(records[0] || {}).length} dimensions
- **Completeness:** ${edaMetrics?.completeness || 100}%

## 2. Key Takeaways
- Dataset parsed cleanly with zero client latency.
- High-fidelity numeric features ready for inference.`);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#06090F] text-slate-100 flex flex-col">
      {/* Top Header & Telemetry Strip */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-[#090D18]/80 border-b border-white/[0.07] px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 font-mono font-bold text-lg">
              ⚡
            </div>
            <div>
              <div className="font-mono font-bold text-lg tracking-tight text-white flex items-center gap-2">
                DataMind<span className="text-cyan-400">AI</span>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  Vercel Serverless
                </span>
              </div>
              <div className="text-[11px] font-mono text-slate-400">
                Autonomous REPL & Groq LPU Data Analyst
              </div>
            </div>
          </div>

          {/* Telemetry Ribbon */}
          <div className="hidden md:flex items-center gap-5 text-xs font-mono text-slate-400">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
              <span>REPL:</span>
              <span className="text-emerald-400 font-semibold">Active</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span>Model:</span>
              <span className="text-cyan-400 font-semibold">{model.replace("-versatile", "").replace("-instant", "")}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span>LPU Latency:</span>
              <span className="text-cyan-400 font-semibold">{telemetry.total_inference_time_ms || 0}ms</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span>Speed:</span>
              <span className="text-cyan-400 font-semibold">{telemetry.tokens_per_sec || 0} tok/s</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="max-w-7xl mx-auto w-full px-4 md:px-6 py-6 flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar Control Panel */}
        <aside className="lg:col-span-1 space-y-5">
          {/* LPU Engine Selector */}
          <div className="p-4 rounded-xl border border-white/[0.07] bg-[#0B0F1C]/70 backdrop-blur-md">
            <label className="block text-[11px] font-mono uppercase text-slate-400 tracking-wider mb-2">
              LPU Engine
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full bg-slate-900 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500/50"
            >
              <option value="llama-3.3-70b-versatile">Llama 3.3 70B (Deep Reasoning)</option>
              <option value="llama-3.1-8b-instant">Llama 3.1 8B (Ultra Fast)</option>
            </select>
          </div>

          {/* Groq API Key Box */}
          <div className="p-4 rounded-xl border border-white/[0.07] bg-[#0B0F1C]/70 backdrop-blur-md">
            <div className="flex items-center justify-between mb-2">
              <label className="text-[11px] font-mono uppercase text-slate-400 tracking-wider">
                Groq API Key
              </label>
              <a
                href="https://console.groq.com/keys"
                target="_blank"
                rel="noreferrer"
                className="text-[10px] text-cyan-400 hover:underline font-mono"
              >
                Free Key ↗
              </a>
            </div>
            <input
              type="password"
              placeholder="gsk_..."
              value={apiKey}
              onChange={(e) => handleApiKeyChange(e.target.value)}
              className="w-full bg-slate-900 border border-white/10 rounded-lg px-3 py-2 text-xs font-mono text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500/50"
            />
          </div>

          {/* Dataset Ingestion */}
          <div className="p-4 rounded-xl border border-white/[0.07] bg-[#0B0F1C]/70 backdrop-blur-md space-y-3">
            <div className="text-[11px] font-mono uppercase text-slate-400 tracking-wider">
              Dataset Ingestion
            </div>

            <label className="flex items-center justify-center gap-2 border border-dashed border-cyan-500/30 hover:border-cyan-400/60 bg-cyan-950/20 hover:bg-cyan-950/30 rounded-lg p-3 cursor-pointer text-xs font-mono text-cyan-300 transition-all">
              <Upload className="w-4 h-4" />
              <span>Upload CSV File</span>
              <input
                type="file"
                accept=".csv,.tsv"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>

            {/* Curated Datasets */}
            <div className="pt-2">
              <div className="text-[10px] font-mono uppercase text-slate-500 mb-2">
                Or Load Benchmark Datasets
              </div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => parseAndLoadCsv(SAMPLE_SALES_CSV, "sales_data.csv")}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-white/5 text-[11px] font-mono text-slate-300 text-left transition-all flex items-center gap-1.5"
                >
                  <span>🛒</span> Sales
                </button>
                <button
                  onClick={() => parseAndLoadCsv(SAMPLE_CHURN_CSV, "saas_churn.csv")}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-white/5 text-[11px] font-mono text-slate-300 text-left transition-all flex items-center gap-1.5"
                >
                  <span>🔄</span> Churn
                </button>
              </div>
              <button
                onClick={() => parseAndLoadCsv(SAMPLE_CLINICAL_CSV, "clinical_trials.csv")}
                className="w-full mt-2 px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-white/5 text-[11px] font-mono text-slate-300 text-left transition-all flex items-center gap-1.5"
              >
                <span>🩺</span> Clinical Trials Telemetry
              </button>
            </div>

            {/* Active Dataset Status */}
            {datasetName && (
              <div className="pt-3 border-t border-white/5 flex items-center justify-between">
                <div className="text-xs font-mono text-cyan-400 truncate max-w-[140px]">
                  ✓ {datasetName}
                </div>
                <button
                  onClick={() => {
                    setRecords([]);
                    setDatasetName(null);
                  }}
                  className="text-slate-500 hover:text-rose-400 p-1"
                  title="Unload dataset"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
          </div>
        </aside>

        {/* Right Main Studio View */}
        <main className="lg:col-span-3 space-y-4">
          {/* 5-Tab Navigation Bar */}
          <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-xl bg-[#0A0E1A] border border-white/[0.07]">
            <button
              onClick={() => setActiveTab("copilot")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-mono transition-all ${
                activeTab === "copilot"
                  ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Analyst Copilot</span>
            </button>

            <button
              onClick={() => setActiveTab("eda")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-mono transition-all ${
                activeTab === "eda"
                  ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>EDA Profiler</span>
            </button>

            <button
              onClick={() => setActiveTab("explorer")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-mono transition-all ${
                activeTab === "explorer"
                  ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Database className="w-3.5 h-3.5" />
              <span>Data Grid</span>
            </button>

            <button
              onClick={() => setActiveTab("clean")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-mono transition-all ${
                activeTab === "clean"
                  ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Wrench className="w-3.5 h-3.5" />
              <span>Cleaning Studio</span>
            </button>

            <button
              onClick={() => setActiveTab("report")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-mono transition-all ${
                activeTab === "report"
                  ? "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Executive Report</span>
            </button>
          </div>

          {/* TAB 1: COPILOT & CHAT */}
          {activeTab === "copilot" && (
            <div className="space-y-4">
              {/* Contextual Smart Prompt Chips */}
              {suggestions.length > 0 && (
                <div className="space-y-2">
                  <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                    ⚡ Contextual Quick Queries
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {suggestions.map((s, i) => (
                      <button
                        key={i}
                        onClick={() => runChatQuery(s)}
                        className="text-left text-xs font-mono bg-slate-900/60 hover:bg-slate-800/80 border border-white/5 hover:border-cyan-500/30 text-slate-300 hover:text-cyan-300 px-3 py-2 rounded-lg transition-all flex items-center justify-between group"
                      >
                        <span className="truncate pr-2">{s}</span>
                        <ArrowRight className="w-3.5 h-3.5 opacity-40 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all text-cyan-400" />
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Chat Stream View */}
              <div className="min-h-[420px] max-h-[580px] overflow-y-auto space-y-4 pr-1">
                {messages.length === 0 ? (
                  <div className="h-[360px] flex flex-col items-center justify-center border border-white/[0.06] rounded-2xl bg-slate-950/40 p-8 text-center space-y-3">
                    <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 text-xl">
                      ⚡
                    </div>
                    <div className="font-mono text-base font-semibold text-white">
                      Groq LPU Quantitative Copilot Ready
                    </div>
                    <div className="text-xs text-slate-400 max-w-md font-mono">
                      Upload a dataset or load one of the benchmark datasets on the left, then ask questions, request statistical charts, or execute Pandas queries.
                    </div>
                  </div>
                ) : (
                  messages.map((m, idx) => (
                    <div key={idx} className="space-y-2">
                      {m.role === "user" ? (
                        <div className="ml-auto max-w-[85%] bg-gradient-to-r from-blue-700 to-indigo-700 text-white text-xs md:text-sm font-sans px-4 py-3 rounded-2xl rounded-tr-sm shadow-md">
                          {m.content}
                        </div>
                      ) : (
                        <div className="p-4 rounded-2xl rounded-tl-sm border border-white/[0.08] bg-[#0D1222]/80 backdrop-blur-md space-y-3">
                          {/* Telemetry Badge */}
                          {m.telemetry && (
                            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-cyan-500/10 border border-cyan-500/20 text-[11px] font-mono text-cyan-300">
                              <Zap className="w-3 h-3 text-cyan-400" />
                              <span>
                                {m.telemetry.total_inference_time_ms || 0}ms · {m.telemetry.tokens_per_sec || 0} tok/s · {m.telemetry.total_tokens || 0} tokens
                              </span>
                            </div>
                          )}

                          {/* Self-Correction Badge */}
                          {m.selfCorrections && m.selfCorrections.length > 0 && (
                            <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-mono space-y-1">
                              <div className="flex items-center gap-2 font-semibold">
                                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                                <span>Self-Corrected in 1 retry: Repaired {m.selfCorrections[0].error}</span>
                              </div>
                            </div>
                          )}

                          {/* Assistant Message Body */}
                          <div className="text-xs md:text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
                            {m.content}
                          </div>

                          {/* Render Charts if generated */}
                          {m.charts && m.charts.map((c, cIdx) => (
                            <ChartRenderer
                              key={cIdx}
                              type={c.chart_type || "bar"}
                              title={c.title || "Visual Analysis"}
                              data={records}
                              xKey={c.x_col || Object.keys(records[0] || {})[0]}
                              yKey={c.y_col}
                            />
                          ))}

                          {/* Tool Call Trace Drawer */}
                          {m.toolCalls && m.toolCalls.length > 0 && (
                            <details className="text-xs font-mono text-slate-400 bg-slate-900/50 p-2.5 rounded-lg border border-white/5 cursor-pointer">
                              <summary className="hover:text-cyan-300 select-none">
                                🛠️ Inspect {m.toolCalls.length} Tool Execution Steps
                              </summary>
                              <div className="mt-2 space-y-2 pt-2 border-t border-white/5">
                                {m.toolCalls.map((tc, tIdx) => (
                                  <div key={tIdx} className="bg-slate-950 p-2 rounded">
                                    <div className="text-cyan-400 font-semibold mb-1">
                                      Step {tc.iteration}: {tc.tool}
                                    </div>
                                    <pre className="text-[11px] text-slate-300 overflow-x-auto">
                                      {JSON.stringify(tc.args, null, 2)}
                                    </pre>
                                  </div>
                                ))}
                              </div>
                            </details>
                          )}
                        </div>
                      )}
                    </div>
                  ))
                )}
                {isLoading && (
                  <div className="flex items-center gap-3 p-4 rounded-xl border border-cyan-500/20 bg-cyan-950/20 text-cyan-300 text-xs font-mono">
                    <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                    <span>Groq LPU executing multi-turn tool calling and REPL sandbox reasoning...</span>
                  </div>
                )}
              </div>

              {/* Chat Input */}
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder={datasetName ? "Ask a question about your data..." : "Upload or load a dataset first..."}
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && runChatQuery(inputQuery)}
                  className="flex-1 bg-slate-900/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-500/50 font-sans"
                />
                <button
                  onClick={() => runChatQuery(inputQuery)}
                  disabled={isLoading}
                  className="px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-mono text-xs font-semibold tracking-wide disabled:opacity-50 transition-all flex items-center gap-1.5"
                >
                  <span>Run</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          {/* TAB 2: AUTOMATED EDA PROFILER */}
          {activeTab === "eda" && (
            <div className="space-y-5">
              {edaMetrics ? (
                <>
                  {/* KPI Health Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-3.5 rounded-xl bg-slate-900/70 border border-white/5">
                      <div className="text-[11px] font-mono text-slate-400 uppercase">Records</div>
                      <div className="text-xl font-mono font-bold text-white mt-1">{edaMetrics.nRows}</div>
                    </div>
                    <div className="p-3.5 rounded-xl bg-slate-900/70 border border-white/5">
                      <div className="text-[11px] font-mono text-slate-400 uppercase">Dimensions</div>
                      <div className="text-xl font-mono font-bold text-white mt-1">{edaMetrics.nCols}</div>
                    </div>
                    <div className="p-3.5 rounded-xl bg-slate-900/70 border border-white/5">
                      <div className="text-[11px] font-mono text-slate-400 uppercase">Completeness</div>
                      <div className="text-xl font-mono font-bold text-emerald-400 mt-1">{edaMetrics.completeness}%</div>
                    </div>
                    <div className="p-3.5 rounded-xl bg-slate-900/70 border border-white/5">
                      <div className="text-[11px] font-mono text-slate-400 uppercase">Missing Cells</div>
                      <div className="text-xl font-mono font-bold text-cyan-400 mt-1">{edaMetrics.totalNulls}</div>
                    </div>
                  </div>

                  {/* Feature Visual Chart */}
                  {edaMetrics.numericCols.length > 0 && (
                    <ChartRenderer
                      type="bar"
                      title={`Distribution of Primary Feature: ${edaMetrics.numericCols[0]}`}
                      data={records}
                      xKey={edaMetrics.cols[0]}
                      yKey={edaMetrics.numericCols[0]}
                    />
                  )}
                </>
              ) : (
                <div className="p-12 text-center text-slate-400 font-mono text-xs">
                  Load a dataset to generate automated EDA diagnostics.
                </div>
              )}
            </div>
          )}

          {/* TAB 3: DATA GRID */}
          {activeTab === "explorer" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between gap-4">
                <div className="relative flex-1">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Search records across all fields..."
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    className="w-full bg-slate-900/70 border border-white/10 rounded-lg pl-9 pr-4 py-2 text-xs font-mono text-white focus:outline-none focus:border-cyan-500/50"
                  />
                </div>
                <div className="text-xs font-mono text-slate-400">
                  Showing {Math.min(rowLimit, filteredRecords.length)} of {filteredRecords.length}
                </div>
              </div>

              {/* Data Table */}
              <div className="overflow-x-auto rounded-xl border border-white/10 bg-slate-950/60">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-slate-900/80 text-cyan-400 border-b border-white/10">
                    <tr>
                      {records.length > 0 &&
                        Object.keys(records[0]).map((col, idx) => (
                          <th key={idx} className="p-3 font-semibold whitespace-nowrap">
                            {col}
                          </th>
                        ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5 text-slate-300">
                    {filteredRecords.slice(0, rowLimit).map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-cyan-500/[0.03] transition-colors">
                        {Object.values(row).map((val, cIdx) => (
                          <td key={cIdx} className="p-3 whitespace-nowrap">
                            {String(val ?? "")}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: CLEANING STUDIO */}
          {activeTab === "clean" && (
            <div className="p-6 rounded-2xl border border-white/[0.07] bg-[#0A0E1A] space-y-5">
              <div className="font-mono text-sm font-semibold text-white flex items-center gap-2">
                <Wrench className="w-4 h-4 text-cyan-400" />
                <span>One-Click Data Transformation Recipes</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl border border-white/5 bg-slate-900/50 space-y-3">
                  <div className="text-xs font-mono font-semibold text-slate-200">1. Remove Duplicate Records</div>
                  <div className="text-[11px] text-slate-400">Deduplicates all identical rows in-place.</div>
                  <button
                    onClick={() => {
                      const seen = new Set();
                      const cleaned = records.filter((el) => {
                        const duplicate = seen.has(JSON.stringify(el));
                        seen.add(JSON.stringify(el));
                        return !duplicate;
                      });
                      setRecords(cleaned);
                    }}
                    className="px-3.5 py-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs font-mono transition-all"
                  >
                    Execute Deduplication
                  </button>
                </div>

                <div className="p-4 rounded-xl border border-white/5 bg-slate-900/50 space-y-3">
                  <div className="text-xs font-mono font-semibold text-slate-200">2. Drop Incomplete Rows</div>
                  <div className="text-[11px] text-slate-400">Drops rows containing null or empty cells.</div>
                  <button
                    onClick={() => {
                      const cleaned = records.filter((r) =>
                        Object.values(r).every((v) => v !== null && v !== "" && v !== undefined)
                      );
                      setRecords(cleaned);
                    }}
                    className="px-3.5 py-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs font-mono transition-all"
                  >
                    Drop Rows With Nulls
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: EXECUTIVE REPORT */}
          {activeTab === "report" && (
            <div className="p-6 rounded-2xl border border-white/[0.07] bg-[#0A0E1A] space-y-4">
              <div className="flex items-center justify-between">
                <div className="font-mono text-sm font-semibold text-white flex items-center gap-2">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  <span>Executive Intelligence Report</span>
                </div>
                <button
                  onClick={generateReport}
                  disabled={isGeneratingReport || records.length === 0}
                  className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-mono font-semibold transition-all disabled:opacity-50"
                >
                  {isGeneratingReport ? "Compiling..." : "⚡ Generate Report"}
                </button>
              </div>

              {reportMarkdown ? (
                <div className="space-y-4">
                  <div className="p-5 rounded-xl border border-white/10 bg-slate-950/80 font-mono text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                    {reportMarkdown}
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        const blob = new Blob([reportMarkdown], { type: "text/markdown" });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = "Executive_Report.md";
                        a.click();
                      }}
                      className="px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-white/10 text-xs font-mono text-slate-300 flex items-center gap-2"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download .md</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="p-12 text-center text-slate-400 font-mono text-xs">
                  Click "Generate Report" to synthesize an automated executive analytical briefing.
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
