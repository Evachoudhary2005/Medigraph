from pathlib import Path

tsx = r"""
"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import MicButton from "@/components/MicButton";

type Lang = "en" | "hi";

type Option = { value: string; label_en: string; label_hi: string };
type Question = {
  id: string;
  type: "text" | "duration" | "single_choice" | "multi_choice" | "yes_no";
  text_en: string;
  text_hi: string;
  required?: boolean;
  options?: Option[];
  visible_if?: { question_id: string; equals: string };
};
type Section = { id: string; title_en: string; title_hi: string; questions: Question[] };
type Questionnaire = { id: string; name: string; language: Lang; sections: Section[] };
type Session = {
  id: string;
  patient_id: string;
  questionnaire_id: string;
  language: string;
  status: string;
  answers: { question_id: string; value: any; source: string }[];
};

const UI: Record<string, { en: string; hi: string }> = {
  "crumb.home": { en: "Home", hi: "\u0939\u094b\u092e" },
  "crumb.questionnaire": { en: "Questionnaire", hi: "\u092a\u094d\u0930\u0936\u094d\u0928\u093e\u0935\u0932\u0940" },
  "head.title": { en: "General Medicine Intake", hi: "\u0938\u093e\u092e\u093e\u0928\u094d\u092f \u091a\u093f\u0915\u093f\u0924\u094d\u0938\u093e \u092a\u094d\u0930\u0935\u0947\u0936" },
  "head.subtitle": { en: "Answer what you can. You may skip any question.", hi: "\u091c\u093f\u0924\u0928\u093e \u0938\u0902\u092d\u0935 \u0939\u094b \u0909\u0924\u094d\u0924\u0930 \u0926\u0947\u0902\u0964 \u0915\u094b\u0908 \u092d\u0940 \u092a\u094d\u0930\u0936\u094d\u0928 \u091b\u094b\u0921\u093c \u0938\u0915\u0924\u0947 \u0939\u0948\u0902\u0964" },
  "head.docs": { en: "Upload documents", hi: "\u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c\u093c \u0905\u092a\u0932\u094b\u0921" },
  "head.answered": { en: "answered", hi: "\u0909\u0924\u094d\u0924\u0930\u093f\u0924" },
  "head.lang": { en: "Language", hi: "\u092d\u093e\u0937\u093e" },
  "head.saving": { en: "saving", hi: "\u0938\u0939\u0947\u091c \u0930\u0939\u0947 \u0939\u0948\u0902" },
  "head.saved": { en: "saved", hi: "\u0938\u0939\u0947\u091c\u093e \u0917\u092f\u093e" },
  "head.autosave": { en: "Answers save automatically", hi: "\u0909\u0924\u094d\u0924\u0930 \u0938\u094d\u0935\u091a\u093e\u0932\u093f\u0924 \u0930\u0942\u092a \u0938\u0947 \u0938\u0939\u0947\u091c\u0947 \u091c\u093e\u0924\u0947 \u0939\u0948\u0902" },
  "submit.title": { en: "Complete and upload documents", hi: "\u092a\u0942\u0930\u094d\u0923 \u0915\u0930\u0947\u0902 \u0914\u0930 \u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c\u093c \u0905\u092a\u0932\u094b\u0921 \u0915\u0930\u0947\u0902" },
  "submit.hint": { en: "You can return and edit your answers before your consultation.", hi: "\u0905\u092a\u0928\u0940 \u092a\u0930\u093e\u092e\u0930\u094d\u0936 \u0938\u0947 \u092a\u0939\u0932\u0947 \u0906\u092a \u0905\u092a\u0928\u0947 \u0909\u0924\u094d\u0924\u0930 \u0935\u093e\u092a\u0938 \u0915\u0930\u0915\u0947 \u0938\u0902\u092a\u093e\u0926\u093f\u0924 \u0915\u0930 \u0938\u0915\u0924\u0947 \u0939\u0948\u0902\u0964" },
  "voice.speak": { en: "Speak", hi: "\u092c\u094b\u0932\u0947\u0902" },
  "voice.stop": { en: "Stop", hi: "\u0930\u094b\u0915\u0947\u0902" },
  "voice.listening": { en: "Listening", hi: "\u0938\u0941\u0928 \u0930\u0939\u0947 \u0939\u0948\u0902" },
  "voice.error": { en: "Microphone error", hi: "\u092e\u093e\u0907\u0915 \u0924\u094d\u0930\u0941\u091f\u093f" },
  "err.load": { en: "Could not load questionnaire.", hi: "\u092a\u094d\u0930\u0936\u094d\u0928\u093e\u0935\u0932\u0940 \u0932\u094b\u0921 \u0928\u0939\u0940\u0902 \u0939\u094b \u0938\u0915\u0940\u0964" },
  "loading": { en: "Loading questionnaire...", hi: "\u092a\u094d\u0930\u0936\u094d\u0928\u093e\u0935\u0932\u0940 \u0932\u094b\u0921 \u0939\u094b \u0930\u0939\u0940 \u0939\u0948..." },
};

export default function IntakeQuestionnairePage({ params }: { params: { patientId: string } }) {
  const router = useRouter();
  const patientId = params.patientId;

  const [lang, setLang] = useState<Lang>("en");
  const [q, setQ] = useState<Questionnaire | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [saving, setSaving] = useState<string | null>(null);
  const [lastSaved, setLastSaved] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const sectionsRef = useRef<Record<string, HTMLElement | null>>({});

  const t = (k: string) => UI[k]?.[lang] ?? k;

  // ---------- load: detect language, then fetch questionnaire + session ----------
  useEffect(() => {
    (async () => {
      try {
        // 1. Determine language
        let chosen: Lang = "en";
        try {
          const stored = window.localStorage.getItem("mg-intake-lang");
          if (stored === "hi" || stored === "en") chosen = stored;
        } catch {}

        try {
          const p = await fetch("/api/v1/patients/" + patientId).then(r => r.json());
          if (p?.preferred_language === "hi" || p?.preferred_language === "en") {
            chosen = p.preferred_language;
          }
        } catch {}

        setLang(chosen);

        // 2. Fetch questionnaire (in chosen language)
        const qr = await fetch("/api/v1/questionnaires/gm_v1?lang=" + chosen).then(r => r.json());
        setQ(qr);

        // 3. Create or resume session
        const s: Session = await fetch("/api/v1/patients/" + patientId + "/intake-sessions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ language: chosen }),
        }).then(r => r.json());
        setSession(s);

        const map: Record<string, any> = {};
        for (const a of s.answers ?? []) map[a.question_id] = a.value;
        setAnswers(map);
      } catch (e: any) {
        setErr(e?.message ?? String(e));
      } finally {
        setLoading(false);
      }
    })();
    // eslint-disable-next-line
  }, [patientId]);

  // ---------- switch language live: refetch questionnaire copy, keep answers ----------
  async function switchLang(next: Lang) {
    if (next === lang) return;
    setLang(next);
    try { window.localStorage.setItem("mg-intake-lang", next); } catch {}
    try {
      const qr = await fetch("/api/v1/questionnaires/gm_v1?lang=" + next).then(r => r.json());
      setQ(qr);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    }
  }

  // ---------- counting + progress ----------
  const allQuestions = useMemo(
    () => (q ? q.sections.flatMap(s => s.questions) : []),
    [q]
  );
  const totalQuestions = allQuestions.length;

  const isVisible = (question: Question) => {
    if (!question.visible_if) return true;
    const v = answers[question.visible_if.question_id];
    return String(v) === question.visible_if.equals;
  };

  const answeredCount = useMemo(
    () => allQuestions.filter(qq => {
      if (!isVisible(qq)) return false;
      const v = answers[qq.id];
      if (v === null || v === undefined) return false;
      if (typeof v === "string" && v.trim() === "") return false;
      if (Array.isArray(v) && v.length === 0) return false;
      if (typeof v === "object" && v.value === "" && v.unit === "") return false;
      return true;
    }).length,
    // eslint-disable-next-line
    [answers, allQuestions]
  );

  const progress = totalQuestions ? Math.round((answeredCount / totalQuestions) * 100) : 0;

  // ---------- per-section stats ----------
  const sectionStats = useMemo(() => {
    const stats: Record<string, { answered: number; total: number }> = {};
    for (const s of q?.sections ?? []) {
      let a = 0, tot = 0;
      for (const qq of s.questions) {
        if (!isVisible(qq)) continue;
        tot += 1;
        const v = answers[qq.id];
        if (v !== null && v !== undefined && !(typeof v === "string" && v.trim() === "") && !(Array.isArray(v) && v.length === 0)) {
          a += 1;
        }
      }
      stats[s.id] = { answered: a, total: tot };
    }
    return stats;
    // eslint-disable-next-line
  }, [q, answers]);

  // ---------- save ----------
  async function saveAnswer(questionId: string, value: any, source: "touch" | "voice" = "touch", confidence?: number) {
    if (!session) return;
    setAnswers(prev => ({ ...prev, [questionId]: value }));
    setSaving(questionId);
    try {
      const s: Session = await fetch(
        "/api/v1/intake-sessions/" + session.id + "/answers/" + questionId,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ value, source, confidence: confidence ?? null }),
        }
      ).then(r => r.json());
      setSession(s);
      setLastSaved(new Date().toLocaleTimeString());
    } catch (e: any) {
      setErr(e?.message ?? String(e));
    } finally {
      setSaving(null);
    }
  }

  async function complete() {
    if (!session) return;
    await fetch("/api/v1/intake-sessions/" + session.id + "/complete", { method: "POST" });
    router.push("/intake/" + patientId + "/documents");
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="flex items-center gap-3 text-slate-500 dark:text-slate-400 text-sm">
          <span className="w-4 h-4 rounded-full border-2 border-slate-300 border-t-blue-500 animate-spin" />
          {t("loading")}
        </div>
      </main>
    );
  }
  if (err && !q) return <main className="p-8 text-red-600">{t("err.load")} {err}</main>;
  if (!q || !session) return <main className="p-8">{t("loading")}</main>;

  return (
    <main className="relative min-h-screen bg-slate-50 dark:bg-[#070b18] pb-24">
      {/* ---------- sticky top bar ---------- */}
      <header className="sticky top-0 z-30 bg-white/80 dark:bg-slate-900/80 backdrop-blur border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="min-w-0">
              <nav className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
                <Link href="/" className="hover:text-slate-900 dark:hover:text-white">{t("crumb.home")}</Link>
                <span className="opacity-50">/</span>
                <span className="text-slate-900 dark:text-white font-medium">{t("crumb.questionnaire")}</span>
              </nav>
              <h1 className="mt-0.5 text-lg font-semibold text-slate-900 dark:text-white tracking-tight">
                {t("head.title")}
              </h1>
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              {/* saving indicator */}
              <div className="hidden sm:flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400">
                {saving ? (
                  <>
                    <span className="w-3 h-3 rounded-full border-2 border-slate-300 border-t-blue-500 animate-spin" />
                    {t("head.saving")}
                  </>
                ) : lastSaved ? (
                  <>
                    <svg className="w-3 h-3 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
                    {t("head.saved")} {lastSaved}
                  </>
                ) : (
                  <>
                    <span className="w-3 h-3 rounded-full border border-slate-300 dark:border-slate-600" />
                    {t("head.autosave")}
                  </>
                )}
              </div>

              {/* language selector */}
              <div className="flex items-center gap-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-0.5">
                {(["en", "hi"] as Lang[]).map(l => (
                  <button key={l} onClick={() => switchLang(l)}
                          className={"px-2.5 py-1 text-xs font-medium rounded-md transition-colors " +
                            (lang === l
                              ? "bg-blue-600 text-white"
                              : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800")}>
                    {l === "en" ? "EN" : "HI"}
                  </button>
                ))}
              </div>

              <Link href={"/intake/" + patientId + "/documents"}
                    className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                {t("head.docs")}
              </Link>
            </div>
          </div>

          {/* progress bar */}
          <div className="mt-3 flex items-center gap-3">
            <div className="flex-1 h-1.5 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500"
                   style={{ width: progress + "%" }} />
            </div>
            <span className="text-xs font-medium text-slate-600 dark:text-slate-400 tabular-nums whitespace-nowrap">
              {progress}% - {answeredCount}/{totalQuestions}
            </span>
          </div>
        </div>
      </header>

      {/* ---------- questionnaire body ---------- */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-6">{t("head.subtitle")}</p>

        {q.sections.map((section, si) => {
          const stat = sectionStats[section.id] ?? { answered: 0, total: 0 };
          const sectionDone = stat.total > 0 && stat.answered === stat.total;

          return (
            <section
              key={section.id}
              ref={el => { sectionsRef.current[section.id] = el; }}
              className="mb-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden"
            >
              {/* section header */}
              <header className="flex items-center gap-3 px-5 py-4 border-b border-slate-100 dark:border-slate-800">
                <div className={"w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 transition-colors " +
                  (sectionDone
                    ? "bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300")}>
                  {sectionDone ? (
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  ) : String(si + 1).padStart(2, "0")}
                </div>
                <div className="flex-1 min-w-0">
                  <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                    {lang === "en" ? section.title_en : section.title_hi}
                  </h2>
                </div>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 tabular-nums whitespace-nowrap">
                  {stat.answered} / {stat.total}
                </span>
              </header>

              {/* questions */}
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {section.questions.filter(isVisible).map(question => (
                  <QuestionRow
                    key={question.id}
                    question={question}
                    lang={lang}
                    value={answers[question.id] ?? null}
                    onChange={(v, src, conf) => saveAnswer(question.id, v, src, conf)}
                    saving={saving === question.id}
                    t={t}
                  />
                ))}
              </div>
            </section>
          );
        })}

        {/* ---------- complete ---------- */}
        <div className="mt-8 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 flex items-center justify-between gap-4 flex-wrap">
          <div>
            <div className="text-sm font-semibold text-slate-900 dark:text-white">{t("submit.title")}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{t("submit.hint")}</div>
          </div>
          <button onClick={complete}
                  className="px-5 py-2.5 rounded-lg text-sm font-medium bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/30 hover:shadow-lg active:scale-[0.98] transition-all">
            {t("submit.title")}
          </button>
        </div>

        {err && (
          <div className="mt-4 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-sm text-red-800 dark:text-red-300">
            {err}
          </div>
        )}
      </div>
    </main>
  );
}

/* ============ question row ============ */

function QuestionRow({
  question, lang, value, onChange, saving, t,
}: {
  question: Question;
  lang: Lang;
  value: any;
  onChange: (v: any, source?: "touch" | "voice", confidence?: number) => void;
  saving: boolean;
  t: (k: string) => string;
}) {
  const label = lang === "en" ? question.text_en : question.text_hi;
  const opts = question.options ?? [];
  const showMic = question.type === "text" || question.type === "yes_no";

  return (
    <div className="px-5 py-5 hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <label className="text-sm font-medium text-slate-800 dark:text-slate-100 leading-snug">
          {label}
          {question.required && <span className="text-red-500 ml-1">*</span>}
        </label>
        <div className="flex items-center gap-2 shrink-0">
          {showMic && (
            <MicButton language={lang}
                       onResult={(text, conf) => {
                         if (question.type === "yes_no") {
                           const tt = text.toLowerCase();
                           const isYes = /\b(yes|yeah|yep|haan|ha|\u0939\u093e\u0901|\u0939\u093e\u0902|\u0939\u093e)\b/i.test(tt);
                           const isNo  = /\b(no|nope|nahi|\u0928\u0939\u0940\u0902|\u0928\u0939\u0940)\b/i.test(tt);
                           if (isYes) return onChange("yes", "voice", conf);
                           if (isNo)  return onChange("no", "voice", conf);
                           return onChange(text, "voice", conf);
                         }
                         onChange(text, "voice", conf);
                       }}
                       labels={{ speak: t("voice.speak"), stop: t("voice.stop"), listening: t("voice.listening"), error: t("voice.error") }} />
          )}
          {saving && (
            <span className="w-3.5 h-3.5 rounded-full border-2 border-slate-200 border-t-blue-500 animate-spin" />
          )}
        </div>
      </div>

      <div className="mt-3">
        {question.type === "text" && (
          <textarea value={value ?? ""} onChange={e => onChange(e.target.value, "touch")}
                    onBlur={e => onChange(e.target.value, "touch")}
                    rows={2}
                    className="w-full rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-colors resize-none" />
        )}

        {question.type === "duration" && (
          <div className="flex gap-2">
            <input type="number" min={0} placeholder="0"
                   value={(value && value.value) || ""}
                   onChange={e => onChange({ value: e.target.value, unit: (value && value.unit) || "days" }, "touch")}
                   className="w-28 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20" />
            <select value={(value && value.unit) || "days"}
                    onChange={e => onChange({ value: (value && value.value) || "", unit: e.target.value }, "touch")}
                    className="rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20">
              <option value="hours">hours</option>
              <option value="days">days</option>
              <option value="weeks">weeks</option>
              <option value="months">months</option>
              <option value="years">years</option>
            </select>
          </div>
        )}

        {question.type === "single_choice" && (
          <div className="flex flex-wrap gap-2">
            {opts.map(o => {
              const selected = value === o.value;
              return (
                <button key={o.value} type="button" onClick={() => onChange(o.value, "touch")}
                        className={"px-3.5 py-2 rounded-lg border text-sm font-medium transition-all active:scale-[0.98] " +
                          (selected
                            ? "border-blue-500 bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 ring-1 ring-blue-500/30"
                            : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600")}>
                  {lang === "en" ? o.label_en : o.label_hi}
                </button>
              );
            })}
          </div>
        )}

        {question.type === "multi_choice" && (
          <div className="flex flex-wrap gap-2">
            {opts.map(o => {
              const arr: string[] = Array.isArray(value) ? value : [];
              const selected = arr.includes(o.value);
              return (
                <button key={o.value} type="button"
                        onClick={() => {
                          const next = selected ? arr.filter(x => x !== o.value) : [...arr, o.value];
                          onChange(next, "touch");
                        }}
                        className={"px-3.5 py-2 rounded-lg border text-sm font-medium transition-all active:scale-[0.98] " +
                          (selected
                            ? "border-blue-500 bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 ring-1 ring-blue-500/30"
                            : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600")}>
                  {lang === "en" ? o.label_en : o.label_hi}
                </button>
              );
            })}
          </div>
        )}

        {question.type === "yes_no" && (
          <div className="flex gap-2">
            {["yes", "no"].map(v => {
              const selected = value === v;
              const text = v === "yes"
                ? (lang === "en" ? "Yes" : "\u0939\u093e\u0901")
                : (lang === "en" ? "No" : "\u0928\u0939\u0940\u0902");
              return (
                <button key={v} type="button" onClick={() => onChange(v, "touch")}
                        className={"px-4 py-2 rounded-lg border text-sm font-medium transition-all active:scale-[0.98] " +
                          (selected
                            ? "border-blue-500 bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 ring-1 ring-blue-500/30"
                            : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 hover:border-slate-300")}>
                  {text}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
"""

out = Path("src/app/intake/[patientId]/page.tsx")
out.write_text(tsx.lstrip(), encoding="utf-8")
print("WROTE", out)
print("bytes:", out.stat().st_size)

raw = out.read_text(encoding="utf-8")
non_ascii = [c for c in raw if ord(c) > 127]
print("non-ASCII chars:", len(non_ascii))
