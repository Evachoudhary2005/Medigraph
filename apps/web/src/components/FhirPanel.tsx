"use client";
import { useEffect, useState } from "react";
import Link from "next/link";

type HapiValidation = {
  available: boolean;
  valid: boolean;
  error_count: number;
  warning_count: number;
  info_count: number;
  issues: { severity: string; code: string; diagnostics: string; location: string[] }[];
  stderr?: string;
};

type FhirBundle = {
  id: string;
  resourceType: string;
  entry: { resource: { resourceType: string; id: string } }[];
};

type Validation = {
  valid: boolean;
  issues: string[];
  entries: number;
  profile: string;
};

type FhirExportResponse = {
  bundle: FhirBundle;
  validation: Validation;
  hapi_validation: HapiValidation | null;
};

export default function FhirPanel({ patientId }: { patientId: string }) {
  const [exporting, setExporting] = useState(false);
  const [data, setData] = useState<FhirExportResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function run() {
    setErr(null);
    setExporting(true);
    setData(null);
    try {
      const r = await fetch("/api/v1/fhir/export/" + patientId + "?actor=clinician", {
        method: "POST",
      });
      if (!r.ok) throw new Error(await r.text());
      setData(await r.json());
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setExporting(false);
    }
  }

  function download() {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data.bundle, null, 2)], { type: "application/fhir+json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "fhir-bundle-" + patientId.slice(0, 8) + ".json";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="mt-6">
      <button onClick={run} disabled={exporting}
              className="px-3 py-1.5 text-sm rounded bg-indigo-600 text-white disabled:opacity-50">
        {exporting ? "Exporting (30-90 s first time)..." : "Export to FHIR + HAPI validate"}
      </button>

      {err && <p className="mt-3 text-sm text-red-600">{err}</p>}

      {data && (
        <>
          {/* Structural */}
          <div className="mt-4 rounded border border-indigo-200 bg-indigo-50 p-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-indigo-900">FHIR R4 Bundle</h2>
              <span className={"px-2 py-1 rounded text-xs " +
                (data.validation.valid ? "bg-emerald-200 text-emerald-900" : "bg-red-200 text-red-900")}>
                {data.validation.valid ? "VALID" : "INVALID"}
              </span>
            </div>
            <dl className="mt-3 text-xs grid grid-cols-2 gap-1">
              <dt className="text-slate-600">Bundle id</dt>
              <dd className="font-mono">{data.bundle.id}</dd>
              <dt className="text-slate-600">Entries</dt>
              <dd>{data.validation.entries}</dd>
              <dt className="text-slate-600">Profile</dt>
              <dd>{data.validation.profile}</dd>
            </dl>
            <h3 className="mt-3 font-medium text-sm text-slate-700">Resources</h3>
            <ul className="mt-1 text-xs space-y-0.5">
              {data.bundle.entry.map((e, i) => (
                <li key={i} className="font-mono text-slate-700">
                  {e.resource.resourceType}/<span className="text-slate-400">{e.resource.id.slice(0, 8)}...</span>
                </li>
              ))}
            </ul>
            <button onClick={download}
                    className="mt-3 px-3 py-1.5 text-sm rounded bg-indigo-600 text-white">
              Download bundle.json
            </button>
          </div>

          {/* HAPI */}
          <div className="mt-4 rounded border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold">HAPI FHIR Validator</h2>
              {data.hapi_validation && (
                <span className={"px-2 py-1 rounded text-xs " +
                  (data.hapi_validation.valid
                    ? "bg-emerald-200 text-emerald-900"
                    : "bg-amber-200 text-amber-900")}>
                  {data.hapi_validation.valid ? "PASS" : "ISSUES"}
                </span>
              )}
            </div>

            {!data.hapi_validation && (
              <p className="mt-2 text-xs text-slate-500">
                Not available (Java or validator_cli.jar missing on server).
              </p>
            )}

            {data.hapi_validation && !data.hapi_validation.available && (
              <p className="mt-2 text-xs text-amber-700">
                {data.hapi_validation.stderr || "Validator unavailable"}
              </p>
            )}

            {data.hapi_validation && data.hapi_validation.available && (
              <>
                <dl className="mt-3 text-xs grid grid-cols-3 gap-2">
                  <div>
                    <dt className="text-slate-500">Errors</dt>
                    <dd className={"text-lg font-mono " +
                      (data.hapi_validation.error_count === 0 ? "text-emerald-700" : "text-red-700")}>
                      {data.hapi_validation.error_count}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate-500">Warnings</dt>
                    <dd className="text-lg font-mono text-slate-700">
                      {data.hapi_validation.warning_count}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-slate-500">Info</dt>
                    <dd className="text-lg font-mono text-slate-500">
                      {data.hapi_validation.info_count}
                    </dd>
                  </div>
                </dl>

                {data.hapi_validation.issues.length > 0 && (
                  <ul className="mt-3 space-y-1 text-xs max-h-48 overflow-auto">
                    {data.hapi_validation.issues.map((i, k) => (
                      <li key={k} className={
                        i.severity === "error" ? "text-red-700" :
                        i.severity === "warning" ? "text-amber-700" :
                        "text-slate-600"
                      }>
                        <span className="font-mono">[{i.severity}]</span> {i.diagnostics}
                        {i.location.length > 0 && (
                          <div className="text-slate-400 ml-4 font-mono">{i.location.join(", ")}</div>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </>
            )}
          </div>
        </>
      )}
    </section>
  );
}