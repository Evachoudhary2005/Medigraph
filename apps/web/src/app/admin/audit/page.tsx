"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

type Entry = {
  id: string;
  actor: string;
  action: string;
  patient_id: string | null;
  resource_type: string | null;
  resource_id: string | null;
  details: Record<string, any>;
  created_at: string;
};

type Page = {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  entries: Entry[];
};

const ACTION_FILTERS = [
  { value: "", label: "All actions" },
  { value: "auth", label: "auth.*" },
  { value: "document", label: "document.*" },
  { value: "summary", label: "summary.*" },
  { value: "timeline", label: "timeline.*" },
  { value: "fhir", label: "fhir.*" },
  { value: "consent", label: "consent.*" },
];

export default function AuditLogPage() {
  const [data, setData] = useState<Page | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [actionFilter, setActionFilter] = useState("");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  async function load() {
    setErr(null);
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set("page", String(page));
      params.set("page_size", String(pageSize));
      if (actionFilter) params.set("action", actionFilter);
      const r = await fetch("/api/v1/consents/audit/page?" + params.toString());
      if (r.status === 403 || r.status === 401) {
        window.location.href = "/clinician";
        return;
      }
      if (!r.ok) throw new Error(await r.text());
      setData(await r.json());
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [page, pageSize, actionFilter]);

  function toggle(id: string) {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  }

  return (
    <main className="max-w-5xl mx-auto p-8">
      <Link href="/admin/users" className="text-sm text-blue-600 hover:underline">
        User management
      </Link>
      <h1 className="mt-2 text-2xl font-semibold">Audit log</h1>
      <p className="mt-1 text-sm text-slate-600">
        Every action is recorded with actor, resource, and details. Read-only.
      </p>

      <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
        <label className="flex items-center gap-2">
          <span className="text-slate-600">Action</span>
          <select value={actionFilter}
                  onChange={e => { setActionFilter(e.target.value); setPage(1); }}
                  className="border border-slate-300 rounded px-2 py-1 text-sm">
            {ACTION_FILTERS.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
          </select>
        </label>

        <label className="flex items-center gap-2">
          <span className="text-slate-600">Page size</span>
          <select value={pageSize}
                  onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }}
                  className="border border-slate-300 rounded px-2 py-1 text-sm">
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </label>

        <button onClick={load}
                className="px-3 py-1 text-xs rounded border border-slate-300 hover:bg-slate-50">
          Refresh
        </button>
      </div>

      {err && <p className="mt-4 text-red-600">{err}</p>}
      {loading && <p className="mt-4 text-slate-500">Loading...</p>}

      {data && (
        <>
          <div className="mt-4 text-xs text-slate-500">
            {data.total} entries - page {data.page} of {data.total_pages}
          </div>

          <ul className="mt-3 divide-y divide-slate-200 border border-slate-200 rounded bg-white">
            {data.entries.map(e => (
              <li key={e.id} className="p-3 text-sm">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs px-1.5 py-0.5 rounded bg-slate-100">
                        {e.action}
                      </span>
                      <span className="text-xs text-slate-500">by {e.actor}</span>
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      {new Date(e.created_at).toLocaleString()}
                      {e.resource_type && (
                        <> - {e.resource_type}
                          {e.resource_id && "/" + e.resource_id.slice(0, 8)}
                        </>
                      )}
                    </div>
                  </div>
                  <button onClick={() => toggle(e.id)}
                          className="text-xs text-blue-600 hover:underline">
                    {expanded[e.id] ? "hide" : "details"}
                  </button>
                </div>
                {expanded[e.id] && (
                  <pre className="mt-2 text-[10px] bg-slate-50 rounded p-2 overflow-auto">
                    {JSON.stringify(e.details, null, 2)}
                  </pre>
                )}
              </li>
            ))}
          </ul>

          {data.entries.length === 0 && (
            <p className="mt-4 text-sm text-slate-500">No entries match this filter.</p>
          )}

          <div className="mt-4 flex items-center justify-between">
            <button onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={!data.has_prev}
                    className="px-3 py-1 text-sm rounded border border-slate-300 disabled:opacity-40">
              Previous
            </button>
            <span className="text-sm text-slate-600">{data.page} / {data.total_pages}</span>
            <button onClick={() => setPage(p => Math.min(data.total_pages, p + 1))}
                    disabled={!data.has_next}
                    className="px-3 py-1 text-sm rounded border border-slate-300 disabled:opacity-40">
              Next
            </button>
          </div>
        </>
      )}
    </main>
  );
}