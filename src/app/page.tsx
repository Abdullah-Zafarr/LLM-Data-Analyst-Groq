"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import Papa from "papaparse";
import {
  ArrowRight,
  ArrowUp,
  BarChart3,
  BookOpenText,
  Bot,
  Braces,
  Check,
  ChevronRight,
  CircleGauge,
  Database,
  Download,
  FileSpreadsheet,
  FileText,
  Menu,
  MessageSquareText,
  RefreshCw,
  Search,
  Settings2,
  Table2,
  Trash2,
  Upload,
  Wand2,
  X,
} from "lucide-react";
import ChartRenderer from "@/components/ChartRenderer";

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

type TabId = "copilot" | "eda" | "explorer" | "clean" | "report";

interface Message {
  role: "user" | "assistant";
  content: string;
  charts?: Record<string, any>[];
  telemetry?: Record<string, any>;
  toolCalls?: Record<string, any>[];
  selfCorrections?: Record<string, any>[];
}

const TABS: { id: TabId; label: string; shortLabel: string; icon: React.ElementType }[] = [
  { id: "copilot", label: "Ask DataMind", shortLabel: "Ask", icon: MessageSquareText },
  { id: "eda", label: "Overview", shortLabel: "Overview", icon: BarChart3 },
  { id: "explorer", label: "Records", shortLabel: "Records", icon: Table2 },
  { id: "clean", label: "Prepare", shortLabel: "Prepare", icon: Wand2 },
  { id: "report", label: "Brief", shortLabel: "Brief", icon: BookOpenText },
];

const DATASETS = [
  { name: "Retail sales", description: "15 orders · revenue & margin", accent: "#ff6b4a", load: SAMPLE_SALES_CSV, file: "sales_data.csv" },
  { name: "SaaS churn", description: "15 accounts · retention signals", accent: "#c6f04f", load: SAMPLE_CHURN_CSV, file: "saas_churn.csv" },
  { name: "Clinical trials", description: "15 patients · efficacy outcomes", accent: "#90b7ff", load: SAMPLE_CLINICAL_CSV, file: "clinical_trials.csv" },
];

function DataEmpty({ onLoad }: { onLoad: () => void }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon"><FileSpreadsheet size={24} strokeWidth={1.7} /></div>
      <h2>There’s no dataset on the desk yet.</h2>
      <p>Bring in a CSV or start with a sample to unlock this view.</p>
      <button className="button button-ink" onClick={onLoad}>
        Load the sales sample <ArrowRight size={15} />
      </button>
    </div>
  );
}

export default function DataMindWorkspace() {
  const [activeTab, setActiveTab] = useState<TabId>("copilot");
  const [records, setRecords] = useState<Record<string, any>[]>([]);
  const [datasetName, setDatasetName] = useState<string | null>(null);
  const [model, setModel] = useState("llama-3.3-70b-versatile");
  const [apiKey, setApiKey] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [telemetry, setTelemetry] = useState<Record<string, any>>({ total_inference_time_ms: 0, tokens_per_sec: 0 });
  const [searchFilter, setSearchFilter] = useState("");
  const [rowLimit, setRowLimit] = useState(25);
  const [reportMarkdown, setReportMarkdown] = useState<string | null>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [cleaningNotice, setCleaningNotice] = useState<string | null>(null);
  const [recordHistory, setRecordHistory] = useState<Record<string, any>[][]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const savedKey = localStorage.getItem("datamind_groq_key");
    if (savedKey) setApiKey(savedKey);
  }, []);


  const parseAndLoadCsv = (csvString: string, name: string) => {
    Papa.parse(csvString, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results) => {
        setRecords(results.data as Record<string, any>[]);
        setDatasetName(name);
        setReportMarkdown(null);
        setMessages([]);
        setSearchFilter("");
        setCleaningNotice(null);
        setRecordHistory([]);
        setMobileMenuOpen(false);
      },
    });
  };

  const loadLocalFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (loaded) => {
      const text = loaded.target?.result as string;
      if (text) parseAndLoadCsv(text, file.name);
    };
    reader.readAsText(file);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    loadLocalFile(file);
    event.target.value = "";
  };

  const clearDataset = () => {
    setRecords([]);
    setDatasetName(null);
    setMessages([]);
    setReportMarkdown(null);
    setSearchFilter("");
    setCleaningNotice(null);
    setRecordHistory([]);
  };

  const commitCleanedRecords = (nextRecords: Record<string, any>[], notice: string) => {
    setRecordHistory((current) => [...current.slice(-4), records]);
    setRecords(nextRecords);
    setCleaningNotice(notice);
  };

  const undoLastClean = () => {
    setRecordHistory((current) => {
      const previous = current[current.length - 1];
      if (previous) {
        setRecords(previous);
        setCleaningNotice("Last transformation undone.");
      }
      return current.slice(0, -1);
    });
  };

  const suggestions = useMemo(() => {
    if (!datasetName) return [];
    const name = datasetName.toLowerCase();
    if (name.includes("sales")) return [
      "Which region is driving the most profit?",
      "Chart revenue by product and explain the pattern",
      "Is the discount rate helping or hurting margin?",
      "Flag unusual orders that deserve a closer look",
    ];
    if (name.includes("churn")) return [
      "Where is churn risk most concentrated?",
      "Compare monthly charges across churn groups",
      "How do support tickets relate to retention?",
      "Which high-value accounts are most at risk?",
    ];
    if (name.includes("clinical")) return [
      "Compare biomarker improvement by cohort",
      "Chart recovery time across treatment groups",
      "Does age appear related to efficacy?",
      "Summarize adverse events and outcomes",
    ];
    const columns = records.length ? Object.keys(records[0]) : [];
    return [
      `Give me a concise profile of ${columns.slice(0, 3).join(", ")}`,
      "Find missing values and distribution issues",
      "Surface the most decision-relevant patterns",
    ];
  }, [datasetName, records]);

  const runChatQuery = async (queryText: string) => {
    if (!queryText.trim() || isLoading) return;
    setMessages((current) => [...current, { role: "user", content: queryText.trim() }]);
    setInputQuery("");
    setIsLoading(true);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_message: queryText.trim(),
          dataset_records: records.length ? records.slice(0, 300) : null,
          dataset_name: datasetName || "dataset.csv",
          model,
          api_key: apiKey || undefined,
        }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "The analysis could not be completed.");
      }
      const data = await response.json();
      setTelemetry(data.telemetry || {});
      setMessages((current) => [...current, {
        role: "assistant",
        content: data.response,
        charts: data.charts || [],
        telemetry: data.telemetry || {},
        toolCalls: data.tool_calls_log || [],
        selfCorrections: data.telemetry?.self_corrections || [],
      }]);
    } catch (error: any) {
      setMessages((current) => [...current, {
        role: "assistant",
        content: `I hit a snag: ${error.message || "Check your Groq API key and try again."}`,
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredRecords = useMemo(() => {
    if (!searchFilter) return records;
    const term = searchFilter.toLowerCase();
    return records.filter((record) =>
      Object.values(record).some((value) => String(value ?? "").toLowerCase().includes(term))
    );
  }, [records, searchFilter]);

  const edaMetrics = useMemo(() => {
    if (!records.length) return null;
    const columns = Object.keys(records[0]);
    let totalNulls = 0;
    const nullsByColumn: Record<string, number> = {};
    const numericColumns: string[] = [];
    columns.forEach((column) => {
      let columnNulls = 0;
      let numeric = true;
      records.forEach((row) => {
        const value = row[column];
        if (value === null || value === undefined || value === "") {
          columnNulls += 1;
          totalNulls += 1;
        } else if (typeof value !== "number") {
          numeric = false;
        }
      });
      nullsByColumn[column] = columnNulls;
      if (numeric) numericColumns.push(column);
    });
    const duplicateCount = records.length - new Set(records.map((row) => JSON.stringify(row))).size;
    const cellCount = Math.max(records.length * columns.length, 1);
    return {
      rows: records.length,
      columns,
      totalNulls,
      nullsByColumn,
      numericColumns,
      duplicateCount,
      completeness: Math.max(0, 100 - (totalNulls / cellCount) * 100),
    };
  }, [records]);

  const generateReport = async () => {
    if (!records.length) return;
    setIsGeneratingReport(true);
    try {
      const response = await fetch("/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ records: records.slice(0, 200), dataset_name: datasetName || "Active dataset" }),
      });
      if (!response.ok) throw new Error("Report service unavailable");
      const data = await response.json();
      setReportMarkdown(data.report_markdown);
    } catch {
      setReportMarkdown(`# Analysis brief — ${datasetName}

## Dataset health
- ${records.length} records across ${Object.keys(records[0] || {}).length} fields
- ${edaMetrics?.completeness.toFixed(1) || 100}% complete
- ${edaMetrics?.duplicateCount || 0} duplicate records detected

## Readout
The dataset parsed successfully and is ready for focused analysis. Use Ask DataMind to investigate a business question or open Overview for a fast structural profile.`);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const downloadCsv = () => {
    if (!records.length) return;
    const url = URL.createObjectURL(new Blob([Papa.unparse(records)], { type: "text/csv;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = datasetName?.replace(/\.csv$/i, "-prepared.csv") || "prepared-data.csv";
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const loadDefault = () => parseAndLoadCsv(SAMPLE_SALES_CSV, "sales_data.csv");
  const activeTabMeta = TABS.find((tab) => tab.id === activeTab) || TABS[0];

  return (
    <div className="workspace-shell">
      {mobileMenuOpen && (
        <button aria-label="Close workspace menu" className="sidebar-scrim" onClick={() => setMobileMenuOpen(false)} />
      )}

      <aside className={`workspace-sidebar ${mobileMenuOpen ? "is-open" : ""}`}>
        <div className="sidebar-topline">
          <a className="wordmark" href="#" aria-label="DataMind home">
            <span className="wordmark-mark">
              <img src="/assets/logo.png" alt="Logo" className="wordmark-logo-img" />
            </span>
            <span>DataMind</span>
          </a>
          <button className="icon-button mobile-only" onClick={() => setMobileMenuOpen(false)} aria-label="Close menu">
            <X size={18} />
          </button>
        </div>

        <div className="sidebar-scroll">
          <section className="sidebar-section">
            <div className="eyebrow sidebar-eyebrow">Your data</div>
            {datasetName ? (
              <div className="active-dataset-card">
                <div className="dataset-file-icon"><FileSpreadsheet size={20} /></div>
                <div className="min-w-0">
                  <div className="dataset-file-name">{datasetName}</div>
                  <div className="dataset-file-meta">{records.length} rows · {Object.keys(records[0] || {}).length} fields</div>
                </div>
                <button className="dataset-remove" onClick={clearDataset} aria-label="Remove dataset" title="Remove dataset">
                  <Trash2 size={15} />
                </button>
              </div>
            ) : (
              <button
                className="upload-dropzone"
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(event) => event.preventDefault()}
                onDrop={(event) => {
                  event.preventDefault();
                  const file = event.dataTransfer.files?.[0];
                  if (file) loadLocalFile(file);
                }}
              >
                <Upload size={18} />
                <span><strong>Choose a CSV</strong><small>or drop it here</small></span>
              </button>
            )}
            {datasetName && (
              <button className="sidebar-text-button" onClick={() => fileInputRef.current?.click()}>
                <Upload size={14} /> Replace dataset
              </button>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.tsv,text/csv,text/tab-separated-values"
              onChange={handleFileUpload}
              className="sr-only"
            />
          </section>

          <section className="sidebar-section">
            <div className="eyebrow sidebar-eyebrow">Sample desks</div>
            <div className="dataset-list">
              {DATASETS.map((dataset) => (
                <button
                  key={dataset.file}
                  className={`dataset-list-item ${datasetName === dataset.file ? "is-active" : ""}`}
                  onClick={() => parseAndLoadCsv(dataset.load, dataset.file)}
                >
                  <span className="dataset-accent" style={{ backgroundColor: dataset.accent }} />
                  <span><strong>{dataset.name}</strong><small>{dataset.description}</small></span>
                  <ChevronRight size={15} />
                </button>
              ))}
            </div>
          </section>

          <section className="sidebar-section sidebar-settings">
            <div className="eyebrow sidebar-eyebrow"><span>Connection</span><Settings2 size={13} /></div>
            <label className="field-label" htmlFor="model-select">Model</label>
            <select id="model-select" value={model} onChange={(event) => setModel(event.target.value)} className="sidebar-select">
              <option value="llama-3.3-70b-versatile">Llama 3.3 70B · deep</option>
              <option value="llama-3.1-8b-instant">Llama 3.1 8B · fast</option>
            </select>
          </section>
        </div>

        <div className="sidebar-footer">
          <span className="sidebar-version">v1.0</span>
        </div>
      </aside>

      <div className="workspace-main">
        <header className="workspace-header">
          <div className="header-title-group">
            <button className="icon-button mobile-only" onClick={() => setMobileMenuOpen(true)} aria-label="Open workspace menu">
              <Menu size={19} />
            </button>
            <div>
              <div className="header-kicker">Workspace / {activeTabMeta.label}</div>
              <h1>{datasetName ? datasetName.replace(/\.[^/.]+$/, "").replace(/_/g, " ") : "Untitled analysis"}</h1>
            </div>
          </div>
          <div className="telemetry-strip">
            <div><span>Engine</span><strong>{model.includes("70b") ? "70B Deep" : "8B Fast"}</strong></div>
            <div><span>Latency</span><strong>{telemetry.total_inference_time_ms || "—"}{telemetry.total_inference_time_ms ? " ms" : ""}</strong></div>
          </div>
        </header>

        <nav className="workspace-tabs" aria-label="Analysis views">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={activeTab === tab.id ? "is-active" : ""}
                aria-current={activeTab === tab.id ? "page" : undefined}
              >
                <Icon size={16} />
                <span className="tab-long-label">{tab.label}</span>
                <span className="tab-short-label">{tab.shortLabel}</span>
              </button>
            );
          })}
        </nav>

        <main className="content-canvas">
          {activeTab === "copilot" && (
            <section className="copilot-view view-enter">
              {messages.length === 0 ? (
                <div className="copilot-intro">
                  <div className="intro-copy">
                    <div className="eyebrow">Conversational analysis</div>
                    <h2>Ask a sharper question.<br /><em>Get a useful answer.</em></h2>
                    <p>DataMind reads the structure, runs the analysis, and explains what matters—without making you write the query.</p>
                  </div>

                  {datasetName ? (
                    <div className="suggestion-grid">
                      {suggestions.map((suggestion, index) => (
                        <button key={suggestion} onClick={() => runChatQuery(suggestion)}>
                          <span className="suggestion-index">0{index + 1}</span>
                          <span>{suggestion}</span>
                          <ArrowRight size={16} />
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="start-panel">
                      <div>
                        <FileSpreadsheet size={20} />
                        <span><strong>Start with some data</strong><small>Upload a file from the sidebar or open the retail sample.</small></span>
                      </div>
                      <button onClick={loadDefault}>Open retail sample <ArrowRight size={15} /></button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="conversation">
                  <div className="conversation-heading">
                    <div><span className="eyebrow">Analysis thread</span><h2>{messages.length} message{messages.length === 1 ? "" : "s"}</h2></div>
                    <button className="button button-quiet" onClick={() => setMessages([])}>New thread</button>
                  </div>
                  <div className="message-list">
                    {messages.map((message, index) => (
                      <article key={index} className={`message ${message.role}`}>
                        <div className="message-avatar">
                          {message.role === "assistant" ? <Bot size={17} /> : <span>YOU</span>}
                        </div>
                        <div className="message-body">
                          <div className="message-label">{message.role === "assistant" ? "DataMind" : "You"}</div>
                          <div className="message-content">{message.content}</div>
                          {message.selfCorrections && message.selfCorrections.length > 0 && (
                            <div className="correction-note"><RefreshCw size={14} /> The analysis repaired one execution step automatically.</div>
                          )}
                          {message.charts?.map((chart, chartIndex) => (
                            <ChartRenderer
                              key={chartIndex}
                              type={chart.chart_type || "bar"}
                              title={chart.title || "Visual analysis"}
                              data={records}
                              xKey={chart.x_col || Object.keys(records[0] || {})[0]}
                              yKey={chart.y_col}
                            />
                          ))}
                          {message.toolCalls && message.toolCalls.length > 0 && (
                            <details className="trace-details">
                              <summary><Braces size={14} /> {message.toolCalls.length} analysis step{message.toolCalls.length > 1 ? "s" : ""}</summary>
                              <div className="trace-list">
                                {message.toolCalls.map((toolCall, toolIndex) => (
                                  <div key={toolIndex}>
                                    <strong>{toolCall.tool || `Step ${toolIndex + 1}`}</strong>
                                    <pre>{JSON.stringify(toolCall.args, null, 2)}</pre>
                                  </div>
                                ))}
                              </div>
                            </details>
                          )}
                          {message.telemetry && message.role === "assistant" && (
                            <div className="message-meta">
                              {message.telemetry.total_inference_time_ms || 0} ms<span />
                              {message.telemetry.total_tokens || 0} tokens<span />
                              {message.telemetry.tokens_per_sec || 0} tok/s
                            </div>
                          )}
                        </div>
                      </article>
                    ))}
                    {isLoading && (
                      <article className="message assistant is-loading">
                        <div className="message-avatar"><Bot size={17} /></div>
                        <div className="message-body">
                          <div className="message-label">DataMind</div>
                          <div className="thinking-line"><span /><span /><span /> Working through the data</div>
                        </div>
                      </article>
                    )}
                  </div>
                </div>
              )}

              <div className="composer-wrap">
                <div className="composer">
                  <textarea
                    aria-label="Ask a question about your data"
                    placeholder={datasetName ? "Ask anything about this dataset…" : "Load a dataset, then ask a question…"}
                    value={inputQuery}
                    onChange={(event) => setInputQuery(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" && !event.shiftKey) {
                        event.preventDefault();
                        runChatQuery(inputQuery);
                      }
                    }}
                    rows={1}
                  />
                  <div className="composer-footer">
                    <span>{datasetName ? `${records.length} rows in context` : "No dataset attached"}</span>
                    <button onClick={() => runChatQuery(inputQuery)} disabled={!inputQuery.trim() || isLoading} aria-label="Send question">
                      {isLoading ? <RefreshCw size={17} className="spin" /> : <ArrowUp size={18} />}
                    </button>
                  </div>
                </div>
                <p>DataMind can make mistakes. Verify high-impact decisions.</p>
              </div>
            </section>
          )}

          {activeTab === "eda" && (
            <section className="view-enter">
              {!edaMetrics ? <DataEmpty onLoad={loadDefault} /> : (
                <>
                  <div className="section-heading">
                    <div>
                      <span className="eyebrow">Automatic profile</span>
                      <h2>The shape of your data</h2>
                      <p>A quick structural read before you ask deeper questions.</p>
                    </div>
                    <div className="quality-badge"><span>{edaMetrics.completeness.toFixed(1)}%</span>data complete</div>
                  </div>
                  <div className="metric-grid">
                    <article className="metric-card metric-card-primary"><span>Records</span><strong>{edaMetrics.rows.toLocaleString()}</strong><small>rows available for analysis</small></article>
                    <article className="metric-card"><span>Fields</span><strong>{edaMetrics.columns.length}</strong><small>{edaMetrics.numericColumns.length} numeric features</small></article>
                    <article className="metric-card"><span>Missing</span><strong>{edaMetrics.totalNulls}</strong><small>{edaMetrics.totalNulls ? "cells need attention" : "nothing missing"}</small></article>
                    <article className="metric-card"><span>Duplicates</span><strong>{edaMetrics.duplicateCount}</strong><small>{edaMetrics.duplicateCount ? "safe to review" : "all rows unique"}</small></article>
                  </div>
                  <div className="overview-grid">
                    <article className="panel profile-panel">
                      <div className="panel-heading"><div><span className="eyebrow">Field health</span><h3>Completeness by column</h3></div><CircleGauge size={20} /></div>
                      <div className="field-health-list">
                        {edaMetrics.columns.slice(0, 8).map((column) => {
                          const complete = 100 - (edaMetrics.nullsByColumn[column] / edaMetrics.rows) * 100;
                          return (
                            <div className="field-health-row" key={column}>
                              <div><span>{column}</span><strong>{complete.toFixed(0)}%</strong></div>
                              <div className="health-track"><span style={{ width: `${complete}%` }} /></div>
                            </div>
                          );
                        })}
                      </div>
                    </article>
                    <article className="panel schema-panel">
                      <div className="panel-heading"><div><span className="eyebrow">Schema</span><h3>What’s inside</h3></div><Database size={19} /></div>
                      <div className="schema-chips">
                        {edaMetrics.columns.map((column) => (
                          <span key={column} className={edaMetrics.numericColumns.includes(column) ? "numeric" : "textual"}>
                            {column}<small>{edaMetrics.numericColumns.includes(column) ? "123" : "abc"}</small>
                          </span>
                        ))}
                      </div>
                    </article>
                  </div>
                  {edaMetrics.numericColumns.length > 0 && (
                    <ChartRenderer
                      type="bar"
                      title={`${edaMetrics.numericColumns[0]} at a glance`}
                      data={records}
                      xKey={edaMetrics.columns[0]}
                      yKey={edaMetrics.numericColumns[0]}
                    />
                  )}
                </>
              )}
            </section>
          )}

          {activeTab === "explorer" && (
            <section className="view-enter">
              {!records.length ? <DataEmpty onLoad={loadDefault} /> : (
                <>
                  <div className="section-heading section-heading-compact">
                    <div><span className="eyebrow">Raw records</span><h2>Look closely</h2></div>
                    <button className="button button-outline" onClick={downloadCsv}><Download size={15} /> Export CSV</button>
                  </div>
                  <div className="table-toolbar">
                    <label className="search-field">
                      <Search size={16} />
                      <input type="search" placeholder="Search every field…" value={searchFilter} onChange={(event) => setSearchFilter(event.target.value)} />
                      {searchFilter && <button onClick={() => setSearchFilter("")} aria-label="Clear search"><X size={14} /></button>}
                    </label>
                    <div className="table-count">
                      {filteredRecords.length.toLocaleString()} result{filteredRecords.length === 1 ? "" : "s"}
                      <select value={rowLimit} onChange={(event) => setRowLimit(Number(event.target.value))} aria-label="Rows per page">
                        <option value={10}>10 rows</option><option value={25}>25 rows</option><option value={50}>50 rows</option><option value={100}>100 rows</option>
                      </select>
                    </div>
                  </div>
                  <div className="data-table-wrap">
                    <table className="data-table">
                      <thead><tr><th className="row-number">#</th>{Object.keys(records[0]).map((column) => <th key={column}>{column}</th>)}</tr></thead>
                      <tbody>
                        {filteredRecords.slice(0, rowLimit).map((row, rowIndex) => (
                          <tr key={rowIndex}>
                            <td className="row-number">{String(rowIndex + 1).padStart(2, "0")}</td>
                            {Object.keys(records[0]).map((column) => <td key={column} title={String(row[column] ?? "")}>{String(row[column] ?? "—")}</td>)}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {!filteredRecords.length && <div className="no-results">No records match “{searchFilter}”.</div>}
                  </div>
                </>
              )}
            </section>
          )}

          {activeTab === "clean" && (
            <section className="view-enter">
              {!edaMetrics ? <DataEmpty onLoad={loadDefault} /> : (
                <>
                  <div className="section-heading">
                    <div><span className="eyebrow">Prepare the dataset</span><h2>Clean, with intent</h2><p>Small, transparent transformations. Your source file stays untouched.</p></div>
                    {recordHistory.length > 0 && (
                      <button className="button button-outline" onClick={undoLastClean}>
                        <RefreshCw size={14} /> Undo last change
                      </button>
                    )}
                  </div>
                  {cleaningNotice && <div className="success-notice"><Check size={16} /> {cleaningNotice}</div>}
                  <div className="recipe-grid">
                    <article className="recipe-card">
                      <div className="recipe-number">01</div><div className="recipe-icon coral"><Braces size={20} /></div>
                      <h3>Remove duplicates</h3><p>Keep the first instance of repeated rows and discard exact copies.</p>
                      <div className="recipe-stat"><strong>{edaMetrics.duplicateCount}</strong><span>duplicate rows found</span></div>
                      <button
                        className="button button-ink"
                        disabled={!edaMetrics.duplicateCount}
                        onClick={() => {
                          const seen = new Set<string>();
                          const cleaned = records.filter((row) => {
                            const key = JSON.stringify(row);
                            if (seen.has(key)) return false;
                            seen.add(key);
                            return true;
                          });
                          const removed = records.length - cleaned.length;
                          commitCleanedRecords(cleaned, `${removed} duplicate row${removed === 1 ? "" : "s"} removed.`);
                        }}
                      >Remove duplicates <ArrowRight size={15} /></button>
                    </article>
                    <article className="recipe-card">
                      <div className="recipe-number">02</div><div className="recipe-icon lime"><Wand2 size={20} /></div>
                      <h3>Drop incomplete rows</h3><p>Remove any row containing a blank, null, or undefined value.</p>
                      <div className="recipe-stat"><strong>{edaMetrics.totalNulls}</strong><span>missing cells found</span></div>
                      <button
                        className="button button-ink"
                        disabled={!edaMetrics.totalNulls}
                        onClick={() => {
                          const cleaned = records.filter((row) => Object.values(row).every((value) => value !== null && value !== "" && value !== undefined));
                          const removed = records.length - cleaned.length;
                          commitCleanedRecords(cleaned, `${removed} incomplete row${removed === 1 ? "" : "s"} removed.`);
                        }}
                      >Drop incomplete rows <ArrowRight size={15} /></button>
                    </article>
                    <article className="recipe-card recipe-card-export">
                      <div className="recipe-number">03</div><div className="recipe-icon blue"><Download size={20} /></div>
                      <h3>Take it with you</h3><p>Download the current working copy as a clean, portable CSV.</p>
                      <div className="recipe-stat"><strong>{records.length}</strong><span>rows ready to export</span></div>
                      <button className="button button-lime" onClick={downloadCsv}>Download prepared CSV <Download size={15} /></button>
                    </article>
                  </div>
                </>
              )}
            </section>
          )}

          {activeTab === "report" && (
            <section className="view-enter">
              {!records.length ? <DataEmpty onLoad={loadDefault} /> : (
                <>
                  <div className="section-heading section-heading-compact">
                    <div><span className="eyebrow">Decision-ready output</span><h2>The brief</h2><p>Turn the current dataset into an executive readout.</p></div>
                    <button className="button button-lime" onClick={generateReport} disabled={isGeneratingReport}>
                      {isGeneratingReport ? <><RefreshCw size={15} className="spin" /> Drafting</> : <><FileText size={15} /> Generate brief</>}
                    </button>
                  </div>
                  {reportMarkdown ? (
                    <article className="report-paper">
                      <div className="report-paper-top">
                        <div><span>DATAMIND / ANALYSIS BRIEF</span><strong>{new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</strong></div>
                        <button
                          className="button button-outline"
                          onClick={() => {
                            const url = URL.createObjectURL(new Blob([reportMarkdown], { type: "text/markdown" }));
                            const anchor = document.createElement("a");
                            anchor.href = url;
                            anchor.download = "datamind-analysis-brief.md";
                            anchor.click();
                            URL.revokeObjectURL(url);
                          }}
                        ><Download size={14} /> Download</button>
                      </div>
                      <div className="report-content">{reportMarkdown}</div>
                    </article>
                  ) : (
                    <div className="report-placeholder">
                      <div className="report-placeholder-art"><span /><span /><span /><span /></div>
                      <h3>A one-page readout, written for decisions.</h3>
                      <p>Generate a concise brief covering data health, key signals, and the next questions worth asking.</p>
                      <button className="button button-ink" onClick={generateReport} disabled={isGeneratingReport}>Generate your first brief <ArrowRight size={15} /></button>
                    </div>
                  )}
                </>
              )}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
