"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import FhirPanel from "@/components/FhirPanel";

type Item = {
  event_id: string;
  text: string;
  confidence: number;
  source: string;
  needs_review: boolean;
  verification_status: string;
  warnings: string[];
};

type Section = { key: string; title: string; items: Item[] };

type Draft = {
  patient_id: string;
  generated_at: string;
  sections: Section[];
  stats: { total_facts: number; low_confidence: number; pending_verification: number };
};

type Evidence = {
  event_id: string;
  label: string;
  value: string;
  source: string;
  confidence: number;
};

type Alert = {
  rule_id: string;
  name: string;
  severity: "urgent" | "caution" | "info";
  description: string;
  source_hint: string;
  evidence: Evidence[];
};

type SummaryResponse = {
  patient_id: string;
  draft: Draft;
  alerts: Alert[];
  events_count: number;
};

type Consent = {
  id: string;
  purpose: string;
  granted: boolean;
  granted_at: string;
  revoked_at: string | null;
};

type AuditEntry = {
  id: string;
  actor: string;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  details: Record<string, any>;
  created_at: string;
};

type AiSummary = {
  patient_id: string;
  draft_id: string;
  narrative: string;
  status: string;
  version: number;
  model_note: string;
  created_at: string;
};

const SEVERITY_STYLE: Record<string, string> = {
  urgent:  "bg-red-50 dark:bg-red-950/40 border-red-400 dark:border-red-800 text-red-900 dark:text-red-200",
  caution: "bg-amber-50 dark:bg-amber-950/40 border-amber-400 dark:border-amber-800 text-amber-900 dark:text-amber-200",
  info:    "bg-blue-50 dark:bg-blue-950/40 border-blue-400 dark:border-blue-800 text-blue-900 dark:text-blue-200",
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

function formatValue(val: any): string {
  if (!val) return "None reported";

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

  if (parsed && typeof parsed === "object" && !Array.isArray(parsed) && parsed.value && parsed.unit) {
    return `${parsed.value} ${parsed.unit}`;
  }

  if (Array.isArray(parsed)) {
    if (parsed.length === 0) return "None reported";
    return parsed
      .map(item => {
        const str = String(item).toLowerCase();
        if (str === "diabetes") return "Diabetes Mellitus";
        if (str === "hypertension") return "Hypertension";
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

  if (lower === "1") return "Mild (Grade 1)";
  if (lower === "2") return "Moderate (Grade 2)";
  if (lower === "3") return "Severe (Grade 3)";
  if (lower === "4") return "Very Severe (Grade 4)";
  if (lower === "sudden") return "Sudden onset";
  if (lower === "gradual") return "Gradual onset";
  if (lower === "never") return "Never smoker";
  if (lower === "occasional") return "Occasional use";
  if (lower === "no") return "No known allergies (NKDA)";
  if (lower === "yes") return "Yes (Confirmed)";

  return str.charAt(0).toUpperCase() + str.slice(1);
}

export default function SummaryDashboard({ params }: { params: { patientId: string } }) {
  const patientId = params.patientId;
  const [data, setData] = useState<SummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  // Active view: "note" for Clinical Note narrative, "findings" for structured categories
  const [activeTab, setActiveTab] = useState<"note" | "findings">("note");

  // Narrative clinical note state
  const [aiSummary, setAiSummary] = useState<AiSummary | null>(null);
  const [narrativeText, setNarrativeText] = useState("");
  const [isEditingNote, setIsEditingNote] = useState(false);
  const [generatingAi, setGeneratingAi] = useState(false);
  const [savingAction, setSavingAction] = useState<"save" | "approve" | null>(null);
  const [statusMsg, setStatusMsg] = useState<{ text: string; type: "ok" | "err" } | null>(null);

  // Drawers and panels
  const [showFhir, setShowFhir] = useState(false);
  const [showDrafts, setShowDrafts] = useState(false);
  const [draftsList, setDraftsList] = useState<any[]>([]);
  const [showAudit, setShowAudit] = useState(false);
  const [auditList, setAuditList] = useState<AuditEntry[]>([]);
  const [showConsents, setShowConsents] = useState(false);
  const [consentsList, setConsentsList] = useState<Consent[]>([]);

  async function loadData() {
    setErr(null);
    setLoading(true);
    try {
      const [sumRes, aiRes] = await Promise.all([
        fetch("/api/v1/summary/" + patientId),
        fetch("/api/v1/ai/patient/" + patientId + "/latest"),
      ]);

      if (!sumRes.ok) throw new Error(await sumRes.text());
      const sumJson: SummaryResponse = await sumRes.json();
      setData(sumJson);

      if (aiRes.ok) {
        const aiJson: AiSummary = await aiRes.json();
        setAiSummary(aiJson);
        setNarrativeText(aiJson.narrative || "");
      }
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
    /* eslint-disable-next-line */
  }, [patientId]);

  // Generate new AI narrative
  async function generateNote() {
    setGeneratingAi(true);
    setStatusMsg(null);
    try {
      const r = await fetch("/api/v1/summary/" + patientId + "/generate?actor=clinician", {
        method: "POST",
      });
      if (!r.ok) throw new Error(await r.text());
      const result = await r.json();
      setNarrativeText(result.narrative);
      setAiSummary({
        patient_id: patientId,
        draft_id: result.draft_id,
        narrative: result.narrative,
        status: "ai_generated",
        version: result.version,
        model_note: result.model ? `via ${result.model}` : "",
        created_at: result.generated_at,
      });
      setStatusMsg({ text: `AI clinical note generated (v${result.version}). Ready for review.`, type: "ok" });
      setIsEditingNote(true);
    } catch (e: any) {
      setStatusMsg({ text: "Generation failed: " + (e?.message ?? String(e)), type: "err" });
    } finally {
      setGeneratingAi(false);
    }
  }

  // Save or Approve the Clinical Note
  async function handleDecision(action: "approve" | "draft") {
    setSavingAction(action === "approve" ? "approve" : "save");
    setStatusMsg(null);
    try {
      if (aiSummary?.draft_id) {
        // If an AI draft exists, register the clinician decision
        const decRes = await fetch("/api/v1/ai/drafts/" + aiSummary.draft_id + "/decision", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            action: action === "approve" ? "approve" : "edit",
            edited_narrative: narrativeText,
            actor: "clinician",
          }),
        });
        if (!decRes.ok) throw new Error(await decRes.text());
      } else {
        // Otherwise save via summary endpoint
        const saveRes = await fetch("/api/v1/summary/" + patientId + "/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sections: [{
              key: "narrative",
              title: "Clinical Note",
              items: [{ event_id: "narrative", text: narrativeText, confidence: 1.0, source: "clinician" }],
            }],
            notes: action === "approve" ? "Approved by clinician" : "Working draft",
            actor: "clinician",
            status: action === "approve" ? "approved" : "draft",
          }),
        });
        if (!saveRes.ok) throw new Error(await saveRes.text());
      }

      setStatusMsg({
        text: action === "approve"
          ? "Clinical note verified and approved successfully."
          : "Working draft saved successfully.",
        type: "ok",
      });
      setIsEditingNote(false);
      await loadData();
    } catch (e: any) {
      setStatusMsg({ text: "Action failed: " + (e?.message ?? String(e)), type: "err" });
    } finally {
      setSavingAction(null);
    }
  }

  // Load versions
  async function loadVersions() {
    try {
      const r = await fetch("/api/v1/summary/" + patientId + "/drafts");
      if (!r.ok) throw new Error(await r.text());
      setDraftsList(await r.json());
      setShowDrafts(true);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    }
  }

  async function loadSpecificDraft(draftId: string) {
    try {
      const r = await fetch("/api/v1/summary/drafts/" + draftId);
      if (!r.ok) throw new Error(await r.text());
      const j = await r.json();
      let narrative = "";
      for (const s of j.sections || []) {
        for (const it of s.items || []) {
          if (it.text) narrative = narrative ? narrative + "\n\n" + it.text : it.text;
        }
      }
      setNarrativeText(narrative);
      setAiSummary({
        patient_id: patientId,
        draft_id: j.id,
        narrative,
        status: j.status,
        version: j.version,
        model_note: j.notes || "",
        created_at: j.created_at,
      });
      setShowDrafts(false);
      setStatusMsg({ text: `Loaded draft v${j.version} (${j.status}).`, type: "ok" });
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    }
  }

  // Load Audit
  async function loadAudit() {
    try {
      const r = await fetch("/api/v1/consents/audit?patient_id=" + patientId);
      if (!r.ok) throw new Error(await r.text());
      setAuditList(await r.json());
      setShowAudit(true);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    }
  }

  // Load Consent
  async function loadConsents() {
    try {
      const r = await fetch("/api/v1/consents/patient/" + patientId);
      if (!r.ok) throw new Error(await r.text());
      setConsentsList(await r.json());
      setShowConsents(true);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    }
  }

  const urgentAlerts = useMemo(
    () => (data?.alerts ?? []).filter(a => a.severity === "urgent"),
    [data]
  );
  const otherAlerts = useMemo(
    () => (data?.alerts ?? []).filter(a => a.severity !== "urgent"),
    [data]
  );

  return (
    <main className="max-w-5xl mx-auto p-8 print:p-0 font-sans text-slate-900 dark:text-slate-100">
      {/* Top Breadcrumb Navigation */}
      <div className="flex items-center justify-between gap-4 text-xs mb-6 print:hidden">
        <div className="flex items-center gap-2">
          <Link href="/clinician" className="text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white flex items-center gap-1 font-medium">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="15 18 9 12 15 6" />
            </svg>
            Clinician Dashboard
          </Link>
          <span className="text-slate-300 dark:text-slate-700">/</span>
          <span className="text-slate-700 dark:text-slate-300 font-medium">Clinical Summary</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href={"/clinician/" + patientId + "/timeline"} className="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="3 6 9 12 13 8 21 16" />
            </svg>
            Encounter Timeline Report
          </Link>
          <span className="text-slate-300 dark:text-slate-700">•</span>
          <Link href={"/clinician/" + patientId + "/orchestrate"} className="text-indigo-600 dark:text-indigo-400 hover:underline">
            Pipeline
          </Link>
        </div>
      </div>

      {/* Main Header */}
      <header className="border-b border-slate-200 dark:border-slate-800 pb-6 flex items-start justify-between gap-4 flex-wrap">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 text-[11px] font-semibold tracking-wide uppercase mb-2">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" />
            Clinical Summary & Synthesis
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Comprehensive Clinical Summary
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 font-mono mt-1">
            Patient ID: {patientId}
          </p>
        </div>

        {/* Global actions */}
        <div className="flex items-center gap-2 print:hidden flex-wrap">
          <a
            href={"/api/v1/summary/" + patientId + "/pdf"}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-sm"
          >
            <svg className="w-3.5 h-3.5 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Download PDF
          </a>
          <button
            onClick={() => setShowFhir(prev => !prev)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
          >
            FHIR Panel
          </button>
          <button
            onClick={loadVersions}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
          >
            Version History
          </button>
          <button
            onClick={loadAudit}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
          >
            Audit Log
          </button>
        </div>
      </header>

      {/* Feedback Messages */}
      {statusMsg && (
        <div className={`mt-4 rounded-xl p-3.5 text-xs flex items-center justify-between border ${
          statusMsg.type === "ok"
            ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900 text-emerald-800 dark:text-emerald-300"
            : "bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-900 text-red-800 dark:text-red-300"
        }`}>
          <span>{statusMsg.text}</span>
          <button onClick={() => setStatusMsg(null)} className="text-sm font-bold opacity-60 hover:opacity-100">&times;</button>
        </div>
      )}

      {err && (
        <div className="mt-4 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 p-3.5 text-xs text-red-800 dark:text-red-300">
          {err}
        </div>
      )}

      {/* Safety Alerts Banner (if present) */}
      {urgentAlerts.length > 0 && (
        <div className="mt-6 space-y-3">
          {urgentAlerts.map(a => (
            <div key={a.rule_id} className={`border-l-4 rounded-xl p-4 shadow-sm ${SEVERITY_STYLE[a.severity]}`}>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wide px-2 py-0.5 rounded bg-red-100 dark:bg-red-900/60 text-red-800 dark:text-red-200">
                  URGENT CLINICAL ALERT
                </span>
                <span className="font-semibold text-sm">{a.name}</span>
              </div>
              <p className="text-xs mt-1.5 leading-relaxed">{a.description}</p>
              {a.evidence && a.evidence.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {a.evidence.map(ev => (
                    <span key={ev.event_id} className="text-[11px] px-2 py-0.5 rounded bg-white dark:bg-slate-900 border text-slate-700 dark:text-slate-300">
                      {ev.label}: {String(ev.value)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {otherAlerts.length > 0 && (
        <div className="mt-4 space-y-2">
          {otherAlerts.map(a => (
            <div key={a.rule_id} className={`border-l-4 rounded-lg p-3 text-xs ${SEVERITY_STYLE[a.severity]}`}>
              <span className="font-bold uppercase tracking-wide mr-2">{a.severity}:</span>
              <span className="font-medium">{a.name}</span> — <span>{a.description}</span>
            </div>
          ))}
        </div>
      )}

      {/* FHIR Panel Collapsible */}
      {showFhir && (
        <div className="mt-6 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-4">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">FHIR Resource Generation</h3>
            <button onClick={() => setShowFhir(false)} className="text-xs text-slate-400 hover:text-slate-600">Close</button>
          </div>
          <FhirPanel patientId={patientId} />
        </div>
      )}

      {/* NAVIGATION TABS: Executive Note vs Structured Findings */}
      <div className="mt-8 flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-px flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab("note")}
            className={`px-4 py-2.5 text-xs font-semibold rounded-t-lg border-b-2 transition-all flex items-center gap-2 ${
              activeTab === "note"
                ? "border-purple-600 text-purple-600 dark:text-purple-400 bg-purple-50/50 dark:bg-purple-950/20"
                : "border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            Executive Clinical Note
            {aiSummary?.status === "approved" && (
              <span className="w-2 h-2 rounded-full bg-emerald-500" title="Approved" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("findings")}
            className={`px-4 py-2.5 text-xs font-semibold rounded-t-lg border-b-2 transition-all flex items-center gap-2 ${
              activeTab === "findings"
                ? "border-blue-600 text-blue-600 dark:text-blue-400 bg-blue-50/50 dark:bg-blue-950/20"
                : "border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="7" height="7" />
              <rect x="14" y="3" width="7" height="7" />
              <rect x="14" y="14" width="7" height="7" />
              <rect x="3" y="14" width="7" height="7" />
            </svg>
            Structured Clinical Findings
            <span className="px-1.5 py-0.2 rounded-full bg-slate-100 dark:bg-slate-800 text-[10px] text-slate-600 dark:text-slate-300">
              {data?.events_count ?? 0}
            </span>
          </button>
        </div>

        {activeTab === "note" && (
          <div className="flex items-center gap-2 print:hidden mb-2">
            {!isEditingNote && narrativeText && (
              <button
                onClick={() => setIsEditingNote(true)}
                className="text-xs px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
              >
                Edit Note
              </button>
            )}
            <button
              onClick={generateNote}
              disabled={generatingAi}
              className="text-xs px-3 py-1.5 rounded-lg border border-purple-200 dark:border-purple-800 text-purple-700 dark:text-purple-300 hover:bg-purple-50 dark:hover:bg-purple-950/40 transition-colors flex items-center gap-1.5 font-medium disabled:opacity-50"
            >
              {generatingAi ? (
                <>
                  <span className="w-3 h-3 border-2 border-purple-600/30 border-t-purple-600 rounded-full animate-spin" />
                  Synthesizing with AI...
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5 text-purple-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2l1.8 5.6L19.4 9l-4.6 3.7L16 18.4 12 15l-4 3.4 1.2-5.7L4.6 9l5.6-1.4z" />
                  </svg>
                  Regenerate with AI
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* TAB 1: EXECUTIVE CLINICAL NOTE */}
      {activeTab === "note" && (
        <div className="mt-6">
          <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm overflow-hidden">
            {/* Note Status Header */}
            <div className="p-4 bg-slate-50/70 dark:bg-slate-800/40 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between gap-4 flex-wrap">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                  aiSummary?.status === "approved"
                    ? "bg-emerald-500 text-white"
                    : "bg-purple-500 text-white"
                }`}>
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    {aiSummary?.status === "approved" ? (
                      <polyline points="20 6 9 17 4 12" />
                    ) : (
                      <path d="M12 2l1.8 5.6L19.4 9l-4.6 3.7L16 18.4 12 15l-4 3.4 1.2-5.7L4.6 9l5.6-1.4z" />
                    )}
                  </svg>
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                      Clinical Note Document
                    </span>
                    {aiSummary?.status === "approved" ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                        CLINICIAN APPROVED (v{aiSummary.version})
                      </span>
                    ) : aiSummary ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-300 border border-purple-300 dark:border-purple-800">
                        PENDING CLINICIAN APPROVAL (v{aiSummary.version})
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                        NOT GENERATED
                      </span>
                    )}
                  </div>
                  {aiSummary && (
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                      Last modified on {new Date(aiSummary.created_at).toLocaleDateString()}
                      {aiSummary.model_note && ` • ${aiSummary.model_note}`}
                    </p>
                  )}
                </div>
              </div>

              {/* Sign-off & save controls */}
              <div className="flex items-center gap-2 print:hidden">
                {isEditingNote && (
                  <button
                    onClick={() => handleDecision("draft")}
                    disabled={savingAction !== null}
                    className="text-xs px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 transition-colors font-medium disabled:opacity-50"
                  >
                    {savingAction === "save" ? "Saving..." : "Save Draft"}
                  </button>
                )}
                <button
                  onClick={() => handleDecision("approve")}
                  disabled={savingAction !== null || !narrativeText.trim()}
                  className="text-xs px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold transition-colors shadow-sm disabled:opacity-50 flex items-center gap-1.5"
                >
                  {savingAction === "approve" ? (
                    <>
                      <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Signing...
                    </>
                  ) : (
                    <>
                      <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      Approve & Sign Note
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Note Content Area */}
            <div className="p-6">
              {loading ? (
                <div className="py-12 text-center text-xs text-slate-400">
                  Loading clinical note...
                </div>
              ) : isEditingNote ? (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
                    Editing Clinical Narrative (Markdown / Text):
                  </label>
                  <textarea
                    value={narrativeText}
                    onChange={e => setNarrativeText(e.target.value)}
                    rows={16}
                    className="w-full text-xs font-mono leading-relaxed p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-950/40 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-y"
                    placeholder="Enter or edit clinical narrative..."
                  />
                  <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
                    <span>You can edit directly before signing. All changes are versioned.</span>
                    <button
                      onClick={() => setIsEditingNote(false)}
                      className="text-blue-600 hover:underline"
                    >
                      Exit edit mode
                    </button>
                  </div>
                </div>
              ) : narrativeText ? (
                <div className="p-6 rounded-xl bg-slate-50/50 dark:bg-slate-950/40 border border-slate-100 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-sans whitespace-pre-line space-y-4">
                  {narrativeText}
                </div>
              ) : (
                <div className="py-12 text-center bg-slate-50/30 dark:bg-slate-950/20 rounded-xl">
                  <div className="w-10 h-10 rounded-full bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 mx-auto flex items-center justify-center mb-3">
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M12 2l1.8 5.6L19.4 9l-4.6 3.7L16 18.4 12 15l-4 3.4 1.2-5.7L4.6 9l5.6-1.4z" />
                    </svg>
                  </div>
                  <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">
                    No clinical note generated yet for this patient.
                  </p>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1 max-w-sm mx-auto">
                    Click "Regenerate with AI" to synthesize intake answers and documents into a structured clinical note.
                  </p>
                  <button
                    onClick={generateNote}
                    disabled={generatingAi}
                    className="mt-4 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold transition-colors shadow-sm"
                  >
                    Generate Clinical Note
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: STRUCTURED CLINICAL FINDINGS */}
      {activeTab === "findings" && (
        <div className="mt-6 space-y-6">
          {data?.draft?.sections && data.draft.sections.length > 0 ? (
            data.draft.sections.map(sec => (
              <section key={sec.key} className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm overflow-hidden">
                <div className="px-5 py-3.5 bg-slate-50/80 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-500" />
                    {sec.title}
                  </h3>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {sec.items.length} recorded item{sec.items.length > 1 ? "s" : ""}
                  </span>
                </div>
                <div className="p-5 grid sm:grid-cols-2 gap-3">
                  {sec.items.map(it => (
                    <div key={it.event_id} className="p-3.5 rounded-xl border border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/30">
                      <div className="text-xs font-medium text-slate-900 dark:text-slate-100 leading-snug">
                        {formatValue(it.text)}
                      </div>
                      <div className="mt-2 flex items-center gap-2 text-[10px]">
                        <span className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-mono uppercase">
                          {it.source}
                        </span>
                        {it.verification_status === "verified" && (
                          <span className="text-emerald-600 font-medium">Verified</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            ))
          ) : (
            <div className="p-8 text-center text-slate-400 text-xs">
              No structured findings documented.
            </div>
          )}
        </div>
      )}

      {/* VERSION HISTORY DRAWER / MODAL */}
      {showDrafts && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">Summary Version History</h3>
              <button onClick={() => setShowDrafts(false)} className="text-sm font-bold text-slate-400 hover:text-slate-600">&times;</button>
            </div>
            <div className="mt-4 flex-1 overflow-y-auto space-y-2.5">
              {draftsList.length === 0 ? (
                <p className="text-xs text-slate-500 py-6 text-center">No past drafts recorded.</p>
              ) : (
                draftsList.map(d => (
                  <div key={d.id} className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 flex items-center justify-between gap-3 text-xs">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900 dark:text-white">Version {d.version}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                          d.status === "approved"
                            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                            : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400"
                        }`}>
                          {d.status}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-1">
                        {new Date(d.created_at).toLocaleString()} by {d.actor}
                      </div>
                      {d.notes && <div className="text-[11px] text-slate-400 italic mt-0.5">{d.notes}</div>}
                    </div>
                    <button
                      onClick={() => loadSpecificDraft(d.id)}
                      className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 dark:bg-blue-950 dark:text-blue-300 transition-colors"
                    >
                      Load
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* AUDIT LOG MODAL */}
      {showAudit && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">Audit Trail</h3>
              <button onClick={() => setShowAudit(false)} className="text-sm font-bold text-slate-400 hover:text-slate-600">&times;</button>
            </div>
            <div className="mt-4 flex-1 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800 text-xs">
              {auditList.length === 0 ? (
                <p className="text-xs text-slate-500 py-6 text-center">No audit log entries recorded.</p>
              ) : (
                auditList.map(a => (
                  <div key={a.id} className="py-2.5">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-medium text-slate-800 dark:text-slate-200">{a.action}</span>
                      <span className="text-[10px] text-slate-400">{new Date(a.created_at).toLocaleString()}</span>
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5">
                      Actor: {a.actor} {a.resource_type ? `• ${a.resource_type}` : ""}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      <footer className="mt-12 pt-6 border-t border-slate-200 dark:border-slate-800 text-center text-[11px] text-slate-400 dark:text-slate-500">
        MediGraph Clinical Record System • HIPAA / GDPR Compliant Local Processing
      </footer>
    </main>
  );
}