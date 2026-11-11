from pathlib import Path

f = Path("src/app/intake/[patientId]/page.tsx")
content = f.read_text(encoding="utf-8")

# 1. Add a mode state
old_state = '  const [loading, setLoading] = useState(true);'
new_state = '''  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<"brief" | "returning" | "full">("brief");
  const [priorSummary, setPriorSummary] = useState<any | null>(null);'''

if "const [mode, setMode]" not in content:
    content = content.replace(old_state, new_state)
    print("  + added mode state")

# 2. In the load effect, decide mode based on existing sessions/documents
old_fetch = '''        const qr = await fetch("/api/v1/questionnaires/gm_v1?lang=" + chosen).then(r => r.json());
        setQ(qr);'''
new_fetch = '''        // Determine whether this patient has been here before
        let chosenMode: "brief" | "returning" = "brief";
        let prior: any = null;
        try {
          const sessions = await fetch(
            "/api/v1/patients/" + patientId + "/intake-sessions",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ language: chosen }),
            }
          ).then(r => r.json());
          // If the session already has answers OR the patient has documents, treat as returning
          const hasPriorAnswers = (sessions.answers ?? []).length > 0;
          const docs = await fetch("/api/v1/documents?patient_id=" + patientId)
            .then(r => r.json())
            .catch(() => []);
          const hasPriorDocs = Array.isArray(docs) && docs.length > 0;

          if (hasPriorAnswers || hasPriorDocs) {
            chosenMode = "returning";
            prior = {
              documentCount: Array.isArray(docs) ? docs.length : 0,
              lastSessionDate: sessions.started_at,
            };
          }
        } catch {}
        setMode(chosenMode);
        setPriorSummary(prior);

        const qr = await fetch(
          "/api/v1/questionnaires/gm_v1?lang=" + chosen + "&mode=" + chosenMode
        ).then(r => r.json());
        setQ(qr);'''

if "Determine whether this patient has been here before" not in content:
    content = content.replace(old_fetch, new_fetch)
    print("  + added mode detection")

# 3. Also switch questionnaire when user changes language
old_switch = '''    try {
      const qr = await fetch("/api/v1/questionnaires/gm_v1?lang=" + next).then(r => r.json());
      setQ(qr);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    }'''
new_switch = '''    try {
      const qr = await fetch(
        "/api/v1/questionnaires/gm_v1?lang=" + next + "&mode=" + mode
      ).then(r => r.json());
      setQ(qr);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    }'''

if '&mode=" + mode' not in content:
    content = content.replace(old_switch, new_switch)
    print("  + language switch keeps mode")

# 4. Add a "welcome back" banner when in returning mode
old_sub = '<p className="text-sm text-slate-600 dark:text-slate-400 mb-8 max-w-2xl">{t("head.sub")}</p>'
new_sub = '''{mode === "returning" ? (
          <div className="mb-6 rounded-2xl border border-emerald-200 dark:border-emerald-900 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/30 p-5 flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-500 text-white flex items-center justify-center shrink-0 shadow-md shadow-emerald-500/30">
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-semibold text-emerald-900 dark:text-emerald-200">
                {lang === "en" ? "Welcome back" : "\u0935\u093e\u092a\u0938\u0940 \u092a\u0930 \u0938\u094d\u0935\u093e\u0917\u0924"}
              </div>
              <p className="text-xs text-emerald-800/80 dark:text-emerald-300/80 mt-1 leading-relaxed">
                {lang === "en"
                  ? "We already have your medical history on file. Just tell us about today's problem."
                  : "\u0939\u092e\u093e\u0930\u0947 \u092a\u093e\u0938 \u0906\u092a\u0915\u093e \u092a\u0942\u0930\u094d\u0935 \u0907\u0924\u093f\u0939\u093e\u0938 \u092a\u0939\u0932\u0947 \u0938\u0947 \u0939\u0948\u0964 \u092c\u0938 \u0906\u091c \u0915\u0940 \u0938\u092e\u0938\u094d\u092f\u093e \u092c\u0924\u093e\u090f\u0902\u0964"}
              </p>
              {priorSummary && priorSummary.documentCount > 0 && (
                <p className="text-[11px] text-emerald-700/70 dark:text-emerald-300/70 mt-2 font-mono">
                  {priorSummary.documentCount} prior document{priorSummary.documentCount > 1 ? "s" : ""} on file
                </p>
              )}
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 max-w-2xl">{t("head.sub")}</p>
        )}'''

if 'mode === "returning" ?' not in content:
    content = content.replace(old_sub, new_sub)
    print("  + added welcome-back banner")

f.write_text(content, encoding="utf-8")
print("WROTE src/app/intake/[patientId]/page.tsx")
print("bytes:", f.stat().st_size)
