from pathlib import Path

tsx = r"""
"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

type AiDraft = {
  draft_id: string;
  patient_id: string;
  synthetic_id: string;
  version: number;
  status: string;
  actor: string;
  model_note: string;
  generated_at: string;
  preview: string;
};

type Grouped = {
  patient_id: string;
  synthetic_id: string;
  drafts: AiDraft[];      // newest first
  latest: AiDraft;
};

export default function AiReviewPage() {
  const [drafts, setDrafts] = useState<AiDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [showHistory, setShowHistory] = useState<Record<string, boolean>>({});
  const [filter, setFilter] = useState<"pending" | "all">("pending");

  async function load() {
    setErr(null);
    setLoading(true);
    try {
      const r = await fetch("/api/v1/ai/queue");
      if (!r.ok) throw new Error(await r.text());
      setDrafts(await r.json());
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }

  async function decide(draftId: string, action: "approve" | "reject") {
    setBusyId(draftId);
    try {
      const r = await fetch("/api/v1/ai/drafts/" + draftId + "/decision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, actor: "clinician" }),
      });
      if (!r.ok) throw new Error(await r.text());
      setDrafts(prev => prev.filter(d => d.draft_id !== draftId));
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setBusyId(null);
    }
  }

  useEffect(() => { load(); }, []);

  // Group drafts by patient, keep all versions per patient
  const groups: Grouped[] = useMemo(() => {
    const byPatient: Record<string, AiDraft[]> = {};
    for (const d of drafts) {
      if (!byPatient[d.patient_id]) byPatient[d.patient_id] = [];
      byPatient[d.patient_id].push(d);
    }
    const arr: Grouped[] = Object.entries(byPatient).map(([pid, list]) => {
      list.sort((a, b) => b.version - a.version);   // newest first
      return {
        patient_id: pid,
        synthetic_id: list[0].synthetic_id,
        drafts: list,
        latest: list[0],
      };
    });
    // Sort patients by most recent activity
    arr.sort((a, b) => {
      const da = new Date(a.latest.generated_at).getTime();
      const db = new Date(b.latest.generated_at).getTime();
      return db - da;
    });
    return arr;
  }, [drafts]);

  const pendingCount = groups.filter(g => g.latest.status === "ai_generated").length;
  const approvedCount = groups.filter(g => g.latest.status === "approved").length;
  const totalVersions = drafts.length;

  const filtered = useMemo(() => {
    if (filter === "all") return groups;
    return groups.filter(g => g.latest.status === "ai_generated");
  }, [groups, filter]);

  function toggleExpand(pid: string) {
    setExpanded(prev => ({ ...prev, [pid]: !prev[pid] }));
  }

  function toggleHistory(pid: string) {
    setShowHistory(prev => ({ ...prev, [pid]: !prev[pid] }));
  }

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-[#070b18]">
      <div className="max-w-5xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
          <Link href="/clinician" className="hover:text-slate-900 dark:hover:text-white">Dashboard</Link>
          <span className="opacity-50">/</span>
          <span className="text-slate-900 dark:text-white font-medium">AI summary review</span>
        </div>

        <header className="mt-6 flex items-start justify-between gap-6 flex-wrap">
          <div>
            <h1 className="text-3xl font-semibold text-slate-900 dark:text-white tracking-tight">
              AI summary review
            </h1>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400 max-w-2xl leading-relaxed">
              AI-generated clinical notes awaiting physician sign-off. Each note is produced locally
              from the patient's intake responses and uploaded documents.
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-200 dark:border-emerald-900 bg-emerald-50 dark:bg-emerald-950/40 text-xs font-medium text-emerald-700 dark:text-emerald-300 whitespace-nowrap">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            Local processing
          </div>
        </header>

        {/* Stats + filters */}
        <div className="mt-6 flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setFilter("pending")}
              className={
                "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors " +
                (filter === "pending"
                  ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900"
                  : "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:border-slate-300")
              }>
              Pending review ({pendingCount})
            </button>
            <button
              onClick={() => setFilter("all")}
              className={
                "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors " +
                (filter === "all"
                  ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900"
                  : "bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:border-slate-300")
              }>
              All ({groups.length})
            </button>
          </div>

          <div className="ml-auto flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
            <span>{groups.length} patient{groups.length === 1 ? "" : "s"}</span>
            <span className="opacity-30">-</span>
            <span>{totalVersions} version{totalVersions === 1 ? "" : "s"}</span>
            <span className="opacity-30">-</span>
            <span className="text-emerald-600 dark:text-emerald-400">{approvedCount} approved</span>
          </div>

          <button onClick={load}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 hover:border-slate-300 transition-colors">
            Refresh
          </button>
        </div>

        {err && (
          <div className="mt-6 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-sm text-red-800 dark:text-red-300">
            {err}
          </div>
        )}
        {loading && (
          <div className="mt-10 flex items-center justify-center gap-3 text-slate-500 dark:text-slate-400 text-sm">
            <span className="w-4 h-4 rounded-full border-2 border-slate-300 border-t-blue-500 animate-spin" />
            Loading queue...
          </div>
        )}

        {!loading && filtered.length === 0 && (
          <div className="mt-10 rounded-2xl border border-emerald-200 dark:border-emerald-900 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/30 p-8 text-center">
            <div className="w-12 h-12 mx-auto rounded-full bg-emerald-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/30">
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <p className="mt-4 text-base font-semibold text-emerald-900 dark:text-emerald-200">
              {filter === "pending" ? "No summaries awaiting review" : "No summaries yet"}
            </p>
            <p className="mt-1 text-sm text-emerald-800/80 dark:text-emerald-300/80">
              {filter === "pending"
                ? "All AI-generated summaries have been reviewed."
                : "Generate a summary from the patient intake page."}
            </p>
          </div>
        )}

        {/* Patient groups */}
        <div className="mt-6 space-y-4">
          {filtered.map(g => {
            const isExpanded = expanded[g.patient_id];
            const showHist = showHistory[g.patient_id];
            const busy = busyId === g.latest.draft_id;
            const isApproved = g.latest.status === "approved";
            const isEdited = g.latest.status === "edited";

            return (
              <article key={g.patient_id}
                       className={
                         "rounded-2xl border bg-white dark:bg-slate-900 overflow-hidden transition-colors " +
                         (isApproved
                           ? "border-emerald-200 dark:border-emerald-900"
                           : isEdited
                           ? "border-amber-200 dark:border-amber-900"
                           : "border-slate-200 dark:border-slate-800")
                       }>
                {/* Top accent */}
                <div className={
                  "h-1 " +
                  (isApproved
                    ? "bg-gradient-to-r from-emerald-400 to-teal-500"
                    : isEdited
                    ? "bg-gradient-to-r from-amber-400 to-orange-500"
                    : "bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500")
                } />

                {/* Header */}
                <header className="flex items-start justify-between gap-4 p-5">
                  <div className="flex items-start gap-4 min-w-0 flex-1">
                    <div className={
                      "w-12 h-12 rounded-xl flex items-center justify-center text-white text-sm font-bold shrink-0 shadow-md " +
                      (isApproved
                        ? "bg-gradient-to-br from-emerald-500 to-teal-600"
                        : "bg-gradient-to-br from-blue-500 to-indigo-600")
                    }>
                      {g.synthetic_id.slice(-2)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-base font-semibold text-slate-900 dark:text-white">
                          {g.synthetic_id}
                        </span>
                        <StatusPill status={g.latest.status} />
                        <span className="text-[10px] px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-mono">
                          v{g.latest.version}
                        </span>
                        {g.drafts.length > 1 && (
                          <button
                            onClick={() => toggleHistory(g.patient_id)}
                            className="text-[10px] font-medium text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
                          >
                            {showHist ? "hide" : g.drafts.length - 1} older version{g.drafts.length > 2 ? "s" : ""}
                          </button>
                        )}
                      </div>
                      <div className="mt-1 text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-2 flex-wrap">
                        <span>{new Date(g.latest.generated_at).toLocaleString()}</span>
                        <span className="opacity-40">-</span>
                        <span className="font-mono">{g.latest.model_note}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <Link
                      href={"/clinician/" + g.patient_id + "/summary"}
                      className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                      <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                        <polyline points="15 3 21 3 21 9" />
                        <line x1="10" y1="14" x2="21" y2="3" />
                      </svg>
                      Open patient
                    </Link>
                    {!isApproved && (
                      <>
                        <button
                          onClick={() => decide(g.latest.draft_id, "approve")}
                          disabled={busy}
                          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700 disabled:opacity-50 transition-colors shadow-sm">
                          {busy ? (
                            <span className="w-3 h-3 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                          ) : (
                            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="20 6 9 17 4 12" />
                            </svg>
                          )}
                          Approve
                        </button>
                        <button
                          onClick={() => decide(g.latest.draft_id, "reject")}
                          disabled={busy}
                          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 text-xs font-medium hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-50 transition-colors">
                          Reject
                        </button>
                      </>
                    )}
                    {isApproved && (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 text-xs font-semibold border border-emerald-200 dark:border-emerald-900">
                        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                        Approved
                      </span>
                    )}
                  </div>
                </header>

                {/* Preview */}
                <div className="px-5 pb-4">
                  <div className={
                    "relative rounded-xl border px-5 py-4 text-sm text-slate-700 dark:text-slate-300 leading-relaxed " +
                    (isApproved
                      ? "border-emerald-100 dark:border-emerald-900/50 bg-emerald-50/40 dark:bg-emerald-950/20"
                      : "border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-950/40")
                  }>
                    <div className={
                      "text-[10px] uppercase tracking-widest font-semibold mb-2 " +
                      (isApproved ? "text-emerald-700 dark:text-emerald-400" : "text-slate-500 dark:text-slate-400")
                    }>
                      Latest version preview
                    </div>
                    <pre className={
                      "whitespace-pre-wrap font-sans text-sm " +
                      (isExpanded ? "" : "line-clamp-4 max-h-24 overflow-hidden")
                    }>
                      {g.latest.preview}
                    </pre>
                    {g.latest.preview.length > 200 && (
                      <button
                        onClick={() => toggleExpand(g.patient_id)}
                        className="mt-2 text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline">
                        {isExpanded ? "Show less" : "Show full text"}
                      </button>
                    )}
                  </div>
                </div>

                {/* History of older versions */}
                {showHist && g.drafts.length > 1 && (
                  <div className="border-t border-slate-100 dark:border-slate-800 px-5 py-4 bg-slate-50/40 dark:bg-slate-950/30">
                    <div className="text-[10px] uppercase tracking-widest font-semibold text-slate-500 dark:text-slate-400 mb-3">
                      Older versions ({g.drafts.length - 1})
                    </div>
                    <ul className="space-y-3">
                      {g.drafts.slice(1).map(d => (
                        <li key={d.draft_id} className="flex items-start gap-3">
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700 shrink-0 mt-0.5">
                            v{d.version}
                          </span>
                          <div className="min-w-0 flex-1">
                            <div className="text-[11px] text-slate-500 dark:text-slate-400">
                              {new Date(d.generated_at).toLocaleString()}
                              <span className="opacity-50 mx-1.5">-</span>
                              <span className="font-mono">{d.model_note}</span>
                            </div>
                            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">
                              {d.preview.slice(0, 200)}
                            </p>
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </article>
            );
          })}
        </div>

        {/* Info footer */}
        {filtered.length > 0 && (
          <div className="mt-8 text-center text-xs text-slate-400 dark:text-slate-500">
            {filtered.length} patient{filtered.length === 1 ? "" : "s"} in queue
            {filter === "pending" && approvedCount > 0 && (
              <> - {approvedCount} already approved</>
            )}
          </div>
        )}
      </div>

      <style jsx>{`
        :global(.line-clamp-4) {
          display: -webkit-box;
          -webkit-line-clamp: 4;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        :global(.line-clamp-2) {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </main>
  );
}

/* ---------- helper components ---------- */

function StatusPill({ status }: { status: string }) {
  if (status === "approved") {
    return (
      <span className="text-[10px] px-2 py-0.5 rounded-md bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-semibold uppercase tracking-wider">
        Approved
      </span>
    );
  }
  if (status === "edited") {
    return (
      <span className="text-[10px] px-2 py-0.5 rounded-md bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 font-semibold uppercase tracking-wider">
        Edited
      </span>
    );
  }
  if (status === "rejected") {
    return (
      <span className="text-[10px] px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
        Rejected
      </span>
    );
  }
  return (
    <span className="text-[10px] px-2 py-0.5 rounded-md bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 font-semibold uppercase tracking-wider">
      Pending
    </span>
  );
}
"""

out = Path("src/app/clinician/ai-review/page.tsx")
out.write_text(tsx.lstrip(), encoding="utf-8")
print("WROTE", out)
print("bytes:", out.stat().st_size)

raw = out.read_text(encoding="utf-8")
non_ascii = [c for c in raw if ord(c) > 127]
print("non-ASCII chars:", len(non_ascii))
