"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

type PatientStats = {
  id: string;
  synthetic_id: string;
  preferred_language: string;
  created_at: string;
  stats: {
    sessions: number;
    answers: number;
    documents: number;
    facts: number;
    timeline_events: number;
    needs_review: number;
    verified: number;
  };
};

type AiDraft = {
  draft_id: string;
  patient_id: string;
  synthetic_id: string;
  version: number;
  status: string;
  generated_at: string;
};

type AuditEntry = {
  id: string;
  actor: string;
  action: string;
  patient_id: string | null;
  resource_type: string | null;
  resource_id: string | null;
  details: Record<string, any>;
  created_at: string;
};

export default function ClinicianDashboard() {
  const [patients, setPatients] = useState<PatientStats[]>([]);
  const [aiQueue, setAiQueue] = useState<AiDraft[]>([]);
  const [audit, setAudit] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "attention" | "recent">("all");

  useEffect(() => {
    (async () => {
      try {
        const [p, a, l] = await Promise.all([
          fetch("/api/v1/patients/stats").then(r => r.ok ? r.json() : []),
          fetch("/api/v1/ai/queue").then(r => r.ok ? r.json() : []),
          fetch("/api/v1/consents/audit?limit=8").then(r => r.ok ? r.json() : []),
        ]);
        setPatients(p);
        setAiQueue(a);
        setAudit(l);
      } catch (e: any) {
        setErr(e?.message ?? String(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // -------- derived metrics --------
  const totals = useMemo(() => {
    return patients.reduce(
      (acc, p) => ({
        patients: acc.patients + 1,
        documents: acc.documents + p.stats.documents,
        facts: acc.facts + p.stats.facts,
        needs_review: acc.needs_review + p.stats.needs_review,
        verified: acc.verified + p.stats.verified,
      }),
      { patients: 0, documents: 0, facts: 0, needs_review: 0, verified: 0 }
    );
  }, [patients]);

  const pendingAi = aiQueue.filter(d => d.status === "ai_generated");

  // Patients who have work waiting: AI draft awaiting approval
  const patientsNeedingAttention = useMemo(() => {
    const withPendingAi = new Set(pendingAi.map(d => d.patient_id));
    return patients.filter(p => withPendingAi.has(p.id));
  }, [patients, pendingAi]);

  const filteredPatients = useMemo(() => {
    let list = patients;

    if (filter === "attention") {
      list = patientsNeedingAttention;
    } else if (filter === "recent") {
      const cutoff = Date.now() - 1000 * 60 * 60 * 24 * 7; // 7 days
      list = patients.filter(p => new Date(p.created_at).getTime() > cutoff);
    }

    const q = search.trim().toLowerCase();
    if (q) {
      list = list.filter(p =>
        p.synthetic_id.toLowerCase().includes(q) ||
        p.id.toLowerCase().includes(q)
      );
    }

    return list;
  }, [patients, patientsNeedingAttention, filter, search]);

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-[#070b18]">
      <div className="max-w-6xl mx-auto px-6 py-10">
        {/* Header */}
        <nav className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
          <Link href="/" className="hover:text-slate-900 dark:hover:text-white">Home</Link>
          <span className="opacity-50">/</span>
          <span className="text-slate-900 dark:text-white font-medium">Clinician dashboard</span>
        </nav>

        <header className="mt-6 flex items-start justify-between gap-6 flex-wrap">
          <div>
            <h1 className="text-3xl font-semibold text-slate-900 dark:text-white tracking-tight">
              Clinician dashboard
            </h1>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400 max-w-2xl leading-relaxed">
              Review AI-generated summaries, track clinical records, and access patient
              timelines. Everything is processed locally and requires your approval
              before clinical use.
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full border border-emerald-200 dark:border-emerald-900 bg-emerald-50 dark:bg-emerald-950/40 text-xs font-medium text-emerald-700 dark:text-emerald-300 whitespace-nowrap">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Local processing
          </div>
        </header>

        {err && (
          <div className="mt-6 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-sm text-red-800 dark:text-red-300">
            {err}
          </div>
        )}

        {/* ---------- Metric cards ---------- */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            label="Patients"
            value={totals.patients}
            icon={<IconUsers />}
            accent="blue"
            sub={`${patientsNeedingAttention.length} need attention`}
            highlight={patientsNeedingAttention.length > 0}
          />
          <MetricCard
            label="AI summaries pending"
            value={pendingAi.length}
            icon={<IconSparkle />}
            accent="purple"
            sub={pendingAi.length > 0 ? "Awaiting your review" : "All reviewed"}
            href="/clinician/ai-review"
            highlight={pendingAi.length > 0}
          />
          <MetricCard
            label="Documents processed"
            value={totals.documents}
            icon={<IconDoc />}
            accent="indigo"
            sub="Parsed & indexed"
          />
        </div>

        {/* ---------- Priority queue ---------- */}
        {patientsNeedingAttention.length > 0 && (
          <section className="mt-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                  Needs your attention
                </h2>
                <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 font-medium">
                  {patientsNeedingAttention.length}
                </span>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-3">
              {patientsNeedingAttention.slice(0, 6).map(p => {
                const draft = pendingAi.find(d => d.patient_id === p.id);
                return (
                  <Link
                    key={p.id}
                    href="/clinician/ai-review"
                    className="group rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 hover:border-purple-300 dark:hover:border-purple-700 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 text-white flex items-center justify-center text-sm font-bold shrink-0">
                          {p.synthetic_id.slice(-2)}
                        </div>
                        <div className="min-w-0">
                          <div className="text-sm font-semibold text-slate-900 dark:text-white truncate">
                            {p.synthetic_id}
                          </div>
                          <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                            {draft
                              ? `AI summary v${draft.version} awaiting review`
                              : `AI summary awaiting review`}
                          </div>
                        </div>
                      </div>
                      <svg className="w-4 h-4 text-slate-400 group-hover:text-purple-600 dark:group-hover:text-purple-400 group-hover:translate-x-0.5 transition-all shrink-0 mt-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="5" y1="12" x2="19" y2="12" />
                        <polyline points="12 5 19 12 12 19" />
                      </svg>
                    </div>
                  </Link>
                );
              })}
            </div>

            {patientsNeedingAttention.length > 6 && (
              <Link
                href="/clinician/ai-review"
                className="mt-3 inline-flex items-center gap-1.5 text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
              >
                View all {patientsNeedingAttention.length} patients
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </Link>
            )}
          </section>
        )}

        {/* ---------- All patients ---------- */}
        <section className="mt-10">
          <div className="flex items-center justify-between gap-4 flex-wrap mb-4">
            <div className="flex items-center gap-2">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                Patients
              </h2>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium">
                {filteredPatients.length}
              </span>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <div className="relative">
                <svg className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <input
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  placeholder="Search patients..."
                  className="pl-8 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-blue-500 w-48"
                />
              </div>

              <div className="flex items-center gap-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-0.5">
                {(["all", "attention", "recent"] as const).map(f => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={
                      "px-2.5 py-1 text-xs font-medium rounded-md transition-colors " +
                      (filter === f
                        ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900"
                        : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800")
                    }
                  >
                    {f === "all" ? "All" : f === "attention" ? "Attention" : "This week"}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {loading && (
            <div className="flex items-center justify-center gap-3 text-slate-500 dark:text-slate-400 text-sm py-12">
              <span className="w-4 h-4 rounded-full border-2 border-slate-300 border-t-blue-500 animate-spin" />
              Loading patients...
            </div>
          )}

          {!loading && filteredPatients.length === 0 && (
            <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-10 text-center">
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {search ? "No patients match your search." : "No patients yet."}
              </p>
            </div>
          )}

          <div className="space-y-2">
            {filteredPatients.map(p => {
              const hasPendingAi = pendingAi.some(d => d.patient_id === p.id);
              const attention = p.stats.needs_review > 0 || hasPendingAi;
              return (
                <article
                  key={p.id}
                  className={
                    "rounded-2xl border bg-white dark:bg-slate-900 overflow-hidden transition-colors " +
                    (attention
                      ? "border-amber-200 dark:border-amber-900"
                      : "border-slate-200 dark:border-slate-800")
                  }
                >
                  <div className="p-4 flex items-center gap-4">
                    {/* Avatar */}
                    <div
                      className={
                        "w-11 h-11 rounded-xl text-white flex items-center justify-center text-sm font-bold shrink-0 shadow-sm " +
                        (attention
                          ? "bg-gradient-to-br from-amber-500 to-orange-500"
                          : "bg-gradient-to-br from-blue-500 to-indigo-600")
                      }
                    >
                      {p.synthetic_id.slice(-2)}
                    </div>

                    {/* Name + meta */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-semibold text-slate-900 dark:text-white">
                          {p.synthetic_id}
                        </span>
                        <span className="text-[10px] uppercase tracking-widest font-mono px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
                          {p.preferred_language}
                        </span>
                        {attention && (
                          <span className="text-[10px] font-semibold uppercase tracking-widest px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300">
                            Needs review
                          </span>
                        )}
                        {hasPendingAi && (
                          <span className="text-[10px] font-semibold uppercase tracking-widest px-1.5 py-0.5 rounded bg-purple-100 dark:bg-purple-950/60 text-purple-800 dark:text-purple-300">
                            AI draft
                          </span>
                        )}
                      </div>
                      <div className="mt-1.5 flex items-center gap-3 text-[11px] text-slate-500 dark:text-slate-400">
                        <span className="font-mono">ID {p.id.slice(0, 8)}</span>
                        <span className="opacity-40">-</span>
                        <span>Created {new Date(p.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    {/* Stats chips */}
                    <div className="hidden md:flex items-center gap-1.5 shrink-0">
                      <StatChip label="docs" value={p.stats.documents} />
                      <StatChip label="events" value={p.stats.timeline_events} />
                      {p.stats.needs_review > 0 && (
                        <StatChip label="review" value={p.stats.needs_review} variant="warn" />
                      )}
                      {p.stats.verified > 0 && (
                        <StatChip label="verified" value={p.stats.verified} variant="ok" />
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-1.5 shrink-0">
                      <IconLink href={"/clinician/" + p.id + "/timeline"} title="Timeline">
                        <IconChart />
                      </IconLink>
                      <IconLink href={"/clinician/" + p.id + "/summary"} title="Summary">
                        <IconNote />
                      </IconLink>
                      <IconLink href={"/clinician/" + p.id + "/orchestrate"} title="Pipeline">
                        <IconGit />
                      </IconLink>
                      <IconLink href={"/intake/" + p.id + "/documents"} title="Documents">
                        <IconDoc />
                      </IconLink>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        </section>

        {/* ---------- Recent activity ---------- */}
        {audit.length > 0 && (
          <section className="mt-10">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                Recent activity
              </h2>
              <Link href="/admin/audit" className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline">
                View full audit log
              </Link>
            </div>

            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800 overflow-hidden">
              {audit.map(a => (
                <div key={a.id} className="px-5 py-3 flex items-center gap-3 text-xs">
                  <ActionIcon action={a.action} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-slate-800 dark:text-slate-200">{a.action}</span>
                      <span className="text-slate-400">by</span>
                      <span className="text-slate-600 dark:text-slate-400 truncate max-w-[180px]">{a.actor}</span>
                    </div>
                  </div>
                  <span className="text-[10px] text-slate-400 whitespace-nowrap">
                    {new Date(a.created_at).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ---------- Bottom card: AI summary queue ---------- */}
        <div className="mt-10">
          <QueueCard
            href="/clinician/ai-review"
            title="AI summary review queue"
            description="Approve, edit, or reject AI-generated clinical notes before they reach the patient record."
            badge={pendingAi.length}
            badgeLabel="pending"
            accent="purple"
            icon={<IconSparkle />}
          />
        </div>

        <p className="mt-10 text-center text-[11px] text-slate-400 dark:text-slate-500">
          Every action is recorded in the audit log. No data leaves this device.
        </p>
      </div>
    </main>
  );
}

/* ---------- Metric card ---------- */

function MetricCard({
  label, value, icon, accent, sub, href, highlight,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  accent: "blue" | "purple" | "amber" | "indigo" | "emerald";
  sub: string;
  href?: string;
  highlight?: boolean;
}) {
  const map = {
    blue:    { ring: "ring-blue-100 dark:ring-blue-900/50",       icon: "from-blue-500 to-indigo-500",      value: "text-blue-700 dark:text-blue-300" },
    purple:  { ring: "ring-purple-100 dark:ring-purple-900/50",   icon: "from-purple-500 to-pink-500",      value: "text-purple-700 dark:text-purple-300" },
    emerald: { ring: "ring-emerald-100 dark:ring-emerald-900/50", icon: "from-emerald-500 to-teal-500",    value: "text-emerald-700 dark:text-emerald-300" },
    amber:   { ring: "ring-amber-100 dark:ring-amber-900/50",     icon: "from-amber-500 to-orange-500",     value: "text-amber-700 dark:text-amber-300" },
    indigo:  { ring: "ring-indigo-100 dark:ring-indigo-900/50",   icon: "from-indigo-500 to-purple-500",    value: "text-indigo-700 dark:text-indigo-300" },
  };
  const a = map[accent];

  const inner = (
    <div
      className={
        "relative rounded-2xl border bg-white dark:bg-slate-900 p-5 transition-all " +
        (href ? "hover:shadow-md hover:-translate-y-0.5 cursor-pointer " : "") +
        (highlight ? "border-slate-300 dark:border-slate-700 ring-1 " + a.ring : "border-slate-200 dark:border-slate-800")
      }
    >
      <div className="flex items-start justify-between">
        <div className={"w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-sm bg-gradient-to-br " + a.icon}>
          {icon}
        </div>
        {href && (
          <svg className="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="5" y1="12" x2="19" y2="12" />
            <polyline points="12 5 19 12 12 19" />
          </svg>
        )}
      </div>
      <div className="mt-4">
        <div className={"text-3xl font-bold tabular-nums " + (highlight ? a.value : "text-slate-900 dark:text-white")}>
          {value}
        </div>
        <div className="text-xs font-medium text-slate-600 dark:text-slate-400 mt-0.5">{label}</div>
        <div className="text-[11px] text-slate-400 dark:text-slate-500 mt-1.5">{sub}</div>
      </div>
    </div>
  );

  return href ? <Link href={href}>{inner}</Link> : inner;
}

/* ---------- queue card ---------- */

function QueueCard({
  href, title, description, badge, badgeLabel, accent, icon,
}: {
  href: string;
  title: string;
  description: string;
  badge: number;
  badgeLabel: string;
  accent: "purple" | "amber";
  icon: React.ReactNode;
}) {
  const map = {
    purple: { bg: "from-purple-500 to-pink-500",      text: "text-purple-700 dark:text-purple-300" },
    amber:  { bg: "from-amber-500 to-orange-500",     text: "text-amber-700 dark:text-amber-300" },
  };
  const a = map[accent];
  return (
    <Link
      href={href}
      className="group rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-md transition-all"
    >
      <div className="flex items-start gap-4">
        <div className={"w-11 h-11 rounded-xl bg-gradient-to-br text-white flex items-center justify-center shadow-sm shrink-0 " + a.bg}>
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">{title}</h3>
            {badge > 0 && (
              <span className={"text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 " + a.text}>
                {badge} {badgeLabel}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">{description}</p>
        </div>
        <svg className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-transform shrink-0 mt-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="5" y1="12" x2="19" y2="12" />
          <polyline points="12 5 19 12 12 19" />
        </svg>
      </div>
    </Link>
  );
}

/* ---------- small components ---------- */

function StatChip({ label, value, variant }: { label: string; value: number; variant?: "warn" | "ok" }) {
  const cls =
    variant === "warn"
      ? "bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-900"
      : variant === "ok"
      ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-900"
      : "bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700";
  return (
    <span className={"inline-flex items-center gap-1 px-2 py-1 rounded-md border text-[10px] font-medium tabular-nums " + cls}>
      <span className="font-bold">{value}</span>
      <span className="opacity-80">{label}</span>
    </span>
  );
}

function IconLink({ href, title, children }: { href: string; title: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      title={title}
      className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white transition-colors"
    >
      {children}
    </Link>
  );
}

function ActionIcon({ action }: { action: string }) {
  const map: Record<string, { bg: string; icon: React.ReactNode }> = {
    "auth.login":         { bg: "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400", icon: <IconUser /> },
    "document.upload":    { bg: "bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400", icon: <IconDoc /> },
    "document.delete":    { bg: "bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400",     icon: <IconDoc /> },
    "fhir.export":        { bg: "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400", icon: <IconCheck /> },
    "summary.save":       { bg: "bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400",     icon: <IconNote /> },
    "summary.pdf_export": { bg: "bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400",     icon: <IconNote /> },
    "summary.generate_ai":{ bg: "bg-purple-100 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400", icon: <IconSparkle /> },
    "summary.ai_approve": { bg: "bg-emerald-100 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400", icon: <IconCheck /> },
    "summary.ai_reject":  { bg: "bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400",     icon: <IconAlert /> },
    "consent.revoke":     { bg: "bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400",     icon: <IconAlert /> },
  };
  const entry = map[action] ?? { bg: "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400", icon: <IconList /> };
  return (
    <span className={"w-7 h-7 rounded-lg flex items-center justify-center shrink-0 " + entry.bg}>
      {entry.icon}
    </span>
  );
}

/* ---------- icons ---------- */

function IconUsers() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function IconSparkle() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2l1.8 5.6L19.4 9l-4.6 3.7L16 18.4 12 15l-4 3.4 1.2-5.7L4.6 9l5.6-1.4z" />
    </svg>
  );
}

function IconAlert() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

function IconDoc() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}

function IconChart() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 9 12 13 8 21 16" />
      <polyline points="21 12 21 16 17 16" />
    </svg>
  );
}

function IconNote() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16v12l-4 4H4z" />
      <line x1="8" y1="9" x2="16" y2="9" />
      <line x1="8" y1="13" x2="14" y2="13" />
    </svg>
  );
}

function IconList() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="8" y1="6" x2="21" y2="6" />
      <line x1="8" y1="12" x2="21" y2="12" />
      <line x1="8" y1="18" x2="21" y2="18" />
      <line x1="3" y1="6" x2="3.01" y2="6" />
      <line x1="3" y1="12" x2="3.01" y2="12" />
      <line x1="3" y1="18" x2="3.01" y2="18" />
    </svg>
  );
}

function IconGit() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="6" cy="6" r="2" />
      <circle cx="6" cy="18" r="2" />
      <circle cx="18" cy="12" r="2" />
      <line x1="6" y1="8" x2="6" y2="16" />
      <path d="M6 12h6a4 4 0 0 0 4-4V6" />
    </svg>
  );
}

function IconUser() {
  return (
    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

function IconCheck() {
  return (
    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function IconCheckBig() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

