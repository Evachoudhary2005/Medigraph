"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

type Event = {
  id: string;
  event_date: string | null;
  kind: string;
  label: string;
  value: string;
  normalized: Record<string, any>;
  source: "document" | "intake" | "voice" | string;
  source_ref: string;
  source_excerpt: string;
  confidence: number;
  needs_review: boolean;
  verification_status: string;
  conflict_group: string | null;
};

type ApprovedSummary = {
  id: string;
  version: number;
  status: string;
  actor: string;
  notes: string;
  created_at: string;
  narrative: string;
  sections?: Array<{
    key: string;
    title: string;
    items: Array<{ event_id: string; text: string; confidence?: number }>;
  }>;
};

const QUESTION_LABELS: Record<string, string> = {
  q_cc_main: "Chief Complaint",
  q_cc_duration: "Duration of Symptoms",
  q_cc_severity: "Severity Assessment",
  q_hpi_onset: "Onset of Symptoms",
  q_hpi_associated: "Associated Symptoms",
  q_pmh_conditions: "Chronic Medical History",
  q_med_allergies: "Drug / Medical Allergies",
  q_med_allergies_detail: "Allergy Details",
  q_pers_smoking: "Smoking History",
  q_pers_alcohol: "Alcohol Consumption",
  gender: "Biological Gender",
  issue_date: "Encounter / Document Date",
  date_of_birth: "Date of Birth",
};

function humanizeLabel(raw: string): string {
  if (QUESTION_LABELS[raw]) return QUESTION_LABELS[raw];
  return raw
    .replace(/^q_/, "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, l => l.toUpperCase());
}

function formatValue(val: any, labelKey?: string): string {
  if (!val) return "Not specified";

  let parsed = val;
  if (typeof val === "string") {
    const trimmed = val.trim();
    if ((trimmed.startsWith("{") && trimmed.endsWith("}")) || (trimmed.startsWith("[") && trimmed.endsWith("]"))) {
      try {
        parsed = JSON.parse(trimmed);
      } catch {
        parsed = val;
      }
    }
  }

  // Duration object: {"value": "4", "unit": "days"}
  if (parsed && typeof parsed === "object" && !Array.isArray(parsed) && parsed.value && parsed.unit) {
    return `${parsed.value} ${parsed.unit}`;
  }

  // Array of values: ["diabetes", "hypertension"]
  if (Array.isArray(parsed)) {
    if (parsed.length === 0) return "None reported";
    return parsed
      .map(item => {
        const str = String(item).toLowerCase();
        if (str === "diabetes") return "Diabetes Mellitus";
        if (str === "hypertension") return "Hypertension (High BP)";
        if (str === "heart") return "Heart Disease";
        if (str === "asthma") return "Asthma";
        if (str === "thyroid") return "Thyroid Disorder";
        if (str === "kidney") return "Kidney Disease";
        if (str === "fever") return "Fever";
        if (str === "nausea") return "Nausea";
        if (str === "vomiting") return "Vomiting";
        if (str === "headache") return "Headache";
        if (str === "dizziness") return "Dizziness";
        if (str === "cough") return "Cough";
        if (str === "breath") return "Breathing Difficulty";
        return str.charAt(0).toUpperCase() + str.slice(1);
      })
      .join(", ");
  }

  const str = String(parsed).trim();
  const lower = str.toLowerCase();

  if (labelKey === "q_cc_severity") {
    if (lower === "1") return "Mild (Grade 1)";
    if (lower === "2") return "Moderate (Grade 2)";
    if (lower === "3") return "Severe (Grade 3)";
    if (lower === "4") return "Very Severe (Grade 4)";
  }

  if (lower === "sudden") return "Sudden onset";
  if (lower === "gradual") return "Gradual onset";
  if (lower === "never") return "Never smoker";
  if (lower === "occasional") return "Occasional use";
  if (lower === "no") return "No known allergies (NKDA)";
  if (lower === "yes") return "Yes (Confirmed)";

  return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDate(iso: string | null): string {
  if (!iso) return "Undated Record";
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", {
      year: "numeric", month: "long", day: "numeric",
    });
  } catch {
    return iso;
  }
}

export default function TimelinePage({ params }: { params: { patientId: string } }) {
  const patientId = params.patientId;
  const [events, setEvents] = useState<Event[]>([]);
  const [approvedSummary, setApprovedSummary] = useState<ApprovedSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [sourceFilter, setSourceFilter] = useState<Record<string, boolean>>({
    document: true,
    intake: true,
    voice: true,
  });

  async function loadTimeline() {
    setErr(null);
    try {
      const r = await fetch("/api/v1/timeline?patient_id=" + patientId);
      if (!r.ok) throw new Error(await r.text());
      const j = await r.json();
      setEvents(j || []);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }

  async function loadApprovedSummary() {
    setSummaryLoading(true);
    try {
      const r = await fetch("/api/v1/summary/" + patientId + "/drafts");
      if (!r.ok) {
        setApprovedSummary(null);
        return;
      }
      const list = await r.json();
      // Only select the latest draft that is explicitly APPROVED by the clinician
      const approvedMeta = (list || []).find((d: any) => d.status === "approved");
      if (approvedMeta) {
        const fullR = await fetch("/api/v1/summary/drafts/" + approvedMeta.id);
        if (fullR.ok) {
          const full = await fullR.json();
          let narrative = "";
          for (const s of full.sections || []) {
            for (const it of s.items || []) {
              if (it.text) {
                narrative = narrative ? narrative + "\n\n" + it.text : it.text;
              }
            }
          }
          setApprovedSummary({ ...full, narrative });
        } else {
          setApprovedSummary(null);
        }
      } else {
        setApprovedSummary(null);
      }
    } catch {
      setApprovedSummary(null);
    } finally {
      setSummaryLoading(false);
    }
  }

  async function loadAll() {
    await Promise.all([loadTimeline(), loadApprovedSummary()]);
  }

  async function rebuild() {
    setRebuilding(true);
    setErr(null);
    setSuccessMsg(null);
    try {
      const r = await fetch("/api/v1/timeline/build/" + patientId, { method: "POST" });
      if (!r.ok) throw new Error(await r.text());
      const data = await r.json();
      setSuccessMsg(`Timeline report successfully synchronized (${data.count} clinical records mapped).`);
      await loadAll();
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setRebuilding(false);
    }
  }

  useEffect(() => {
    loadAll();
    /* eslint-disable-next-line */
  }, [patientId]);

  const filtered = useMemo(() => {
    return events.filter(e => {
      if (sourceFilter[e.source] === false) return false;
      return true;
    });
  }, [events, sourceFilter]);

  const sourceCounts = useMemo(() => {
    const counts: Record<string, number> = { document: 0, intake: 0, voice: 0 };
    for (const e of events) {
      if (counts[e.source] !== undefined) counts[e.source] += 1;
    }
    return counts;
  }, [events]);

  // Group events by encounter date
  const grouped = useMemo(() => {
    const byDate = new Map<string, Event[]>();
    for (const e of filtered) {
      const key = e.event_date ? e.event_date.slice(0, 10) : "undated";
      if (!byDate.has(key)) byDate.set(key, []);
      byDate.get(key)!.push(e);
    }
    return Array.from(byDate.entries()).sort((a, b) => {
      if (a[0] === "undated") return 1;
      if (b[0] === "undated") return -1;
      return b[0].localeCompare(a[0]);
    });
  }, [filtered]);

  return (
    <main className="max-w-4xl mx-auto p-8 print:p-0 print:max-w-none text-slate-900 dark:text-slate-100 font-sans">
      {/* Breadcrumb Navigation - hidden on print */}
      <div className="flex items-center justify-between gap-4 text-xs mb-6 print:hidden">
        <div className="flex items-center gap-3">
          <Link href="/clinician" className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1 font-medium">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Clinician Dashboard
          </Link>
          <span className="text-slate-300 dark:text-slate-700">/</span>
          <span className="text-slate-700 dark:text-slate-300 font-medium">Timeline Clinical Report</span>
        </div>
        <div className="flex items-center gap-2">
          <Link href={"/clinician/" + patientId + "/summary"} className="text-blue-600 dark:text-blue-400 hover:underline">
            Summary Editor
          </Link>
          <span className="text-slate-300 dark:text-slate-700">•</span>
          <Link href={"/clinician/" + patientId + "/orchestrate"} className="text-indigo-600 dark:text-indigo-400 hover:underline">
            Pipeline
          </Link>
          <span className="text-slate-300 dark:text-slate-700">•</span>
          <Link href={"/intake/" + patientId + "/documents"} className="text-purple-600 dark:text-purple-400 hover:underline">
            Documents
          </Link>
        </div>
      </div>

      {/* REPORT HEADER */}
      <header className="border-b border-slate-200 dark:border-slate-800 pb-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 text-[11px] font-semibold tracking-wide uppercase mb-2">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
              Longitudinal Clinical Report
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              Patient Encounter Timeline Report
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-mono mt-1">
              Patient ID: {patientId}
            </p>
          </div>

          <div className="flex items-center gap-2 print:hidden">
            <button
              onClick={() => window.print()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
              <svg className="w-3.5 h-3.5 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="6 9 6 2 18 2 18 9" />
                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
                <rect x="6" y="14" width="12" height="8" />
              </svg>
              Print Report
            </button>
            <button
              onClick={rebuild}
              disabled={rebuilding}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 disabled:opacity-50 transition-colors shadow-sm"
            >
              {rebuilding ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-current/30 border-t-current rounded-full animate-spin" />
                  Syncing...
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
                  </svg>
                  Rebuild Timeline
                </>
              )}
            </button>
          </div>
        </div>

        {/* Report Metadata Pills */}
        <div className="mt-4 flex flex-wrap gap-2 text-xs">
          <div className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 text-slate-700 dark:text-slate-300">
            <span className="font-semibold">{events.length}</span> Total Documented Records
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800/80 border border-slate-200/80 dark:border-slate-700/80 text-slate-700 dark:text-slate-300">
            <span className="font-semibold">{grouped.length}</span> Encounter Dates Mapped
          </div>
          {approvedSummary && (
            <div className="px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5 font-medium">
              <svg className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Clinician Verified & Approved Summary (v{approvedSummary.version})
            </div>
          )}
        </div>
      </header>

      {successMsg && (
        <div className="mt-4 rounded-xl border border-emerald-200 dark:border-emerald-900 bg-emerald-50 dark:bg-emerald-950/40 p-3 text-xs text-emerald-800 dark:text-emerald-300 flex items-center justify-between">
          <span>{successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="text-emerald-700 text-sm font-bold">&times;</button>
        </div>
      )}

      {err && (
        <div className="mt-4 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 p-3 text-xs text-red-800 dark:text-red-300">
          {err}
        </div>
      )}

      {/* ---------- SECTION 1: CLINICIAN-APPROVED SUMMARY (EXECUTIVE REPORT) ---------- */}
      <section className="mt-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500 text-white flex items-center justify-center shrink-0 shadow-sm">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wide">
                  Executive Clinical Summary
                </h2>
                {approvedSummary ? (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                    APPROVED
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                    PENDING APPROVAL
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                {approvedSummary
                  ? `Formally approved by ${approvedSummary.actor || "clinician"} • Verified on ${new Date(approvedSummary.created_at).toLocaleDateString()}`
                  : "Clinical safety protocol: only clinician-approved summaries appear in this official report."}
              </p>
            </div>
          </div>

          {approvedSummary && (
            <div className="flex items-center gap-2 print:hidden">
              <a
                href={"/api/v1/summary/" + patientId + "/pdf"}
                target="_blank"
                rel="noreferrer"
                className="text-xs px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 transition-colors inline-flex items-center gap-1.5 font-medium"
              >
                Download PDF
              </a>
              <Link
                href={"/clinician/" + patientId + "/summary"}
                className="text-xs px-2.5 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 transition-colors inline-flex items-center gap-1.5 font-medium"
              >
                Edit in Summary View
              </Link>
            </div>
          )}
        </div>

        {summaryLoading ? (
          <div className="p-8 text-center text-xs text-slate-400">
            Loading executive clinical summary...
          </div>
        ) : approvedSummary ? (
          <div className="p-6">
            <div className="bg-slate-50/50 dark:bg-slate-950/40 rounded-xl p-5 border border-slate-100 dark:border-slate-800/80 font-sans text-xs text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-line space-y-4">
              {approvedSummary.narrative}
            </div>
            {approvedSummary.notes && (
              <div className="mt-3 text-[11px] text-slate-400 dark:text-slate-500 flex items-center gap-1.5 italic">
                <span>Model attribution & metadata:</span>
                <span>{approvedSummary.notes}</span>
              </div>
            )}
          </div>
        ) : (
          <div className="p-8 text-center bg-slate-50/40 dark:bg-slate-950/20">
            <div className="w-10 h-10 rounded-full bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 mx-auto flex items-center justify-center mb-2">
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">
              No clinician-approved summary on record.
            </p>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 max-w-md mx-auto">
              Per strict patient safety protocol, unreviewed AI drafts are never rendered directly in the official timeline report until approved.
            </p>
            <div className="mt-4 flex items-center justify-center gap-2 print:hidden">
              <Link
                href="/clinician/ai-review"
                className="text-xs px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-700 text-white font-medium transition-colors"
              >
                Open AI Review Queue
              </Link>
              <Link
                href={"/clinician/" + patientId + "/summary"}
                className="text-xs px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-800 transition-colors"
              >
                Review Summary Drafts
              </Link>
            </div>
          </div>
        )}
      </section>

      {/* ---------- SECTION 2: LONGITUDINAL ENCOUNTER REPORT (CHRONOLOGICAL) ---------- */}
      <section className="mt-10">
        <div className="flex items-center justify-between gap-4 mb-4 flex-wrap">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Chronological Encounter Records
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Structured clinical findings, symptoms, and documented medications ordered by date
            </p>
          </div>

          {/* Source filters - hidden on print */}
          <div className="flex items-center gap-3 print:hidden">
            <span className="text-xs text-slate-400 font-medium">Filter sources:</span>
            {(["document", "intake", "voice"] as const).map(src => (
              <label key={src} className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-300 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={sourceFilter[src]}
                  onChange={e => setSourceFilter(prev => ({ ...prev, [src]: e.target.checked }))}
                  className="rounded text-blue-600"
                />
                <span className="uppercase font-mono text-[10px] font-semibold">{src}</span>
                <span className="text-slate-400 font-mono text-[10px]">({sourceCounts[src] ?? 0})</span>
              </label>
            ))}
          </div>
        </div>

        {loading && (
          <div className="p-12 text-center text-slate-500 text-xs">
            Loading chronological encounter records...
          </div>
        )}

        {!loading && filtered.length === 0 && (
          <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 p-8 text-center text-slate-500 text-xs">
            No clinical encounter events found matching current filters.
          </div>
        )}

        {/* Encounter timeline list */}
        <div className="space-y-8 mt-6">
          {grouped.map(([date, dateEvents], idx) => {
            // Group events inside this encounter into structured clinical categories
            const intakeAnswers = dateEvents.filter(e => e.kind === "intake_answer");
            const medications = dateEvents.filter(e => e.kind === "medication");
            const otherRecords = dateEvents.filter(e => e.kind !== "intake_answer" && e.kind !== "medication");

            return (
              <article key={date} className="relative rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm overflow-hidden">
                {/* Encounter Date Header */}
                <div className="px-6 py-4 bg-slate-50/80 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between gap-4 flex-wrap">
                  <div className="flex items-center gap-3">
                    <span className="w-7 h-7 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                      {idx + 1}
                    </span>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                        {date === "undated" ? "Undated Encounter / Diagnostic Records" : formatDate(date)}
                      </h3>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                        {dateEvents.length} documented clinical finding{dateEvents.length > 1 ? "s" : ""}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 text-[10px] font-mono">
                    {dateEvents.some(e => e.source === "intake") && (
                      <span className="px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 font-semibold border border-blue-200 dark:border-blue-900">
                        PATIENT INTAKE
                      </span>
                    )}
                    {dateEvents.some(e => e.source === "document") && (
                      <span className="px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 font-semibold border border-purple-200 dark:border-purple-900">
                        CLINICAL DOCUMENT
                      </span>
                    )}
                    {dateEvents.some(e => e.source === "voice") && (
                      <span className="px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 font-semibold border border-amber-200 dark:border-amber-900">
                        VOICE TRANSCRIPT
                      </span>
                    )}
                  </div>
                </div>

                <div className="p-6 space-y-6">
                  {/* Category A: Patient Intake & Presenting History */}
                  {intakeAnswers.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-blue-500" />
                        Patient-Reported History & Symptoms
                      </h4>
                      <div className="grid sm:grid-cols-2 gap-3">
                        {intakeAnswers.map(e => (
                          <div key={e.id} className="p-3.5 rounded-xl border border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/30">
                            <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                              {humanizeLabel(e.label)}
                            </div>
                            <div className="mt-1 text-xs font-medium text-slate-900 dark:text-slate-100 leading-snug">
                              {formatValue(e.value, e.label)}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Category B: Medications & Prescriptions */}
                  {medications.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500" />
                        Documented Pharmacotherapy & Medications
                      </h4>
                      <div className="grid sm:grid-cols-2 gap-3">
                        {medications.map(e => (
                          <div key={e.id} className="p-3.5 rounded-xl border border-emerald-100 dark:border-emerald-950/60 bg-emerald-50/30 dark:bg-emerald-950/20">
                            <div className="flex items-center justify-between gap-2">
                              <span className="text-xs font-bold text-slate-900 dark:text-white">
                                {e.label}
                              </span>
                              <span className="px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 font-mono text-[10px] font-semibold">
                                {e.value || "Prescribed"}
                              </span>
                            </div>
                            {e.source_excerpt && (
                              <p className="mt-1.5 text-[11px] text-slate-500 dark:text-slate-400 italic">
                                Document excerpt: "{e.source_excerpt}"
                              </p>
                            )}
                            {e.normalized?.drug_class && (
                              <p className="mt-1 text-[11px] text-emerald-700 dark:text-emerald-400 font-medium">
                                Drug Class: {e.normalized.drug_class}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Category C: Other Document Records & Observations */}
                  {otherRecords.length > 0 && (
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-purple-500" />
                        Clinical Observations & Records
                      </h4>
                      <div className="grid sm:grid-cols-2 gap-3">
                        {otherRecords.map(e => (
                          <div key={e.id} className="p-3.5 rounded-xl border border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/30">
                            <div className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                              {humanizeLabel(e.label)}
                            </div>
                            <div className="mt-1 text-xs font-medium text-slate-900 dark:text-slate-100">
                              {formatValue(e.value, e.label)}
                            </div>
                            {e.source_excerpt && (
                              <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400 italic">
                                Source: "{e.source_excerpt}"
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </section>

      {/* Report Footer */}
      <footer className="mt-12 pt-6 border-t border-slate-200 dark:border-slate-800 text-center text-[11px] text-slate-400 dark:text-slate-500">
        MediGraph Longitudinal Clinical Record System • Local Verification Architecture • All records encrypted and localized
      </footer>
    </main>
  );
}