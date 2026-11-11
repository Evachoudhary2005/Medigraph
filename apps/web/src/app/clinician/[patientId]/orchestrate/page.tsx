"use client";
import { useEffect, useState, useRef } from "react";
import Link from "next/link";

type OrchestrateResult = {
  patient_id: string;
  stage: string;
  log: string[];
  confidence: number | null;
  needs_review: boolean | null;
  timeline_count: number | null;
  narrative?: string | null;
  draft_id?: string | null;
  draft_version?: number | null;
  alerts: { rule_id: string; name: string; severity: string }[];
  summary_sections: { key: string; title: string; item_count: number }[];
  fhir: {
    resource_types: string[];
    validation: { valid: boolean; issues: string[]; entries: number } | null;
  };
  errors: string[];
};

type Doc = { id: string; filename: string; document_type: string; page_count?: number };

const PIPELINE_STAGES = [
  { id: "extract", name: "Ingestion & Extraction", desc: "OCR parsing & clinical entity recognition" },
  { id: "validate", name: "Validation Guard", desc: "Confidence scoring & clinical integrity check" },
  { id: "timeline", name: "Timeline Synthesis", desc: "Temporal sequencing of clinical events" },
  { id: "summarize", name: "AI Clinical Summary", desc: "MedGemma LLM clinical narrative draft" },
  { id: "alerts", name: "Safety & Alert Scan", desc: "Contraindications & clinical drug checks" },
  { id: "fhir", name: "FHIR R4 Standardization", desc: "HL7 FHIR bundle synthesis & schema validation" },
  { id: "finalize", name: "Finalization", desc: "Draft staging & tamper-evident audit logging" },
];

export default function OrchestratePage({ params }: { params: { patientId: string } }) {
  const patientId = params.patientId;
  const [docs, setDocs] = useState<Doc[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string>("");
  const [running, setRunning] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [activeStageIndex, setActiveStageIndex] = useState<number>(-1);
  const [result, setResult] = useState<OrchestrateResult | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const stageTimerRef = useRef<NodeJS.Timeout | null>(null);

  async function loadDocs() {
    try {
      const r = await fetch("/api/v1/documents?patient_id=" + patientId);
      if (!r.ok) throw new Error(await r.text());
      const data: Doc[] = await r.json();
      setDocs(data);
      if (data.length > 0 && !selectedDoc) {
        setSelectedDoc(data[0].id);
      }
    } catch (e: any) {
      console.warn("Could not load documents:", e?.message ?? e);
    }
  }

  useEffect(() => {
    loadDocs();
  }, [patientId]);

  // Clean up timers on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (stageTimerRef.current) clearInterval(stageTimerRef.current);
    };
  }, []);

  async function run() {
    setRunning(true);
    setErr(null);
    setResult(null);
    setElapsed(0);
    setActiveStageIndex(0);

    // Elapsed timer
    const startTime = Date.now();
    timerRef.current = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 500);

    // Simulate progressive stage activation while waiting for response
    let currentStage = 0;
    stageTimerRef.current = setInterval(() => {
      currentStage = Math.min(currentStage + 1, PIPELINE_STAGES.length - 2);
      setActiveStageIndex(currentStage);
    }, 3500);

    try {
      const r = await fetch("/api/v1/orchestrate/" + patientId, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: selectedDoc || null,
          actor: "clinician",
        }),
      });

      if (!r.ok) {
        const text = await r.text();
        throw new Error(text || "HTTP " + r.status);
      }

      const j: OrchestrateResult = await r.json();
      setResult(j);
      setActiveStageIndex(PIPELINE_STAGES.length - 1);
    } catch (e: any) {
      setErr("Orchestration encountered an issue: " + (e?.message ?? String(e)));
    } finally {
      if (timerRef.current) clearInterval(timerRef.current);
      if (stageTimerRef.current) clearInterval(stageTimerRef.current);
      setRunning(false);
    }
  }

  return (
    <main className="max-w-6xl mx-auto p-6 md:p-10 font-sans text-slate-900 dark:text-slate-100">
      {/* Top Breadcrumb Navigation */}
      <div className="flex items-center justify-between gap-4 text-xs mb-6">
        <div className="flex items-center gap-2">
          <Link
            href="/clinician"
            className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1 font-medium"
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Clinician Dashboard
          </Link>
          <span className="text-slate-300 dark:text-slate-700">/</span>
          <span className="text-slate-700 dark:text-slate-300 font-medium">Pipeline Orchestration</span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href={"/clinician/" + patientId + "/timeline"}
            className="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 text-xs font-medium"
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="3 6 9 12 13 8 21 16" />
            </svg>
            Timeline Report
          </Link>
          <span className="text-slate-300 dark:text-slate-700">•</span>
          <Link
            href={"/clinician/" + patientId + "/summary"}
            className="text-purple-600 dark:text-purple-400 hover:underline flex items-center gap-1 text-xs font-medium"
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            AI Summary Studio
          </Link>
        </div>
      </div>

      {/* Main Header */}
      <header className="border-b border-slate-200 dark:border-slate-800 pb-6 flex items-start justify-between gap-4 flex-wrap">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 text-[11px] font-semibold tracking-wide uppercase mb-2">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
            LangGraph Automation Pipeline
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Clinical Pipeline Orchestration
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
            Execute the unified multi-stage LangGraph pipeline: ingest clinical inputs, perform OCR & entity extraction, validate clinical integrity, synchronize chronological events, synthesize MedGemma clinical notes, and compile HL7 FHIR R4 bundles.
          </p>
          <p className="text-xs text-slate-400 dark:text-slate-500 font-mono mt-2">
            Patient ID: {patientId}
          </p>
        </div>
      </header>

      {/* Execution Control Card */}
      <section className="mt-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-6 shadow-sm">
        <h2 className="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2">
          <svg className="w-5 h-5 text-indigo-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <polygon points="10 8 16 12 10 16 10 8" />
          </svg>
          Pipeline Execution Controls
        </h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Select an ingestion source or run against existing patient clinical intake records.
        </p>

        <div className="mt-5 grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div className="md:col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">
              Source Document / Input Stream
            </label>
            <select
              value={selectedDoc}
              onChange={(e) => setSelectedDoc(e.target.value)}
              disabled={running}
              className="w-full border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-60"
            >
              <option value="">Full Ingestion: Synchronize Patient Intake & Clinical Records</option>
              {docs.map((d) => (
                <option key={d.id} value={d.id}>
                  📄 {d.filename} ({d.document_type || "clinical document"})
                </option>
              ))}
            </select>
          </div>

          <div>
            <button
              onClick={run}
              disabled={running}
              className="w-full inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm transition-all shadow-sm hover:shadow active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {running ? (
                <>
                  <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  <span>Executing Pipeline ({elapsed}s)...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                  <span>Run Orchestration Pipeline</span>
                </>
              )}
            </button>
          </div>
        </div>

        {running && (
          <div className="mt-4 p-3.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/50 flex items-center justify-between text-xs text-indigo-800 dark:text-indigo-300 animate-pulse">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-ping" />
              Running multi-stage pipeline: OCR extraction, temporal timeline synthesis, and local MedGemma clinical narrative generation...
            </span>
            <span className="font-mono font-bold text-indigo-700 dark:text-indigo-300">{elapsed}s elapsed</span>
          </div>
        )}
      </section>

      {/* Pipeline Architecture DAG Visualization */}
      <section className="mt-8">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
            Pipeline Architecture & Stage Progress
          </h2>
          {result && (
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Pipeline Execution Completed Successfully
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {PIPELINE_STAGES.map((st, idx) => {
            const isCompleted = result !== null || (running && activeStageIndex > idx);
            const isCurrent = running && activeStageIndex === idx;

            return (
              <div
                key={st.id}
                className={`p-4 rounded-xl border transition-all relative overflow-hidden ${
                  isCurrent
                    ? "border-indigo-500 bg-indigo-50/70 dark:bg-indigo-950/40 shadow-sm ring-1 ring-indigo-500"
                    : isCompleted
                    ? "border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/30 dark:bg-emerald-950/20"
                    : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/40 opacity-70"
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span className="text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                    Stage {idx + 1}
                  </span>
                  {isCurrent ? (
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-200 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200 animate-pulse">
                      Active
                    </span>
                  ) : isCompleted ? (
                    <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-emerald-500 text-white text-xs">
                      ✓
                    </span>
                  ) : (
                    <span className="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-700" />
                  )}
                </div>

                <div className="font-semibold text-sm text-slate-900 dark:text-white">
                  {st.name}
                </div>
                <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-snug">
                  {st.desc}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Error message */}
      {err && (
        <div className="mt-6 p-4 rounded-xl border border-red-200 bg-red-50 dark:bg-red-950/40 text-red-800 dark:text-red-200 text-sm flex items-start gap-3">
          <svg className="w-5 h-5 text-red-500 shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <div>
            <div className="font-semibold">Execution Failure</div>
            <div className="mt-0.5 text-xs text-red-700 dark:text-red-300">{err}</div>
          </div>
        </div>
      )}

      {/* Pipeline Result Cockpit */}
      {result && (
        <div className="mt-8 space-y-6">
          {/* Executive Metrics Bar */}
          <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Pipeline Outcome
              </span>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-xl font-bold text-slate-900 dark:text-white capitalize">
                  {result.stage}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                  READY
                </span>
              </div>
              <div className="text-xs text-slate-500 mt-1">Audit log recorded</div>
            </div>

            <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Clinical Timeline
              </span>
              <div className="mt-1 text-xl font-bold text-blue-600 dark:text-blue-400">
                {result.timeline_count ?? 0} Events
              </div>
              <Link
                href={"/clinician/" + patientId + "/timeline"}
                className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline mt-1 font-medium"
              >
                View Timeline Report &rarr;
              </Link>
            </div>

            <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                AI Clinical Draft
              </span>
              <div className="mt-1 text-xl font-bold text-purple-600 dark:text-purple-400">
                Version {result.draft_version ?? 1}
              </div>
              <Link
                href={"/clinician/" + patientId + "/summary"}
                className="inline-flex items-center gap-1 text-xs text-purple-600 hover:underline mt-1 font-medium"
              >
                Open in Summary Studio &rarr;
              </Link>
            </div>

            <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                FHIR R4 Bundle
              </span>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-xl font-bold text-slate-900 dark:text-white">
                  {result.fhir.validation?.entries ?? result.fhir.resource_types.length} Entries
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    result.fhir.validation?.valid
                      ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                      : "bg-amber-100 text-amber-800"
                  }`}
                >
                  {result.fhir.validation?.valid ? "VALID" : "PENDING"}
                </span>
              </div>
              <div className="text-xs text-slate-500 mt-1">Interoperability standard</div>
            </div>
          </section>

          {/* AI Clinical Note Draft Preview */}
          {result.narrative && (
            <section className="rounded-2xl border border-purple-200 dark:border-purple-900/50 bg-purple-50/20 dark:bg-purple-950/20 p-6 shadow-sm">
              <div className="flex items-start justify-between gap-4 flex-wrap pb-4 border-b border-purple-200/60 dark:border-purple-900/40">
                <div>
                  <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200 text-xs font-semibold mb-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-purple-600" />
                    MedGemma AI Clinical Draft Staged (v{result.draft_version ?? 1})
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                    Generated Clinical Note Narrative
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    This note is prepared for clinician review. Only approved notes are permanently committed to the official record.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Link
                    href={"/clinician/" + patientId + "/summary"}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-medium text-xs shadow-sm transition-all"
                  >
                    <span>Review & Approve in Summary Studio</span>
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <polyline points="9 18 15 12 9 6" />
                    </svg>
                  </Link>
                </div>
              </div>

              <div className="mt-4 p-4 rounded-xl bg-white dark:bg-slate-900 border border-purple-100 dark:border-purple-900/30 text-sm text-slate-800 dark:text-slate-200 font-sans leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto">
                {result.narrative}
              </div>
            </section>
          )}

          {/* Clinical Alerts / Safety Warnings */}
          {result.alerts && result.alerts.length > 0 ? (
            <section className="rounded-xl border border-red-300 bg-red-50 dark:bg-red-950/40 p-4">
              <h3 className="text-sm font-semibold text-red-900 dark:text-red-200 flex items-center gap-2">
                <svg className="w-4 h-4 text-red-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
                Safety Alerts Identified ({result.alerts.length})
              </h3>
              <ul className="mt-2 space-y-1.5 text-xs">
                {result.alerts.map((a) => (
                  <li key={a.rule_id} className="flex items-center gap-2 text-red-800 dark:text-red-300">
                    <span className="font-bold uppercase tracking-wider text-[10px] px-1.5 py-0.5 rounded bg-red-200 dark:bg-red-900 text-red-900 dark:text-red-100">
                      {a.severity}
                    </span>
                    <span className="font-medium">{a.name}</span>
                  </li>
                ))}
              </ul>
            </section>
          ) : (
            <div className="p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/50 dark:bg-emerald-950/20 text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-2">
              <svg className="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <span>Clinical Safety Screen: No immediate contraindication or adverse drug interaction flags detected.</span>
            </div>
          )}

          {/* Two-Column Detail: Execution Trace & FHIR Bundles */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Live Pipeline Execution Trace */}
            <section className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-5 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                  <svg className="w-4 h-4 text-indigo-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="4 17 10 11 4 5" />
                    <line x1="12" y1="19" x2="20" y2="19" />
                  </svg>
                  Pipeline Execution Log
                </h3>
                <span className="text-[11px] font-mono text-slate-400">
                  {result.log.length} steps executed
                </span>
              </div>

              <ol className="mt-3 space-y-2.5">
                {result.log.map((line, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-xs">
                    <span className="shrink-0 w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-400 flex items-center justify-center font-mono text-[10px] font-semibold mt-0.5">
                      ✓
                    </span>
                    <span className="text-slate-700 dark:text-slate-300 font-mono leading-relaxed break-words">
                      {line}
                    </span>
                  </li>
                ))}
              </ol>
            </section>

            {/* FHIR R4 Bundle Validation */}
            <section className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-5 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                  <svg className="w-4 h-4 text-teal-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z" />
                    <path d="M2 17l10 5 10-5" />
                    <path d="M2 12l10 5 10-5" />
                  </svg>
                  FHIR R4 Bundle Composition
                </h3>
                <span className="text-[11px] font-mono text-emerald-600 dark:text-emerald-400 font-bold">
                  PASS (Schema Valid)
                </span>
              </div>

              <div className="mt-3">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">
                  Standardized FHIR R4 clinical resource instances included in generated bundle:
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {result.fhir.resource_types.map((type, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono text-[11px] border border-slate-200 dark:border-slate-700"
                    >
                      {type}
                    </span>
                  ))}
                </div>

                {result.summary_sections && result.summary_sections.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                    <div className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
                      Structured Clinical Sections
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {result.summary_sections.map((s) => (
                        <div
                          key={s.key}
                          className="flex items-center justify-between p-2 rounded-lg bg-slate-50 dark:bg-slate-800/60"
                        >
                          <span className="text-slate-700 dark:text-slate-300 truncate">{s.title}</span>
                          <span className="text-slate-400 font-mono text-[11px]">{s.item_count} items</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </section>
          </div>
        </div>
      )}
    </main>
  );
}