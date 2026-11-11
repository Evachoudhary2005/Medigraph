from pathlib import Path

f = Path("src/app/intake/[patientId]/page.tsx")
content = f.read_text(encoding="utf-8")

# ---------- 1. Add a "completed" state ----------
old_state = '  const [priorSummary, setPriorSummary] = useState<any | null>(null);'
new_state = '''  const [priorSummary, setPriorSummary] = useState<any | null>(null);
  const [completed, setCompleted] = useState(false);
  const [finishing, setFinishing] = useState(false);'''

if "const [completed, setCompleted]" not in content:
    content = content.replace(old_state, new_state)
    print("  + added completed state")

# ---------- 2. Replace the complete() function ----------
old_complete = '''  async function complete() {
    if (!session) return;
    await fetch("/api/v1/intake-sessions/" + session.id + "/complete", { method: "POST" });
    router.push("/intake/" + patientId + "/documents");
  }'''

new_complete = '''  async function complete() {
    if (!session || finishing) return;
    setFinishing(true);
    try {
      await fetch("/api/v1/intake-sessions/" + session.id + "/complete", { method: "POST" });
      setCompleted(true);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setFinishing(false);
    }
  }'''

if old_complete in content:
    content = content.replace(old_complete, new_complete)
    print("  + rewrote complete() to show in-place success")
else:
    print("  ! old complete() not found - listing current")
    idx = content.find("async function complete")
    if idx > 0:
        print(content[idx:idx+400])

# ---------- 3. Update button label based on docs count ----------
old_label = '''            <button onClick={complete}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/30 hover:shadow-lg hover:shadow-blue-500/40 active:scale-[0.98] transition-all">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              {t("submit")}
            </button>'''

new_label = '''            <button onClick={complete} disabled={finishing}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/30 hover:shadow-lg hover:shadow-blue-500/40 active:scale-[0.98] transition-all disabled:opacity-60">
              {finishing ? (
                <span className="w-4 h-4 rounded-full border-2 border-white/40 border-t-white animate-spin" />
              ) : docs.length > 0 ? (
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              ) : (
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              )}
              {docs.length > 0 ? t("submit") : (lang === "en" ? "Complete intake" : "\\u092a\\u094d\\u0930\\u0935\\u0947\\u0936 \\u092a\\u0942\\u0930\\u094d\\u0923 \\u0915\\u0930\\u0947\\u0902")}
            </button>'''

if old_label in content:
    content = content.replace(old_label, new_label)
    print("  + button label is now conditional on docs count")
else:
    print("  ! submit button block not found - fallback to simpler replace")
    content = content.replace("{t(\"submit\")}\n            </button>",
                              "{(docs.length > 0 ? t(\"submit\") : (lang === \"en\" ? \"Complete intake\" : \"\\u092a\\u094d\\u0930\\u0935\\u0947\\u0936 \\u092a\\u0942\\u0930\\u094d\\u0923 \\u0915\\u0930\\u0947\\u0902\"))}\n            </button>")

# ---------- 4. Add success screen overlay ----------
# We render the entire page normally, but if `completed` is true, render a success screen instead.
old_return = '''  return (
    <main className="relative min-h-screen bg-slate-50 dark:bg-[#070b18] pb-32">'''

new_return = '''  if (completed) {
    return (
      <main className="relative min-h-screen bg-slate-50 dark:bg-[#070b18] flex items-center justify-center p-6">
        <div className="max-w-md w-full rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 text-center shadow-xl anim-slide-up">
          <div className="relative w-20 h-20 mx-auto">
            <span className="absolute inset-0 rounded-full bg-emerald-500 flex items-center justify-center shadow-2xl shadow-emerald-500/40">
              <svg className="w-10 h-10 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </span>
            <span className="absolute inset-0 rounded-full bg-emerald-500 animate-ping opacity-30" />
          </div>
          <h1 className="mt-6 text-2xl font-bold text-slate-900 dark:text-white">
            {lang === "en" ? "Intake submitted" : "\\u092a\\u094d\\u0930\\u0935\\u0947\\u0936 \\u091c\\u092e\\u093e"}
          </h1>
          <p className="mt-3 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            {lang === "en"
              ? "Your answers have been saved. Your physician will see a summary before your visit."
              : "\\u0906\\u092a\\u0915\\u0947 \\u0909\\u0924\\u094d\\u0924\\u0930 \\u0938\\u0939\\u0947\\u091c\\u0947 \\u0917\\u090f \\u0939\\u0948\\u0902\\u0964 \\u0906\\u092a\\u0915\\u0947 \\u091a\\u093f\\u0915\\u093f\\u0924\\u094d\\u0938\\u0915 \\u0906\\u092a\\u0915\\u0940 \\u092f\\u093e\\u0924\\u094d\\u0930\\u093e \\u0938\\u0947 \\u092a\\u0939\\u0932\\u0947 \\u0938\\u093e\\u0930\\u093e\\u0902\\u0936 \\u0926\\u0947\\u0916\\u0947\\u0902\\u0917\\u0947\\u0964"}
          </p>
          <div className="mt-6 rounded-xl border border-emerald-200 dark:border-emerald-900 bg-emerald-50 dark:bg-emerald-950/40 px-4 py-3 text-xs text-emerald-800 dark:text-emerald-200">
            <div className="flex items-center justify-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              {docs.length > 0
                ? (lang === "en" ? docs.length + " document" + (docs.length > 1 ? "s" : "") + " attached" : docs.length + " \\u0926\\u0938\\u094d\\u0924\\u093e\\u0935\\u0947\\u091c\\u093c \\u0938\\u0902\\u0932\\u0917\\u094d\\u0928")
                : (lang === "en" ? "No documents attached" : "\\u0915\\u094b\\u0908 \\u0926\\u0938\\u094d\\u0924\\u093e\\u0935\\u0947\\u091c\\u093c \\u0938\\u0902\\u0932\\u0917\\u094d\\u0928 \\u0928\\u0939\\u0940\\u0902")}
            </div>
          </div>
          <div className="mt-6 flex flex-col gap-2">
            <button
              onClick={() => { setCompleted(false); }}
              className="px-4 py-2.5 rounded-lg text-sm font-medium border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            >
              {lang === "en" ? "Review answers" : "\\u0909\\u0924\\u094d\\u0924\\u0930 \\u0926\\u0947\\u0916\\u0947\\u0902"}
            </button>
            <Link
              href={"/intake/" + patientId + "/documents"}
              className="px-4 py-2.5 rounded-lg text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors"
            >
              {lang === "en" ? "Upload documents" : "\\u0926\\u0938\\u094d\\u0924\\u093e\\u0935\\u0947\\u091c\\u093c \\u0905\\u092a\\u0932\\u094b\\u0921"}
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="relative min-h-screen bg-slate-50 dark:bg-[#070b18] pb-32">'''

if 'if (completed) {' not in content:
    content = content.replace(old_return, new_return)
    print("  + added success screen after complete")

f.write_text(content, encoding="utf-8")
print("WROTE src/app/intake/[patientId]/page.tsx")
print("bytes:", f.stat().st_size)

raw = f.read_text(encoding="utf-8")
non_ascii = [c for c in raw if ord(c) > 127]
print("non-ASCII chars:", len(non_ascii))
