"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";

type Doc = {
  id: string;
  filename: string;
  document_type: string;
  language: string;
  size_bytes: number;
  uploaded_at: string;
  needs_review?: boolean;
  verified_confidence?: number | null;
};

export default function DocumentsPage({ params }: { params: { patientId: string } }) {
  const patientId = params.patientId;
  const [lang, setLang] = useState<"en" | "hi">("en");
  const [docs, setDocs] = useState<Doc[]>([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [doneFilename, setDoneFilename] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  async function refresh() {
    try {
      const list = await fetch("/api/v1/documents?patient_id=" + patientId).then(r => r.json());
      setDocs(list);
    } catch (e: any) { setErr(e?.message ?? String(e)); }
  }

  useEffect(() => { refresh(); }, [patientId]);

  async function upload(file: File) {
    setErr(null);
    setUploading(true);
    setProcessing(false);
    setDoneFilename(null);
    try {
      const fd = new FormData();
      fd.append("patient_id", patientId);
      fd.append("language", lang);
      fd.append("file", file, file.name);
      const r = await fetch("/api/v1/documents/upload", { method: "POST", body: fd });
      if (!r.ok) throw new Error(await r.text());
      const j = await r.json();

      setProcessing(true);
      const pr = await fetch("/api/v1/documents/" + j.document_id + "/process?actor=system", {
        method: "POST",
      });
      if (!pr.ok) throw new Error("Processing failed: " + (await pr.text()));

      setDoneFilename(file.name);
      await refresh();
    } catch (e: any) {
      setErr("Upload error: " + (e?.message ?? String(e)));
    } finally {
      setUploading(false);
      setProcessing(false);
    }
  }

  async function deleteDoc(documentId: string, filename: string) {
    const ok = window.confirm(
      "Remove this document?\n\n" + filename + "\n\n" + "This cannot be undone."
    );
    if (!ok) return;
    setErr(null);
    setDeletingId(documentId);
    try {
      const r = await fetch("/api/v1/documents/" + documentId, { method: "DELETE" });
      if (!r.ok) throw new Error(await r.text());
      await refresh();
    } catch (e: any) {
      setErr("Delete error: " + (e?.message ?? String(e)));
    } finally {
      setDeletingId(null);
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) upload(f);
  }

  return (
    <main className="max-w-2xl mx-auto p-8">
      <Link href={"/intake/" + patientId} className="text-sm text-blue-600 hover:underline">
        Back to intake
      </Link>
      <h1 className="mt-2 text-2xl font-semibold">Upload medical documents</h1>
      <p className="text-slate-600 text-sm">
        Add a photo or scan of any prescription, lab report, or discharge summary.
        Your doctor will review it before your visit.
      </p>

      <div className="mt-4 flex items-center gap-3">
        <span className="text-sm text-slate-600">Language:</span>
        <select value={lang} onChange={e => setLang(e.target.value as "en" | "hi")}
                className="border border-slate-300 rounded px-2 py-1 text-sm">
          <option value="en">English</option>
          <option value="hi">Hindi</option>
        </select>
      </div>

      <div onDragOver={e => e.preventDefault()} onDrop={onDrop}
           className="mt-6 border-2 border-dashed border-slate-300 rounded p-8 text-center bg-white">
        <p className="text-slate-600">Drag a JPG, PNG, or PDF here, or</p>
        <button type="button" onClick={() => inputRef.current?.click()} disabled={uploading}
                className="mt-3 px-4 py-2 rounded bg-blue-600 text-white disabled:opacity-50">
          {uploading
            ? (processing ? "Analysing with AI..." : "Uploading...")
            : "Choose file"}
        </button>
        <input ref={inputRef} type="file"
               accept="image/jpeg,image/png,image/webp,application/pdf"
               className="hidden"
               onChange={e => { const f = e.target.files?.[0]; if (f) upload(f); }} />
        {uploading && (
          <p className="mt-3 text-xs text-slate-500">
            {processing
              ? "Running the AI pipeline. This may take up to 2 minutes on the first document."
              : "Extracting text from your document..."}
          </p>
        )}
      </div>

      {err && <p className="mt-4 text-red-600">{err}</p>}

      {doneFilename && !uploading && (
        <section className="mt-6 rounded border border-emerald-300 bg-emerald-50 p-4">
          <h2 className="font-semibold text-emerald-900">Document received</h2>
          <p className="text-sm text-emerald-800 mt-1">
            <span className="font-medium">{doneFilename}</span> has been processed.
            A summary will be ready for your doctor to review before your visit.
          </p>
        </section>
      )}

      <section className="mt-8">
        <h2 className="font-semibold">Your documents</h2>
        {docs.length === 0 && (
          <p className="text-sm text-slate-500 mt-1">No documents uploaded yet.</p>
        )}
        <ul className="mt-2 space-y-2">
          {docs.map(d => (
            <li key={d.id} className="rounded border border-slate-200 bg-white p-3 text-sm">
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <div className="font-medium truncate">{d.filename}</div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    {new Date(d.uploaded_at).toLocaleString()} - {(d.size_bytes / 1024).toFixed(0)} KB
                  </div>
                </div>
                <button onClick={() => deleteDoc(d.id, d.filename)}
                        disabled={deletingId === d.id}
                        className="text-xs px-3 py-1 rounded border border-red-300 text-red-700 hover:bg-red-50 disabled:opacity-50">
                  {deletingId === d.id ? "Removing..." : "Remove"}
                </button>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}