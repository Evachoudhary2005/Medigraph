from pathlib import Path

f = Path("src/app/intake/[patientId]/page.tsx")
content = f.read_text(encoding="utf-8")

# ---------- 1. Add upload translations ----------
if '"docs.title"' not in content:
    content = content.replace(
        '"voice.err":    { en: "Microphone error",   hi: "\\u092e\\u093e\\u0907\\u0915 \\u0924\\u094d\\u0930\\u0941\\u091f\\u093f" },',
        '"voice.err":    { en: "Microphone error",   hi: "\\u092e\\u093e\\u0907\\u0915 \\u0924\\u094d\\u0930\\u0941\\u091f\\u093f" },\n'
        '  "docs.title":   { en: "Prior documents",   hi: "\\u092a\\u0942\\u0930\\u094d\\u0935 \\u0926\\u0938\\u094d\\u0924\\u093e\\u0935\\u0947\\u091c\\u093c" },\n'
        '  "docs.desc":    { en: "Optional. Add photos or scans of prescriptions, lab reports, or discharge summaries.",\n'
        '                    hi: "\\u0935\\u0948\\u0915\\u0932\\u094d\\u092a\\u093f\\u0915\\u0964 \\u092a\\u0930\\u094d\\u091a\\u094b\\u0902, \\u0932\\u0948\\u092c \\u0930\\u093f\\u092a\\u094b\\u0930\\u094d\\u091f, \\u092f\\u093e \\u0921\\u093f\\u0938\\u094d\\u091a\\u093e\\u0930\\u094d\\u091c \\u0938\\u092e\\u0930\\u0940 \\u0915\\u0940 \\u092b\\u094b\\u091f\\u094b \\u091c\\u094b\\u0921\\u093c\\u0947\\u0902\\u0964" },\n'
        '  "docs.drop":    { en: "Drag a JPG, PNG, or PDF here, or", hi: "JPG, PNG, \\u092f\\u093e PDF \\u092f\\u0939\\u093e\\u0902 \\u0916\\u0940\\u0902\\u091a\\u0947\\u0902, \\u092f\\u093e" },\n'
        '  "docs.choose":  { en: "Choose file",        hi: "\\u092b\\u093c\\u093e\\u0907\\u0932 \\u091a\\u0941\\u0928\\u0947\\u0902" },\n'
        '  "docs.processing": { en: "Analysing with AI...", hi: "AI \\u0938\\u0947 \\u0935\\u093f\\u0936\\u094d\\u0932\\u0947\\u0937\\u0923..." },\n'
        '  "docs.uploading": { en: "Uploading...",    hi: "\\u0905\\u092a\\u0932\\u094b\\u0921 \\u0939\\u094b \\u0930\\u0939\\u093e \\u0939\\u0948..." },\n'
        '  "docs.received": { en: "Received",         hi: "\\u092a\\u094d\\u0930\\u093e\\u092a\\u094d\\u0924" },\n'
        '  "docs.remove":  { en: "Remove",            hi: "\\u0939\\u091f\\u093e\\u090f\\u0902" },\n'
        '  "docs.empty":   { en: "No documents uploaded yet.", hi: "\\u0905\\u092d\\u0940 \\u0924\\u0915 \\u0915\\u094b\\u0908 \\u0926\\u0938\\u094d\\u0924\\u093e\\u0935\\u0947\\u091c\\u093c \\u0928\\u0939\\u0940\\u0902\\u0964" },'
    )
    print("  + added docs translations")

# ---------- 2. Add docs state + handlers ----------
anchor_state = '  const [loading, setLoading] = useState(true);'
new_state = '''  const [loading, setLoading] = useState(true);
  const [docs, setDocs] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadErr, setUploadErr] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const docInputRef = useRef<HTMLInputElement | null>(null);'''

if "const [docs, setDocs]" not in content:
    content = content.replace(anchor_state, new_state)
    print("  + added docs state")

# ---------- 3. Add load-docs + upload + delete functions ----------
anchor_fn = '  async function complete() {'
fn_block = '''  async function loadDocs() {
    try {
      const r = await fetch("/api/v1/documents?patient_id=" + patientId);
      if (r.ok) setDocs(await r.json());
    } catch {}
  }

  async function uploadDoc(file: File) {
    setUploadErr(null);
    setUploading(true);
    setProcessing(false);
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
      if (!pr.ok) throw new Error(await pr.text());
      await loadDocs();
    } catch (e: any) {
      setUploadErr(e?.message ?? String(e));
    } finally {
      setUploading(false);
      setProcessing(false);
    }
  }

  async function deleteDoc(documentId: string) {
    if (!confirm("Remove this document?")) return;
    setDeletingId(documentId);
    try {
      const r = await fetch("/api/v1/documents/" + documentId, { method: "DELETE" });
      if (!r.ok) throw new Error(await r.text());
      await loadDocs();
    } catch (e: any) {
      setUploadErr(e?.message ?? String(e));
    } finally {
      setDeletingId(null);
    }
  }

  async function complete() {'''

if "async function loadDocs()" not in content:
    content = content.replace(anchor_fn, fn_block)
    print("  + added docs functions")

# ---------- 4. Call loadDocs on mount ----------
old_mount = '''        const map: Record<string, any> = {};
        for (const a of s.answers ?? []) map[a.question_id] = a.value;
        setAnswers(map);'''
new_mount = '''        const map: Record<string, any> = {};
        for (const a of s.answers ?? []) map[a.question_id] = a.value;
        setAnswers(map);

        // load any prior documents
        try {
          const dr = await fetch("/api/v1/documents?patient_id=" + patientId);
          if (dr.ok) setDocs(await dr.json());
        } catch {}'''

if "load any prior documents" not in content:
    content = content.replace(old_mount, new_mount)
    print("  + wired loadDocs on mount")

# ---------- 5. Insert the upload section JSX before the "err" block ----------
anchor_jsx = '''        {err && (
          <div className="mt-6 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-sm text-red-800 dark:text-red-300">
            {err}
          </div>
        )}'''

upload_jsx = '''        {/* -------- Inline document upload -------- */}
        <section className="mb-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden shadow-sm">
          <div className="relative">
            <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-indigo-500 to-purple-500" />
            <div className="flex items-center gap-4 px-5 py-4">
              <div className="relative w-11 h-11 rounded-xl flex items-center justify-center shrink-0 bg-gradient-to-br from-indigo-500 to-purple-500 text-white shadow-md">
                {docs.length > 0 ? (
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-base font-semibold text-slate-900 dark:text-white">{t("docs.title")}</h2>
                  <span className="text-[10px] uppercase tracking-widest font-semibold text-indigo-700 dark:text-indigo-300">
                    {docs.length > 0 ? docs.length + " " + t("docs.received") : "Optional"}
                  </span>
                </div>
                <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  {t("docs.desc")}
                </p>
              </div>
              <Link href={"/intake/" + patientId + "/documents"}
                    className="hidden sm:inline-flex items-center gap-1.5 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline whitespace-nowrap shrink-0">
                Full view
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </Link>
            </div>
          </div>

          <div className="border-t border-slate-100 dark:border-slate-800 p-5">
            {/* drop zone */}
            <div
              onDragOver={e => e.preventDefault()}
              onDrop={e => {
                e.preventDefault();
                const f = e.dataTransfer.files?.[0];
                if (f) uploadDoc(f);
              }}
              className="relative rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-950/40 px-6 py-8 text-center hover:border-indigo-400 dark:hover:border-indigo-600 transition-colors"
            >
              <div className="mx-auto w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 text-white flex items-center justify-center shadow-md shadow-indigo-500/30">
                {uploading || processing ? (
                  <span className="w-5 h-5 rounded-full border-2 border-white/40 border-t-white animate-spin" />
                ) : (
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                )}
              </div>
              <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">
                {uploading
                  ? (processing ? t("docs.processing") : t("docs.uploading"))
                  : t("docs.drop")}
              </p>
              {!uploading && (
                <button
                  type="button"
                  onClick={() => docInputRef.current?.click()}
                  className="mt-3 inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-xs font-semibold hover:bg-slate-800 dark:hover:bg-slate-100 transition-colors">
                  <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  {t("docs.choose")}
                </button>
              )}
              <input
                ref={docInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp,application/pdf"
                className="hidden"
                onChange={e => {
                  const f = e.target.files?.[0];
                  if (f) uploadDoc(f);
                  e.target.value = "";
                }}
              />
            </div>

            {uploadErr && (
              <div className="mt-3 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 px-4 py-2.5 text-xs text-red-800 dark:text-red-300">
                {uploadErr}
              </div>
            )}

            {/* uploaded list */}
            {docs.length > 0 ? (
              <ul className="mt-4 space-y-2">
                {docs.map((d: any) => (
                  <li key={d.id} className="flex items-center gap-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-4 py-3">
                    <span className="w-9 h-9 rounded-lg bg-indigo-100 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-300 flex items-center justify-center shrink-0">
                      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-slate-900 dark:text-white truncate">{d.filename}</div>
                      <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                        {new Date(d.uploaded_at).toLocaleString()}
                        {d.verified_confidence != null && " - AI conf " + d.verified_confidence.toFixed(2)}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => deleteDoc(d.id)}
                      disabled={deletingId === d.id}
                      className="text-[11px] px-2.5 py-1 rounded-md text-slate-500 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors disabled:opacity-50">
                      {deletingId === d.id ? "..." : t("docs.remove")}
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-3 text-xs text-slate-500 dark:text-slate-400 text-center">{t("docs.empty")}</p>
            )}
          </div>
        </section>

        {err && (
          <div className="mt-6 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-sm text-red-800 dark:text-red-300">
            {err}
          </div>
        )}'''

if "Inline document upload" not in content:
    content = content.replace(anchor_jsx, upload_jsx)
    print("  + inserted upload section JSX")

f.write_text(content, encoding="utf-8")
print("WROTE src/app/intake/[patientId]/page.tsx")
print("bytes:", f.stat().st_size)

raw = f.read_text(encoding="utf-8")
non_ascii = [c for c in raw if ord(c) > 127]
print("non-ASCII chars:", len(non_ascii))
