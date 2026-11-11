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
  "crumb.home":   { en: "Home",               hi: "\u0939\u094b\u092e" },
  "crumb.q":      { en: "Questionnaire",      hi: "\u092a\u094d\u0930\u0936\u094d\u0928\u093e\u0935\u0932\u0940" },
  "head.title":   { en: "General Medicine Intake", hi: "\u0938\u093e\u092e\u093e\u0928\u094d\u092f \u091a\u093f\u0915\u093f\u0924\u094d\u0938\u093e \u092a\u094d\u0930\u0935\u0947\u0936" },
  "head.sub":     { en: "Answer what you can. You may skip any question.", hi: "\u091c\u093f\u0924\u0928\u093e \u0938\u0902\u092d\u0935 \u0939\u094b \u0909\u0924\u094d\u0924\u0930 \u0926\u0947\u0902\u0964 \u0915\u094b\u0908 \u092d\u0940 \u092a\u094d\u0930\u0936\u094d\u0928 \u091b\u094b\u0921\u093c \u0938\u0915\u0924\u0947 \u0939\u0948\u0902\u0964" },
  "head.docs":    { en: "Upload documents",   hi: "\u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c\u093c \u0905\u092a\u0932\u094b\u0921" },
  "head.saving":  { en: "Saving",             hi: "\u0938\u0939\u0947\u091c \u0930\u0939\u0947" },
  "head.saved":   { en: "Saved",              hi: "\u0938\u0939\u0947\u091c\u093e" },
  "head.auto":    { en: "Auto-save on",       hi: "\u0938\u094d\u0935\u091a\u093e\u0932\u093f\u0924 \u0938\u0939\u0947\u091c" },
  "submit":       { en: "Complete and upload documents", hi: "\u092a\u0942\u0930\u094d\u0923 \u0915\u0930\u0947\u0902 \u0914\u0930 \u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c\u093c \u0905\u092a\u0932\u094b\u0921 \u0915\u0930\u0947\u0902" },
  "submit.hint":  { en: "You can return and edit before your consultation.", hi: "\u0905\u092a\u0928\u0940 \u092a\u0930\u093e\u092e\u0930\u094d\u0936 \u0938\u0947 \u092a\u0939\u0932\u0947 \u0906\u092a \u0935\u093e\u092a\u0938 \u0906\u0915\u0930 \u0938\u0902\u092a\u093e\u0926\u093f\u0924 \u0915\u0930 \u0938\u0915\u0924\u0947 \u0939\u0948\u0902\u0964" },
  "loading":      { en: "Loading questionnaire...", hi: "\u092a\u094d\u0930\u0936\u094d\u0928\u093e\u0935\u0932\u0940 \u0932\u094b\u0921 \u0939\u094b \u0930\u0939\u0940 \u0939\u0948..." },
  "section.done": { en: "Complete",           hi: "\u092a\u0942\u0930\u094d\u0923" },
  "voice.speak":  { en: "Speak",              hi: "\u092c\u094b\u0932\u0947\u0902" },
  "voice.stop":   { en: "Stop",               hi: "\u0930\u094b\u0915\u0947\u0902" },
  "voice.listen": { en: "Listening",          hi: "\u0938\u0941\u0928 \u0930\u0939\u0947" },
  "voice.err":    { en: "Microphone error",   hi: "\u092e\u093e\u0907\u0915 \u0924\u094d\u0930\u0941\u091f\u093f" },
};

const SECTION_ACCENTS = [
  { bg: "from-blue-500 to-indigo-500",     ring: "ring-blue-500/20",     bg50: "bg-blue-50 dark:bg-blue-950/40",     text: "text-blue-700 dark:text-blue-300" },
  { bg: "from-purple-500 to-fuchsia-500",  ring: "ring-purple-500/20",   bg50: "bg-purple-50 dark:bg-purple-950/40", text: "text-purple-700 dark:text-purple-300" },
  { bg: "from-pink-500 to-rose-500",       ring: "ring-pink-500/20",     bg50: "bg-pink-50 dark:bg-pink-950/40",     text: "text-pink-700 dark:text-pink-300" },
  { bg: "from-amber-500 to-orange-500",    ring: "ring-amber-500/20",    bg50: "bg-amber-50 dark:bg-amber-950/40",   text: "text-amber-700 dark:text-amber-300" },
  { bg: "from-emerald-500 to-teal-500",    ring: "ring-emerald-500/20",  bg50: "bg-emerald-50 dark:bg-emerald-950/40", text: "text-emerald-700 dark:text-emerald-300" },
  { bg: "from-cyan-500 to-blue-500",       ring: "ring-cyan-500/20",     bg50: "bg-cyan-50 dark:bg-cyan-950/40",     text: "text-cyan-700 dark:text-cyan-300" },
  { bg: "from-violet-500 to-purple-500",   ring: "ring-violet-500/20",   bg50: "bg-violet-50 dark:bg-violet-950/40", text: "text-violet-700 dark:text-violet-300" },
];

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

  const t = (k: string) => UI[k]?.[lang] ?? k;

  useEffect(() => {
    (async () => {
      try {
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

        const qr = await fetch("/api/v1/questionnaires/gm_v1?lang=" + chosen).then(r => r.json());
        setQ(qr);

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

  const allQuestions = useMemo(() => (q ? q.sections.flatMap(s => s.questions) : []), [q]);
  const totalQuestions = allQuestions.length;

  function isVisible(question: Question) {
    if (!question.visible_if) return true;
    return String(answers[question.visible_if.question_id]) === question.visible_if.equals;
  }

  function isAnswered(question: Question) {
    const v = answers[question.id];
    if (v === null || v === undefined) return false;
    if (typeof v === "string" && v.trim() === "") return false;
    if (Array.isArray(v) && v.length === 0) return false;
    if (typeof v === "object" && v.value === "" && v.unit === "") return false;
    return true;
  }

  const answeredCount = useMemo(
    () => allQuestions.filter(qq => isVisible(qq) && isAnswered(qq)).length,
    // eslint-disable-next-line
    [answers, allQuestions]
  );

  const progress = totalQuestions ? Math.round((answeredCount / totalQuestions) * 100) : 0;

  const sectionStats = useMemo(() => {
    const stats: Record<string, { answered: number; total: number }> = {};
    for (const s of q?.sections ?? []) {
      let a = 0, tot = 0;
      for (const qq of s.questions) {
        if (!isVisible(qq)) continue;
        tot += 1;
        if (isAnswered(qq)) a += 1;
      }
      stats[s.id] = { answered: a, total: tot };
    }
    return stats;
    // eslint-disable-next-line
  }, [q, answers]);

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
  if (!q || !session) return <main className="p-8">{t("loading")}</main>;

  return (
    <main className="relative min-h-screen bg-slate-50 dark:bg-[#070b18] pb-32">
      {/* ambient */}
      <div aria-hidden className="pointer-events-none absolute inset-x-0 top-0 h-96"
           style={{ background: "radial-gradient(50% 60% at 50% 0%, rgba(59,130,246,0.10), transparent 70%)" }} />

      {/* ---------- sticky header ---------- */}
      <header className="sticky top-0 z-30 bg-white/85 dark:bg-slate-900/85 backdrop-blur border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-4xl mx-auto px-6 py-3.5">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="min-w-0">
              <nav className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
                <Link href="/" className="hover:text-slate-900 dark:hover:text-white">{t("crumb.home")}</Link>
                <span className="opacity-50">/</span>
                <span className="text-slate-900 dark:text-white font-medium">{t("crumb.q")}</span>
              </nav>
              <h1 className="mt-0.5 text-lg font-semibold text-slate-900 dark:text-white tracking-tight">
                {t("head.title")}
              </h1>
            </div>

            <div className="flex items-center gap-3 flex-wrap">
              {/* save indicator */}
              <div className="hidden sm:flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400">
                {saving ? (
                  <><span className="w-3 h-3 rounded-full border-2 border-slate-300 border-t-blue-500 animate-spin" />{t("head.saving")}</>
                ) : lastSaved ? (
                  <><svg className="w-3 h-3 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>{t("head.saved")} {lastSaved}</>
                ) : (
                  <><span className="w-3 h-3 rounded-full border border-slate-300 dark:border-slate-600" />{t("head.auto")}</>
                )}
              </div>

              <div className="flex items-center gap-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-0.5">
                {(["en", "hi"] as Lang[]).map(l => (
                  <button key={l} onClick={() => switchLang(l)}
                          className={"px-2.5 py-1 text-xs font-semibold rounded-md transition-colors " +
                            (lang === l ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900" : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800")}>
                    {l === "en" ? "EN" : "HI"}
                  </button>
                ))}
              </div>

              <Link href={"/intake/" + patientId + "/documents"}
                    className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-xs font-medium hover:bg-slate-800 dark:hover:bg-slate-100 transition-colors">
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                {t("head.docs")}
              </Link>
            </div>
          </div>
        </div>

        {/* progress track (full width of header) */}
        <div className="max-w-4xl mx-auto px-6 pb-3 flex items-center gap-3">
          <div className="relative flex-1 h-2 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
            <div className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 transition-all duration-700"
                 style={{ width: progress + "%" }} />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-900 dark:text-white tabular-nums">{progress}%</span>
            <span className="text-[11px] text-slate-500 dark:text-slate-400 tabular-nums">{answeredCount}/{totalQuestions}</span>
          </div>
        </div>
      </header>

      {/* ---------- body ---------- */}
      <div className="relative max-w-4xl mx-auto px-6 py-8">
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-8 max-w-2xl">{t("head.sub")}</p>

        {q.sections.map((section, si) => {
          const accent = SECTION_ACCENTS[si % SECTION_ACCENTS.length];
          const stat = sectionStats[section.id] ?? { answered: 0, total: 0 };
          const pct = stat.total > 0 ? Math.round((stat.answered / stat.total) * 100) : 0;
          const sectionDone = stat.total > 0 && stat.answered === stat.total;

          return (
            <section key={section.id} className="mb-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden shadow-sm">
              {/* header */}
              <header className="relative">
                {/* top gradient hairline */}
                <div className={"absolute inset-x-0 top-0 h-1 bg-gradient-to-r " + accent.bg} />
                <div className="flex items-center gap-4 px-5 py-4">
                  <div className={"relative w-11 h-11 rounded-xl flex items-center justify-center text-sm font-bold shrink-0 bg-gradient-to-br text-white shadow-md transition-all " + accent.bg}>
                    {sectionDone ? (
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    ) : (
                      <span>{String(si + 1).padStart(2, "0")}</span>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                        {lang === "en" ? section.title_en : section.title_hi}
                      </h2>
                      {sectionDone && (
                        <span className={"text-[10px] uppercase tracking-widest font-semibold " + accent.text}>
                          {t("section.done")}
                        </span>
                      )}
                    </div>
                    <div className="mt-2 flex items-center gap-2">
                      <div className="flex-1 h-1 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                        <div className={"h-full rounded-full bg-gradient-to-r transition-all duration-500 " + accent.bg}
                             style={{ width: pct + "%" }} />
                      </div>
                      <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 tabular-nums">
                        {stat.answered}/{stat.total}
                      </span>
                    </div>
                  </div>
                </div>
              </header>

              {/* questions */}
              <div className="border-t border-slate-100 dark:border-slate-800">
                {section.questions.filter(isVisible).map((question, qi) => {
                  const answered = isAnswered(question);
                  return (
                    <div
                      key={question.id}
                      className={
                        "px-5 py-5 transition-colors " +
                        (qi > 0 ? "border-t border-slate-100 dark:border-slate-800 " : "") +
                        (answered ? "bg-slate-50/40 dark:bg-slate-800/20" : "")
                      }
                    >
                      <div className="flex items-start gap-3">
                        {/* answered check icon */}
                        <div className={"mt-0.5 w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0 transition-all " +
                          (answered
                            ? "border-emerald-500 bg-emerald-500"
                            : "border-slate-200 dark:border-slate-700 bg-transparent")}>
                          {answered && (
                            <svg className="w-2.5 h-2.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                              <polyline points="20 6 9 17 4 12" />
                            </svg>
                          )}
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-3">
                            <label className="text-sm font-medium text-slate-800 dark:text-slate-100 leading-snug">
                              {lang === "en" ? question.text_en : question.text_hi}
                              {question.required && <span className="text-red-500 ml-1">*</span>}
                            </label>
                            <div className="flex items-center gap-2 shrink-0">
                              {(question.type === "text" || question.type === "yes_no") && (
                                <MicButton language={lang}
                                  onResult={(text, conf) => {
                                    if (question.type === "yes_no") {
                                      const tt = text.toLowerCase();
                                      const isYes = /\b(yes|yeah|yep|haan|ha|\u0939\u093e\u0901|\u0939\u093e\u0902|\u0939\u093e)\b/i.test(tt);
                                      const isNo  = /\b(no|nope|nahi|\u0928\u0939\u0940\u0902|\u0928\u0939\u0940)\b/i.test(tt);
                                      if (isYes) return onChangeWrapper(question.id, "yes", "voice", conf);
                                      if (isNo)  return onChangeWrapper(question.id, "no",  "voice", conf);
                                      return onChangeWrapper(question.id, text, "voice", conf);
                                    }
                                    onChangeWrapper(question.id, text, "voice", conf);
                                  }}
                                  labels={{ speak: t("voice.speak"), stop: t("voice.stop"), listening: t("voice.listen"), error: t("voice.err") }}
                                />
                              )}
                              {saving === question.id && (
                                <span className="w-3.5 h-3.5 rounded-full border-2 border-slate-200 border-t-blue-500 animate-spin" />
                              )}
                            </div>
                          </div>

                          <div className="mt-3">
                            <QuestionInput
                              question={question}
                              lang={lang}
                              value={answers[question.id] ?? null}
                              onChange={(v) => onChangeWrapper(question.id, v, "touch")}
                              accent={accent}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          );
        })}

        {err && (
          <div className="mt-6 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-sm text-red-800 dark:text-red-300">
            {err}
          </div>
        )}
      </div>

      {/* ---------- sticky bottom CTA ---------- */}
      <div className="fixed bottom-0 left-0 right-0 z-30 bg-white/90 dark:bg-slate-900/90 backdrop-blur border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-4xl mx-auto px-6 py-3 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="hidden sm:block">
              <div className="text-xs font-medium text-slate-500 dark:text-slate-400">
                {t("submit.hint")}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500 dark:text-slate-400 tabular-nums">
              {answeredCount}/{totalQuestions}
            </span>
            <button onClick={complete}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/30 hover:shadow-lg hover:shadow-blue-500/40 active:scale-[0.98] transition-all">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              {t("submit")}
            </button>
          </div>
        </div>
      </div>
    </main>
  );

  function onChangeWrapper(questionId: string, value: any, source: "touch" | "voice", conf?: number) {
    saveAnswer(questionId, value, source, conf);
  }
}

/* ============ question input ============ */

function QuestionInput({
  question, lang, value, onChange, accent,
}: {
  question: Question;
  lang: Lang;
  value: any;
  onChange: (v: any) => void;
  accent: typeof SECTION_ACCENTS[number];
}) {
  const opts = question.options ?? [];

  if (question.type === "text") {
    return (
      <textarea
        value={value ?? ""}
        onChange={e => onChange(e.target.value)}
        onBlur={e => onChange(e.target.value)}
        rows={2}
        placeholder={lang === "en" ? "Type or use the mic..." : "\u0932\u093f\u0916\u0947\u0902 \u092f\u093e \u092e\u093e\u0907\u0915 \u0909\u092a\u092f\u094b\u0917 \u0915\u0930\u0947\u0902..."}
        className="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-4 py-3 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:border-slate-400 dark:focus:border-slate-500 focus:ring-2 focus:ring-slate-900/5 dark:focus:ring-white/5 transition-all resize-none"
      />
    );
  }

  if (question.type === "duration") {
    return (
      <div className="flex gap-2">
        <input
          type="number"
          min={0}
          placeholder="0"
          value={(value && value.value) || ""}
          onChange={e => onChange({ value: e.target.value, unit: (value && value.unit) || "days" })}
          className="w-28 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-4 py-3 text-sm text-slate-900 dark:text-white focus:outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-900/5 transition-all"
        />
        <select
          value={(value && value.unit) || "days"}
          onChange={e => onChange({ value: (value && value.value) || "", unit: e.target.value })}
          className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 px-4 py-3 text-sm text-slate-900 dark:text-white focus:outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-900/5 transition-all"
        >
          <option value="hours">hours</option>
          <option value="days">days</option>
          <option value="weeks">weeks</option>
          <option value="months">months</option>
          <option value="years">years</option>
        </select>
      </div>
    );
  }

  if (question.type === "single_choice") {
    return (
      <div className="flex flex-wrap gap-2">
        {opts.map(o => {
          const selected = value === o.value;
          return (
            <button key={o.value} type="button" onClick={() => onChange(o.value)}
                    className={
                      "group inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-all active:scale-[0.98] " +
                      (selected
                        ? "border-slate-900 dark:border-white bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-sm"
                        : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-700 dark:text-slate-200 hover:border-slate-400 dark:hover:border-slate-500")
                    }>
              <span className={
                "w-4 h-4 rounded-full border-2 flex items-center justify-center transition-colors " +
                (selected ? "border-white dark:border-slate-900" : "border-slate-300 dark:border-slate-600")
              }>
                {selected && <span className="w-2 h-2 rounded-full bg-white dark:bg-slate-900" />}
              </span>
              {lang === "en" ? o.label_en : o.label_hi}
            </button>
          );
        })}
      </div>
    );
  }

  if (question.type === "multi_choice") {
    return (
      <div className="flex flex-wrap gap-2">
        {opts.map(o => {
          const arr: string[] = Array.isArray(value) ? value : [];
          const selected = arr.includes(o.value);
          return (
            <button key={o.value} type="button"
                    onClick={() => {
                      const next = selected ? arr.filter(x => x !== o.value) : [...arr, o.value];
                      onChange(next);
                    }}
                    className={
                      "inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-all active:scale-[0.98] " +
                      (selected
                        ? "border-slate-900 dark:border-white bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-sm"
                        : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-700 dark:text-slate-200 hover:border-slate-400 dark:hover:border-slate-500")
                    }>
              <span className={
                "w-4 h-4 rounded-md border-2 flex items-center justify-center transition-colors " +
                (selected ? "border-white dark:border-slate-900 bg-white dark:bg-slate-900" : "border-slate-300 dark:border-slate-600")
              }>
                {selected && (
                  <svg className="w-2.5 h-2.5 text-slate-900 dark:text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                )}
              </span>
              {lang === "en" ? o.label_en : o.label_hi}
            </button>
          );
        })}
      </div>
    );
  }

  if (question.type === "yes_no") {
    return (
      <div className="flex gap-2">
        {(["yes", "no"] as const).map(v => {
          const selected = value === v;
          const text = v === "yes"
            ? (lang === "en" ? "Yes" : "\u0939\u093e\u0901")
            : (lang === "en" ? "No" : "\u0928\u0939\u0940\u0902");
          return (
            <button key={v} type="button" onClick={() => onChange(v)}
                    className={
                      "px-6 py-2.5 rounded-xl border text-sm font-semibold transition-all active:scale-[0.98] " +
                      (selected
                        ? (v === "yes"
                          ? "border-emerald-500 bg-emerald-500 text-white shadow-sm shadow-emerald-500/30"
                          : "border-slate-900 dark:border-white bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-sm")
                        : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-700 dark:text-slate-200 hover:border-slate-400 dark:hover:border-slate-500")
                    }>
              {text}
            </button>
          );
        })}
      </div>
    );
  }

  return null;
}
"""

out = Path("src/app/intake/[patientId]/page.tsx")
out.write_text(tsx.lstrip(), encoding="utf-8")
print("WROTE", out)
print("bytes:", out.stat().st_size)

raw = out.read_text(encoding="utf-8")
non_ascii = [c for c in raw if ord(c) > 127]
print("non-ASCII chars:", len(non_ascii))
