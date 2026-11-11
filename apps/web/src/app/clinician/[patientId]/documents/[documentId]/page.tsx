"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

type Region = {
  text: string;
  confidence: number;
  bbox: number[][];
  page?: number;
};

type PageData = {
  page: number;
  text: string;
  mean_confidence: number | null;
  regions: Region[];
};

type DocumentDetail = {
  id: string;
  patient_id: string;
  filename: string;
  document_type: string;
  language: string;
  size_bytes: number;
  uploaded_at: string;
  verified_text: string;
  verified_confidence: number | null;
  needs_review: boolean;
  file_url: string | null;
  pages: PageData[];
};

export default function DocumentDetailPage() {
  const params = useParams<{ patientId: string; documentId: string }>();
  const patientId = params.patientId;
  const documentId = params.documentId;

  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<"image" | "text">("image");
  const imgRef = useRef<HTMLImageElement | null>(null);
  const [imgSize, setImgSize] = useState<{ w: number; h: number } | null>(null);
  const [displayedWidth, setDisplayedWidth] = useState<number>(0);

  async function load() {
    setErr(null);
    setLoading(true);
    try {
      const r = await fetch("/api/v1/documents/" + documentId);
      if (!r.ok) throw new Error(await r.text());
      setDoc(await r.json());
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [documentId]);

  function onImgLoad() {
    if (!imgRef.current) return;
    setImgSize({
      w: imgRef.current.naturalWidth,
      h: imgRef.current.naturalHeight,
    });
    setDisplayedWidth(imgRef.current.clientWidth);
  }

  useEffect(() => {
    if (!imgRef.current) return;
    const ro = new ResizeObserver(() => {
      if (imgRef.current) setDisplayedWidth(imgRef.current.clientWidth);
    });
    ro.observe(imgRef.current);
    return () => ro.disconnect();
  }, [doc]);

  const regions = doc?.pages[0]?.regions ?? [];
  const scale = imgSize && displayedWidth ? displayedWidth / imgSize.w : 1;

  return (
    <main className="max-w-6xl mx-auto p-8">
      <div className="flex items-center gap-4">
        <Link href={"/intake/" + patientId + "/documents"}
              className="text-sm text-blue-600 hover:underline">
          All documents
        </Link>
        <Link href={"/clinician/" + patientId + "/timeline"}
              className="text-sm text-blue-600 hover:underline">
          Timeline
        </Link>
      </div>

      {err && <p className="mt-4 text-red-600">{err}</p>}
      {loading && <p className="mt-4 text-slate-500">Loading document...</p>}

      {doc && (
        <>
          <div className="mt-4 flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-semibold">{doc.filename}</h1>
              <p className="text-xs text-slate-500 mt-1">
                {doc.document_type} - {doc.language} - {doc.size_bytes} bytes -{" "}
                {new Date(doc.uploaded_at).toLocaleString()}
              </p>
              <p className="text-xs text-slate-500">document_id: {doc.id}</p>
            </div>
            <div className="text-right">
              {doc.verified_confidence != null && (
                <div className="text-sm">
                  <span className="text-slate-500">AI confidence: </span>
                  <span className="font-mono">{doc.verified_confidence.toFixed(2)}</span>
                </div>
              )}
              {doc.needs_review && (
                <span className="inline-block mt-1 px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-xs">
                  needs review
                </span>
              )}
            </div>
          </div>

          <div className="mt-6 flex gap-2 border-b border-slate-200">
            <button onClick={() => setActiveTab("image")}
                    className={"px-3 py-1.5 text-sm -mb-px " +
                      (activeTab === "image"
                        ? "border-b-2 border-blue-600 text-blue-700 font-medium"
                        : "text-slate-600 hover:text-slate-900")}>
              Image + bboxes
            </button>
            <button onClick={() => setActiveTab("text")}
                    className={"px-3 py-1.5 text-sm -mb-px " +
                      (activeTab === "text"
                        ? "border-b-2 border-blue-600 text-blue-700 font-medium"
                        : "text-slate-600 hover:text-slate-900")}>
              Extracted text
            </button>
          </div>

          {activeTab === "image" && (
            <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2">
                {doc.file_url ? (
                  <div className="relative rounded border border-slate-200 overflow-hidden bg-slate-100">
                    <img
                      ref={imgRef}
                      src={doc.file_url}
                      alt={doc.filename}
                      onLoad={onImgLoad}
                      className="w-full h-auto block"
                    />
                    {imgSize && regions.map((r, idx) => {
                      if (!r.bbox || r.bbox.length < 3) return null;
                      const xs = r.bbox.map(p => p[0]);
                      const ys = r.bbox.map(p => p[1]);
                      const x = Math.min(...xs) * scale;
                      const y = Math.min(...ys) * scale;
                      const w = (Math.max(...xs) - Math.min(...xs)) * scale;
                      const h = (Math.max(...ys) - Math.min(...ys)) * scale;
                      const isHover = hoveredIdx === idx;
                      const isLowConf = r.confidence < 0.7;
                      return (
                        <div
                          key={idx}
                          onMouseEnter={() => setHoveredIdx(idx)}
                          onMouseLeave={() => setHoveredIdx(null)}
                          className={"absolute border-2 cursor-pointer " +
                            (isHover
                              ? "border-blue-600 bg-blue-300/30"
                              : isLowConf
                              ? "border-amber-500 bg-amber-200/20"
                              : "border-blue-400/40 hover:border-blue-500")}
                          style={{ left: x, top: y, width: w, height: h }}
                          title={r.text}
                        />
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">
                    No image available (PDF or older upload).
                  </p>
                )}
                <p className="mt-2 text-xs text-slate-500">
                  {regions.length} OCR regions. Hover a box to highlight it.
                  Amber = low confidence (&lt; 0.70).
                </p>
              </div>

              <div className="lg:col-span-1 max-h-[70vh] overflow-auto rounded border border-slate-200 bg-white">
                <div className="sticky top-0 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-600 border-b">
                  Regions ({regions.length})
                </div>
                <ul className="divide-y divide-slate-100 text-xs">
                  {regions.map((r, idx) => (
                    <li
                      key={idx}
                      onMouseEnter={() => setHoveredIdx(idx)}
                      onMouseLeave={() => setHoveredIdx(null)}
                      className={"p-2 cursor-pointer " +
                        (hoveredIdx === idx ? "bg-blue-50" : "hover:bg-slate-50")}
                    >
                      <div className="flex items-center justify-between">
                        <span className={"font-mono " +
                          (r.confidence < 0.7 ? "text-amber-700" : "text-slate-400")}>
                          [{r.confidence.toFixed(2)}]
                        </span>
                        <span className="text-slate-400">#{idx}</span>
                      </div>
                      <div className="text-slate-700 mt-0.5">{r.text}</div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {activeTab === "text" && (
            <div className="mt-6 space-y-4">
              {doc.pages.map(p => (
                <div key={p.page} className="rounded border border-slate-200 bg-white p-4">
                  <div className="text-xs text-slate-500 mb-2">
                    Page {p.page}
                    {p.mean_confidence != null && ` - mean confidence ${p.mean_confidence.toFixed(2)}`}
                  </div>
                  <pre className="text-xs whitespace-pre-wrap">{p.text}</pre>
                </div>
              ))}
              {doc.verified_text && (
                <div className="rounded border border-purple-200 bg-purple-50 p-4">
                  <div className="text-xs font-medium text-purple-900 mb-2">
                    AI-corrected (verified) text
                  </div>
                  <pre className="text-xs whitespace-pre-wrap">{doc.verified_text}</pre>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </main>
  );
}