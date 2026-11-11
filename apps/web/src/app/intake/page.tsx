"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiPost } from "@/lib/api";

type Lang = "en" | "hi";

type ExistingPatient = {
  id: string;
  synthetic_id: string;
  preferred_language: string;
  created_at: string;
};

type ExistingSummary = {
  documents: number;
  facts: number;
  timeline_events: number;
  sessions: number;
};

const TRANSLATIONS: Record<string, { en: string; hi: string }> = {
  "crumb.home": { en: "Home", hi: "\u0939\u094b\u092e" },
  "crumb.intake": { en: "Patient intake", hi: "\u0930\u094b\u0917\u0940 \u092a\u094d\u0930\u0935\u0947\u0936" },
  "page.title": { en: "Patient intake", hi: "\u0930\u094b\u0917\u0940 \u092a\u094d\u0930\u0935\u0947\u0936" },
  "page.badge": { en: "On-premises processing", hi: "\u0938\u094d\u0925\u093e\u0928\u0940\u092f \u092a\u094d\u0930\u0915\u094d\u0930\u093f\u092f\u093e" },
  "page.subtitle": { en: "Complete this short form before your consultation. Information is summarized for your physician.",
                     hi: "\u0905\u092a\u0928\u0940 \u092a\u0930\u093e\u092e\u0930\u094d\u0936 \u0938\u0947 \u092a\u0939\u0932\u0947 \u092f\u0939 \u0938\u0902\u0915\u094d\u0937\u093f\u092a\u094d\u0924 \u092b\u0949\u0930\u094d\u092e \u092d\u0930\u0947\u0902\u0964" },
  "s1.title": { en: "Preferred language", hi: "\u092a\u0938\u0902\u0926\u0940\u0926\u093e \u092d\u093e\u0937\u093e" },
  "s1.desc": { en: "Choose the language you are most comfortable with.",
               hi: "\u0935\u0939 \u092d\u093e\u0937\u093e \u091a\u0941\u0928\u0947\u0902 \u091c\u093f\u0938\u092e\u0947\u0902 \u0906\u092a \u0938\u0939\u091c \u0939\u0948\u0902\u0964" },
  "s1.en": { en: "English", hi: "English" },
  "s1.hi": { en: "Hindi", hi: "\u0939\u093f\u0928\u094d\u0926\u0940" },
  "s2.title": { en: "Patient identifier", hi: "\u0930\u094b\u0917\u0940 \u092a\u0939\u091a\u093e\u0928\u0915\u0930\u094d\u0924\u093e" },
  "s2.desc": { en: "Enter the identifier from your hospital slip or appointment letter.",
               hi: "\u0905\u0938\u094d\u092a\u0924\u093e\u0932 \u0915\u0940 \u092a\u0930\u094d\u091a\u0940 \u092f\u093e \u0905\u092a\u0949\u0907\u0902\u091f\u092e\u0947\u0902\u091f \u0932\u0947\u091f\u0930 \u0938\u0947 \u092a\u0939\u091a\u093e\u0928\u0915\u0930\u094d\u0924\u093e \u0926\u0930\u094d\u091c \u0915\u0930\u0947\u0902\u0964" },
  "s2.label": { en: "Patient ID", hi: "\u0930\u094b\u0917\u0940 \u0906\u0908\u0921\u0940" },
  "s2.generate": { en: "Generate", hi: "\u092c\u0928\u093e\u090f\u0902" },
  "s2.hint": { en: "We will look up your existing record if you have visited us before.",
               hi: "\u092f\u0926\u093f \u0906\u092a \u092a\u0939\u0932\u0947 \u0906 \u091a\u0941\u0915\u0947 \u0939\u0948\u0902 \u0924\u094b \u0939\u092e \u0906\u092a\u0915\u093e \u0930\u093f\u0915\u0949\u0930\u094d\u0921 \u0922\u0942\u0902\u0922 \u0932\u0947\u0902\u0917\u0947\u0964" },
  "s2.found": { en: "Existing patient found", hi: "\u092e\u094c\u091c\u0942\u0926\u093e \u0930\u094b\u0917\u0940 \u092e\u093f\u0932\u093e" },
  "s2.welcome_back": { en: "Welcome back", hi: "\u0935\u093e\u092a\u0938\u0940 \u092a\u0930 \u0938\u094d\u0935\u093e\u0917\u0924 \u0939\u0948" },
  "s2.member_since": { en: "Member since", hi: "\u0938\u0926\u0938\u094d\u092f\u0924\u093e \u0938\u0947" },
  "s2.loading": { en: "Looking up...", hi: "\u0926\u0947\u0916 \u0930\u0939\u0947 \u0939\u0948\u0902..." },
  "s2.new_patient": { en: "New patient", hi: "\u0928\u092f\u093e \u0930\u094b\u0917\u0940" },
  "s2.reset_id": { en: "Use different ID", hi: "\u0905\u0932\u0917 \u0906\u0908\u0921\u0940 \u0909\u092a\u092f\u094b\u0917 \u0915\u0930\u0947\u0902" },
  "s3.title": { en: "Consent", hi: "\u0938\u0939\u092e\u0924\u093f" },
  "s3.desc": { en: "Your consent is required before we can record your information.",
               hi: "\u0906\u092a\u0915\u0940 \u091c\u093e\u0928\u0915\u093e\u0930\u0940 \u0926\u0930\u094d\u091c \u0915\u0930\u0928\u0947 \u0938\u0947 \u092a\u0939\u0932\u0947 \u0906\u092a\u0915\u0940 \u0938\u0939\u092e\u0924\u093f \u0906\u0935\u0936\u094d\u092f\u0915 \u0939\u0948\u0964" },
  "s3.consent_title": { en: "I consent to pre-consultation intake",
                        hi: "\u092e\u0948\u0902 \u092a\u0930\u093e\u092e\u0930\u094d\u0936-\u092a\u0942\u0930\u094d\u0935 \u092a\u094d\u0930\u0935\u0947\u0936 \u0915\u0947 \u0932\u093f\u090f \u0938\u0939\u092e\u0924\u093f \u0926\u0947\u0924\u093e/\u0926\u0947\u0924\u0940 \u0939\u0942\u0902" },
  "s3.consent_body": { en: "My responses and documents are processed on this device to prepare a summary for my physician. This is a documentation aid, not a diagnosis. I may revoke consent at any time.",
                       hi: "\u092e\u0947\u0930\u0947 \u0909\u0924\u094d\u0924\u0930 \u0914\u0930 \u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c\u093c \u0907\u0938 \u0921\u093f\u0935\u093e\u0907\u0938 \u092a\u0930 \u0938\u0902\u0938\u093e\u0927\u093f\u0924 \u0939\u094b\u0924\u0947 \u0939\u0948\u0902\u0964 \u092e\u0948\u0902 \u0915\u092d\u0940 \u092d\u0940 \u0938\u0939\u092e\u0924\u093f \u0935\u093e\u092a\u0938 \u0932\u0947 \u0938\u0915\u0924\u093e/\u0938\u0915\u0924\u0940 \u0939\u0942\u0902\u0964" },
  "s3.bullet1": { en: "Data processed on this device only",
                  hi: "\u0921\u0947\u091f\u093e \u0915\u0947\u0935\u0932 \u0907\u0938 \u0921\u093f\u0935\u093e\u0907\u0938 \u092a\u0930" },
  "s3.bullet2": { en: "No transfer to cloud services",
                  hi: "\u0915\u094d\u0932\u093e\u0909\u0921 \u0938\u094d\u0925\u093e\u0928\u093e\u0902\u0924\u0930\u0923 \u0928\u0939\u0940\u0902" },
  "s3.bullet3": { en: "Consent revocable at any time",
                  hi: "\u0938\u0939\u092e\u0924\u093f \u0915\u092d\u0940 \u092d\u0940 \u0930\u0926\u094d\u0926" },
  "s3.bullet4": { en: "Aligned with DPDP Act 2023",
                  hi: "DPDP \u0905\u0927\u093f\u0928\u093f\u092f\u092e 2023" },
  "submit.ready": { en: "Ready to continue", hi: "\u091c\u093e\u0930\u0940 \u0930\u0916\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f \u0924\u0948\u092f\u093e\u0930" },
  "submit.ready_desc": { en: "All required fields are complete.", hi: "\u0938\u092d\u0940 \u092b\u0940\u0932\u094d\u0921 \u092a\u0942\u0930\u094d\u0923" },
  "submit.not_ready": { en: "Incomplete form", hi: "\u0905\u092a\u0942\u0930\u094d\u0923 \u092b\u0949\u0930\u094d\u092e" },
  "submit.not_ready_desc": { en: "Complete all required fields.", hi: "\u0938\u092d\u0940 \u092b\u0940\u0932\u094d\u0921 \u092a\u0942\u0930\u094d\u0923 \u0915\u0930\u0947\u0902" },
  "submit.cancel": { en: "Cancel", hi: "\u0930\u0926\u094d\u0926 \u0915\u0930\u0947\u0902" },
  "submit.continue": { en: "Continue", hi: "\u091c\u093e\u0930\u0940 \u0930\u0916\u0947\u0902" },
  "submit.continue_existing": { en: "Continue as existing patient", hi: "\u092e\u094c\u091c\u0942\u0926\u093e \u0930\u094b\u0917\u0940 \u0915\u0947 \u0930\u0942\u092a \u092e\u0947\u0902 \u091c\u093e\u0930\u0940 \u0930\u0916\u0947\u0902" },
  "card.title": { en: "Patient card", hi: "\u0930\u094b\u0917\u0940 \u0915\u093e\u0930\u094d\u0921" },
  "card.ready": { en: "Ready", hi: "\u0924\u0948\u092f\u093e\u0930" },
  "card.identifier": { en: "Identifier", hi: "\u092a\u0939\u091a\u093e\u0928\u0915\u0930\u094d\u0924\u093e" },
  "card.not_provided": { en: "not yet provided", hi: "\u0905\u092d\u0940 \u0924\u0915 \u0928\u0939\u0940\u0902" },
  "card.language": { en: "Language", hi: "\u092d\u093e\u0937\u093e" },
  "card.consent": { en: "Consent", hi: "\u0938\u0939\u092e\u0924\u093f" },
  "card.given": { en: "Given", hi: "\u0926\u0940 \u0917\u0908" },
  "card.not_yet": { en: "Not yet", hi: "\u0905\u092d\u0940 \u0928\u0939\u0940\u0902" },
  "card.attending": { en: "Attending", hi: "\u091a\u093f\u0915\u093f\u0924\u094d\u0938\u0915" },
  "card.pending": { en: "(pending)", hi: "(\u0932\u0902\u092c\u093f\u0924)" },
  "card.status_ready": { en: "status: ready to file", hi: "\u0938\u094d\u0925\u093f\u0924\u093f: \u0924\u0948\u092f\u093e\u0930" },
  "card.status_incomplete": { en: "status: incomplete", hi: "\u0938\u094d\u0925\u093f\u0924\u093f: \u0905\u092a\u0942\u0930\u094d\u0923" },
  "card.status_returning": { en: "status: returning patient", hi: "\u0938\u094d\u0925\u093f\u0924\u093f: \u0932\u094c\u091f\u0924\u093e \u0930\u094b\u0917\u0940" },
  "prev.title": { en: "Prior records on file", hi: "\u092a\u0942\u0930\u094d\u0935 \u0930\u093f\u0915\u0949\u0930\u094d\u0921" },
  "prev.documents": { en: "Documents", hi: "\u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c\u093c" },
  "prev.facts": { en: "Clinical facts", hi: "\u0928\u0948\u0926\u093e\u0928\u093f\u0915 \u0924\u0925\u094d\u092f" },
  "prev.events": { en: "Timeline events", hi: "\u091f\u093e\u0907\u092e\u0932\u093e\u0907\u0928 \u0917\u0924\u093f\u0935\u093f\u0927\u093f\u092f\u093e\u0902" },
  "prev.sessions": { en: "Prior visits", hi: "\u092a\u0939\u0932\u0947 \u0915\u0947 \u0926\u094c\u0930\u0947" },
  "prev.view_timeline": { en: "View full timeline", hi: "\u092a\u0942\u0930\u0940 \u091f\u093e\u0907\u092e\u0932\u093e\u0907\u0928 \u0926\u0947\u0916\u0947\u0902" },
  "next.title": { en: "What happens next", hi: "\u0906\u0917\u0947 \u0915\u094d\u092f\u093e \u0939\u094b\u0917\u093e" },
  "next.1.title": { en: "Complete this form", hi: "\u092f\u0939 \u092b\u0949\u0930\u094d\u092e \u092d\u0930\u0947\u0902" },
  "next.1.body": { en: "Takes about three minutes.", hi: "\u0932\u0917\u092d\u0917 \u0924\u0940\u0928 \u092e\u093f\u0928\u091f" },
  "next.2.title": { en: "Answer the questionnaire", hi: "\u092a\u094d\u0930\u0936\u094d\u0928\u093e\u0935\u0932\u0940" },
  "next.2.body": { en: "Structured General Medicine history.", hi: "\u0938\u0902\u0930\u091a\u093f\u0924 \u0907\u0924\u093f\u0939\u093e\u0938" },
  "next.3.title": { en: "Upload prior documents", hi: "\u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c\u093c \u0905\u092a\u0932\u094b\u0921" },
  "next.3.body": { en: "Optional. Read automatically.", hi: "\u0935\u0948\u0915\u0932\u094d\u092a\u093f\u0915\u0964" },
  "next.4.title": { en: "Physician review", hi: "\u091a\u093f\u0915\u093f\u0924\u094d\u0938\u0915 \u0938\u092e\u0940\u0915\u094d\u0937\u093e" },
  "next.4.body": { en: "Your doctor approves before your visit.", hi: "\u0921\u0949\u0915\u094d\u091f\u0930 \u0905\u0928\u0941\u092e\u094b\u0926\u093f\u0924 \u0915\u0930\u0924\u0947 \u0939\u0948\u0902" },
  "priv.title": { en: "Privacy & compliance", hi: "\u0917\u094b\u092a\u0928\u0940\u092f\u0924\u093e \u0914\u0930 \u0905\u0928\u0941\u092a\u093e\u0932\u0928" },
  "priv.location": { en: "Data location", hi: "\u0921\u0947\u091f\u093e \u0938\u094d\u0925\u093e\u0928" },
  "priv.location_val": { en: "This device", hi: "\u092f\u0939 \u0921\u093f\u0935\u093e\u0907\u0938" },
  "priv.cloud": { en: "Cloud transfer", hi: "\u0915\u094d\u0932\u093e\u0909\u0921" },
  "priv.cloud_val": { en: "None", hi: "\u0915\u094b\u0908 \u0928\u0939\u0940\u0902" },
  "priv.retention": { en: "Retention", hi: "\u092a\u094d\u0930\u0924\u093f\u0927\u093e\u0930\u0923" },
  "priv.retention_val": { en: "Until revocation", hi: "\u0930\u0926\u094d\u0926 \u0939\u094b\u0928\u0947 \u0924\u0915" },
  "priv.regulation": { en: "Regulation", hi: "\u0935\u093f\u0928\u093f\u092f\u092e\u0928" },
  "priv.regulation_val": { en: "DPDP Act 2023", hi: "DPDP 2023" },
  "priv.interop": { en: "Interoperability", hi: "\u0907\u0902\u091f\u0930\u0911\u092a" },
  "priv.interop_val": { en: "ABDM FHIR R4", hi: "ABDM FHIR R4" },
};

export default function IntakePage() {
  const router = useRouter();
  const [lang, setLang] = useState<Lang>("en");
  const [id, setId] = useState("");
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [focused, setFocused] = useState<"id" | null>(null);

  // lookup state
  const [looking, setLooking] = useState(false);
  const [existing, setExisting] = useState<ExistingPatient | null>(null);
  const [existingSummary, setExistingSummary] = useState<ExistingSummary | null>(null);
  const [idLocked, setIdLocked] = useState(false);
  const [autoRedirecting, setAutoRedirecting] = useState(false);

  const t = (k: string) => TRANSLATIONS[k]?.[lang] ?? k;

  useEffect(() => {
    setMounted(true);

    // On first load (no ID typed yet), pick up the browser's preferred language.
    // Anything starting with "hi" (hi, hi-IN, hi-Devanagari) -> Hindi, else English.
    try {
      const stored = window.localStorage.getItem("mg-intake-lang");
      if (stored === "en" || stored === "hi") {
        setLang(stored);
        return;
      }
      const nav = (navigator.language || "en").toLowerCase();
      if (nav.startsWith("hi")) {
        setLang("hi");
      } else {
        setLang("en");
      }
    } catch {
      // ignore - leave default
    }
  }, []);

  // ---------- AUTO FETCH EXISTING PATIENT ON ID CHANGE ----------
  const lookupTimer = useRef<NodeJS.Timeout | null>(null);
  useEffect(() => {
    if (lookupTimer.current) clearTimeout(lookupTimer.current);
    const trimmed = id.trim();
    if (!trimmed || idLocked) {
      if (!idLocked) setExisting(null);
      return;
    }
    lookupTimer.current = setTimeout(async () => {
      setLooking(true);
      try {
        const list: ExistingPatient[] = await fetch("/api/v1/patients").then(r => r.json());
        const match = list.find(p => p.synthetic_id.toLowerCase() === trimmed.toLowerCase());
        if (match) {
          setExisting(match);
          // Auto-switch UI language to patient's preferred language
          if (match.preferred_language === "hi" || match.preferred_language === "en") {
            setLang(match.preferred_language as Lang);
            try { window.localStorage.setItem("mg-intake-lang", match.preferred_language); } catch {}
          }
          // Fetch summary stats
          try {
            const docs = await fetch("/api/v1/documents?patient_id=" + match.id).then(r => r.json());
            const facts = await fetch("/api/v1/facts?patient_id=" + match.id).then(r => r.json());
            const tl = await fetch("/api/v1/timeline?patient_id=" + match.id).then(r => r.json());
            setExistingSummary({
              documents: Array.isArray(docs) ? docs.length : 0,
              facts: Array.isArray(facts) ? facts.length : 0,
              timeline_events: Array.isArray(tl) ? tl.length : 0,
              sessions: 0,
            });
          } catch {
            setExistingSummary({ documents: 0, facts: 0, timeline_events: 0, sessions: 0 });
          }
        } else {
          setExisting(null);
          setExistingSummary(null);
        }
      } catch {
        setExisting(null);
      } finally {
        setLooking(false);
      }
    }, 500);

    return () => {
      if (lookupTimer.current) clearTimeout(lookupTimer.current);
    };
    // eslint-disable-next-line
  }, [id, idLocked]);

  // Auto-redirect when an existing patient is detected
  useEffect(() => {
    if (!existing || idLocked) return;
    setIdLocked(true);
    let cancelled = false;
    (async () => {
      setAutoRedirecting(true);
      try {
        // Record a fresh consent for this visit
        await apiPost("/api/v1/patients/" + existing.id + "/consents", {
          purpose: "pre_consultation_intake",
          granted: true,
        });
        await new Promise(r => setTimeout(r, 1300));
        if (!cancelled) router.push("/intake/" + existing.id);
      } catch (e: any) {
        if (!cancelled) {
          setAutoRedirecting(false);
          setIdLocked(false);
          setErr("Could not open existing record: " + (e?.message ?? String(e)));
        }
      }
    })();
    return () => { cancelled = true; };
    // eslint-disable-next-line
  }, [existing]);

  const completed = useMemo(() => {
    let n = 0;
    if (lang) n += 1;
    if (id.trim()) n += 1;
    if (consent) n += 1;
    return n;
  }, [lang, id, consent]);

  const ready = id.trim().length > 0 && consent && !busy;

  async function submit() {
    if (!ready) return;
    setBusy(true);
    setErr(null);
    try {
      let patientId: string;

      if (existing) {
        // Returning patient - reuse the record
        setStatus("Opening existing record...");
        patientId = existing.id;
      } else {
        // New patient
        setStatus("Creating record...");
        const p = await apiPost<{ id: string }>("/api/v1/patients", {
          synthetic_id: id.trim(),
          preferred_language: lang,
        });
        patientId = p.id;
      }

      setStatus("Recording consent...");
      await apiPost("/api/v1/patients/" + patientId + "/consents", {
        purpose: "pre_consultation_intake",
        granted: true,
      });

      setStatus("Opening questionnaire...");
      router.push("/intake/" + patientId);
    } catch (e: any) {
      setErr(e?.message ?? String(e));
      setBusy(false);
      setStatus(null);
    }
  }

  function resetId() {
    setId("");
    setExisting(null);
    setExistingSummary(null);
    setIdLocked(false);
    setConsent(false);
    setTimeout(() => setFocused("id"), 50);
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-slate-50 dark:bg-[#070b18]">
      {/* Auto-redirect overlay */}
      {autoRedirecting && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-md">
          <div className="text-center px-6">
            <div className="relative w-20 h-20 mx-auto">
              <div className="absolute inset-0 rounded-full border-4 border-white/10" />
              <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-emerald-400 animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <svg className="w-8 h-8 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
            </div>
            <div className="mt-6 text-lg font-semibold text-white">Opening your record...</div>
            <div className="mt-2 text-sm text-white/60">Welcome back, {existing?.synthetic_id}</div>
            <div className="mt-1 text-xs text-white/40">Redirecting to your intake questionnaire</div>
          </div>
        </div>
      )}

      <div aria-hidden className="pointer-events-none absolute inset-0">
        <div
          className="absolute inset-x-0 top-0 h-[36rem]"
          style={{
            background:
              "radial-gradient(50% 60% at 20% 0%, rgba(59,130,246,0.18), transparent 60%)," +
              "radial-gradient(40% 60% at 70% 0%, rgba(139,92,246,0.16), transparent 60%)",
          }}
        />
        <div className="absolute -bottom-32 -left-32 w-[28rem] h-[28rem] rounded-full bg-blue-300/30 dark:bg-blue-700/10 blur-3xl" />
        <div className="absolute -bottom-32 -right-32 w-[28rem] h-[28rem] rounded-full bg-indigo-300/30 dark:bg-indigo-700/10 blur-3xl" />
      </div>

      <div className="relative max-w-6xl mx-auto px-6 py-6">
        <nav className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
          <Link href="/" className="hover:text-slate-900 dark:hover:text-white">{t("crumb.home")}</Link>
          <span className="opacity-50">/</span>
          <span className="text-slate-900 dark:text-white font-medium">{t("crumb.intake")}</span>
        </nav>

        <header className={"mt-4 rounded-2xl overflow-hidden relative transition-all duration-700 " + (mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4")}>
          <div className="relative bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 px-6 py-5 md:px-8 md:py-6">
            <div aria-hidden className="absolute -bottom-24 -left-24 w-64 h-64 rounded-full bg-blue-500/10 blur-3xl" />
            <div aria-hidden className="absolute -top-24 -right-24 w-64 h-64 rounded-full bg-purple-500/10 blur-3xl" />

            <div className="relative flex items-center justify-between gap-4 flex-wrap">
              <div className="min-w-0">
                <div className="flex items-center gap-3 flex-wrap">
                  <h1 className="text-xl md:text-2xl font-semibold tracking-tight text-white">{t("page.title")}</h1>
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/10 border border-white/15 text-[10px] font-medium text-emerald-200">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    {t("page.badge")}
                  </span>
                </div>
                <p className="mt-1.5 text-xs text-white/55 max-w-xl leading-relaxed">{t("page.subtitle")}</p>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <div className="hidden sm:block w-32 h-1.5 rounded-full bg-white/10 overflow-hidden">
                  <div className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-blue-400 to-purple-400 transition-all duration-500"
                       style={{ width: (completed / 3) * 100 + "%" }} />
                </div>
                <span className="text-xs font-medium text-white/60 tabular-nums whitespace-nowrap">{completed} / 3</span>
              </div>
            </div>
          </div>
        </header>

        <div className="mt-6 grid lg:grid-cols-3 gap-6">
          <div className={"lg:col-span-2 space-y-5 transition-all duration-700 delay-100 " + (mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4")}>

            <FormCard index="01" title={t("s1.title")} description={t("s1.desc")} done={!!lang} accent="blue">
              <div className="grid grid-cols-2 gap-3">
                <LangTile checked={lang === "en"} onChange={() => { setLang("en"); try { window.localStorage.setItem("mg-intake-lang", "en"); } catch {} }} label="English" native="English" flag="EN" gradient="from-blue-500 to-indigo-500" />
                <LangTile checked={lang === "hi"} onChange={() => { setLang("hi"); try { window.localStorage.setItem("mg-intake-lang", "hi"); } catch {} }} label={t("s1.hi")} native={t("s1.hi")} flag="HI" gradient="from-emerald-500 to-teal-500" />
              </div>
            </FormCard>

            <FormCard index="02" title={t("s2.title")} description={t("s2.desc")} done={id.trim().length > 0 && !looking} accent="indigo">
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-2">{t("s2.label")}</label>
              <div className="relative">
                <div
                  aria-hidden
                  className={"absolute -inset-px rounded-xl transition-opacity duration-300 " + (focused === "id" ? "opacity-100" : "opacity-0")}
                  style={{ background: "linear-gradient(135deg, rgba(59,130,246,0.6), rgba(99,102,241,0.6), rgba(139,92,246,0.6))" }}
                />
                <div className="relative flex items-stretch rounded-xl bg-white dark:bg-slate-900 overflow-hidden">
                  <input
                    value={id}
                    onChange={e => setId(e.target.value)}
                    onFocus={() => setFocused("id")}
                    onBlur={() => setFocused(null)}
                    onKeyDown={e => { if (e.key === "Enter" && ready) submit(); }}
                    placeholder="SYN-042"
                    disabled={idLocked}
                    className="flex-1 bg-transparent px-4 py-3.5 text-sm font-mono text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none disabled:opacity-70"
                  />

                  {/* status indicator */}
                  <div className="pr-2 flex items-center gap-2">
                    {looking && (
                      <span className="flex items-center gap-1.5 text-[10px] font-medium text-slate-500">
                        <span className="w-3 h-3 rounded-full border-2 border-slate-300 border-t-blue-500 animate-spin" />
                        {t("s2.loading")}
                      </span>
                    )}
                    {!looking && id.trim() && !existing && (
                      <span className="flex items-center gap-1 text-[10px] font-medium text-slate-500">
                        <span className="w-4 h-4 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                          <svg className="w-2.5 h-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="12" y1="5" x2="12" y2="19" />
                            <line x1="5" y1="12" x2="19" y2="12" />
                          </svg>
                        </span>
                        {t("s2.new_patient")}
                      </span>
                    )}
                    {!looking && existing && (
                      <span className="flex items-center gap-1 text-[10px] font-medium text-emerald-600 dark:text-emerald-400">
                        <span className="w-4 h-4 rounded-full bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center">
                          <svg className="w-2.5 h-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                        </span>
                        {t("s2.found")}
                      </span>
                    )}
                  </div>

                  {!idLocked && (
                    <button type="button" onClick={() => setId("SYN-" + Math.floor(100 + Math.random() * 900))}
                            className="px-4 text-xs font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors border-l border-slate-100 dark:border-slate-800">
                      {t("s2.generate")}
                    </button>
                  )}
                  {idLocked && (
                    <button type="button" onClick={resetId}
                            className="px-4 text-xs font-medium text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors border-l border-slate-100 dark:border-slate-800">
                      {t("s2.reset_id")}
                    </button>
                  )}
                </div>
              </div>
              <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{t("s2.hint")}</p>

              {/* WELCOME BACK CARD */}
              {existing && (
                <div className="mt-4 rounded-xl border border-emerald-200 dark:border-emerald-900 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/30 p-4 anim-slide-up">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-emerald-500 text-white flex items-center justify-center shrink-0 shadow-md shadow-emerald-500/30">
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs uppercase tracking-widest font-semibold text-emerald-700 dark:text-emerald-300">
                        {t("s2.welcome_back")}
                      </div>
                      <div className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">
                        {existing.synthetic_id}
                      </div>
                      <div className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
                        {t("s2.member_since")}{" "}
                        {new Date(existing.created_at).toLocaleDateString()}
                      </div>

                      {/* Prior records summary */}
                      {existingSummary && (
                        <div className="mt-3 grid grid-cols-3 gap-2">
                          <MiniStat label={t("prev.documents")} value={existingSummary.documents} />
                          <MiniStat label={t("prev.facts")} value={existingSummary.facts} />
                          <MiniStat label={t("prev.events")} value={existingSummary.timeline_events} />
                        </div>
                      )}

                      <Link href={"/clinician/" + existing.id + "/timeline"}
                            className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-emerald-700 dark:text-emerald-300 hover:underline">
                        {t("prev.view_timeline")}
                        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <line x1="5" y1="12" x2="19" y2="12" />
                          <polyline points="12 5 19 12 12 19" />
                        </svg>
                      </Link>
                    </div>
                  </div>
                </div>
              )}
            </FormCard>

            <FormCard index="03" title={t("s3.title")} description={t("s3.desc")} done={consent} accent="emerald">
              <button type="button" onClick={() => setConsent(!consent)}
                      className={"w-full text-left rounded-xl border-2 p-4 transition-all " + (consent ? "border-emerald-400 dark:border-emerald-700 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/30 ring-1 ring-emerald-500/30" : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-slate-700")}>
                <div className="flex items-start gap-3">
                  <span className={"mt-0.5 w-5 h-5 rounded-md border-2 flex items-center justify-center shrink-0 transition-all " + (consent ? "border-emerald-500 bg-emerald-500" : "border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900")}>
                    {consent && (
                      <svg className="w-3 h-3 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    )}
                  </span>
                  <div className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                    <p className="font-medium text-slate-900 dark:text-white">{t("s3.consent_title")}</p>
                    <p className="mt-1.5 text-xs text-slate-600 dark:text-slate-400">{t("s3.consent_body")}</p>
                  </div>
                </div>
              </button>
              <ul className="mt-4 grid sm:grid-cols-2 gap-2.5 text-xs text-slate-600 dark:text-slate-400">
                <Bullet>{t("s3.bullet1")}</Bullet>
                <Bullet>{t("s3.bullet2")}</Bullet>
                <Bullet>{t("s3.bullet3")}</Bullet>
                <Bullet>{t("s3.bullet4")}</Bullet>
              </ul>
            </FormCard>

            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 flex items-center justify-between gap-4 flex-wrap">
              <div className="flex items-center gap-3">
                <div className={"w-9 h-9 rounded-full flex items-center justify-center transition-colors " + (ready ? "bg-emerald-100 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400" : "bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500")}>
                  {ready ? (
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
                  ) : (
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><path d="M12 8v4l3 2" /></svg>
                  )}
                </div>
                <div>
                  <div className="text-sm font-medium text-slate-900 dark:text-white">{ready ? t("submit.ready") : t("submit.not_ready")}</div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">{ready ? t("submit.ready_desc") : t("submit.not_ready_desc")}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Link href="/" className="px-4 py-2.5 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                  {t("submit.cancel")}
                </Link>
                <button onClick={submit} disabled={!ready}
                        className={"px-5 py-2.5 rounded-lg text-sm font-medium transition-all active:scale-[0.98] " + (ready ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/30" : "bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-500 cursor-not-allowed")}>
                  {busy ? status : (existing ? t("submit.continue_existing") : t("submit.continue"))}
                </button>
              </div>
            </div>

            {err && (
              <div className="rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-sm text-red-800 dark:text-red-300">{err}</div>
            )}
          </div>

          <aside className={"space-y-5 transition-all duration-700 delay-200 " + (mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4")}>
            <LivePatientCard id={id} lang={lang} consent={consent} existing={existing} t={t} />

            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
              <div className="px-5 pt-5 pb-3 border-b border-slate-100 dark:border-slate-800">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">{t("next.title")}</h3>
              </div>
              <ol className="px-5 py-4 space-y-4">
                <SideStep n="1" title={t("next.1.title")} body={t("next.1.body")} done={completed === 3} />
                <SideStep n="2" title={t("next.2.title")} body={t("next.2.body")} />
                <SideStep n="3" title={t("next.3.title")} body={t("next.3.body")} />
                <SideStep n="4" title={t("next.4.title")} body={t("next.4.body")} />
              </ol>
            </div>

            <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
              <div className="px-5 pt-5 pb-3 border-b border-slate-100 dark:border-slate-800">
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">{t("priv.title")}</h3>
              </div>
              <ul className="px-5 py-4 space-y-3 text-xs">
                <PrivacyRow label={t("priv.location")}  value={t("priv.location_val")} />
                <PrivacyRow label={t("priv.cloud")}     value={t("priv.cloud_val")} />
                <PrivacyRow label={t("priv.retention")} value={t("priv.retention_val")} />
                <PrivacyRow label={t("priv.regulation")} value={t("priv.regulation_val")} />
                <PrivacyRow label={t("priv.interop")}   value={t("priv.interop_val")} last />
              </ul>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}

function FormCard({ index, title, description, done, accent, children }: {
  index: string; title: string; description: string; done?: boolean;
  accent: "blue" | "indigo" | "emerald"; children: React.ReactNode;
}) {
  const map = {
    blue: "from-blue-500 to-indigo-500",
    indigo: "from-indigo-500 to-purple-500",
    emerald: "from-emerald-500 to-teal-500",
  };
  return (
    <section className="relative rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 md:p-6 overflow-hidden">
      <div aria-hidden className={"absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r " + map[accent] + (done ? " opacity-100" : " opacity-40")} />
      <header className="flex items-start gap-3">
        <div className={"shrink-0 w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-md bg-gradient-to-br " + map[accent]}>
          {done ? (
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
          ) : (
            <span className="text-sm font-bold">{index}</span>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase tracking-widest font-semibold text-slate-400">{index}</span>
            {done && <span className="text-[10px] uppercase tracking-widest font-semibold text-emerald-600 dark:text-emerald-400">- complete</span>}
          </div>
          <h2 className="text-base font-semibold text-slate-900 dark:text-white mt-0.5">{title}</h2>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{description}</p>
        </div>
      </header>
      <div className="mt-5">{children}</div>
    </section>
  );
}

function LangTile({ checked, onChange, label, native, flag, gradient }: {
  checked: boolean; onChange: () => void; label: string; native: string;
  flag: string; gradient: string;
}) {
  return (
    <button type="button" onClick={onChange}
            className={"rounded-xl border-2 p-4 text-left transition-all " + (checked ? "border-blue-500 bg-blue-50/70 dark:bg-blue-950/30 ring-2 ring-blue-500/20 shadow-md" : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300")}>
      <div className="flex items-center justify-between">
        <div className={"w-9 h-9 rounded-lg bg-gradient-to-br " + gradient + " text-white text-xs font-bold flex items-center justify-center"}>
          {flag}
        </div>
        <span className={"w-5 h-5 rounded-full border-2 flex items-center justify-center " + (checked ? "border-blue-600 bg-blue-600" : "border-slate-300")}>
          {checked && <svg className="w-3 h-3 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>}
        </span>
      </div>
      <div className="mt-3">
        <div className="text-sm font-semibold text-slate-900 dark:text-white">{label}</div>
        <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{native}</div>
      </div>
    </button>
  );
}

function Bullet({ children }: { children: React.ReactNode }) {
  return (
    <li className="flex items-start gap-2">
      <svg className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
      <span>{children}</span>
    </li>
  );
}

function MiniStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-white/70 dark:bg-slate-900/50 border border-emerald-200 dark:border-emerald-900 px-3 py-2">
      <div className="text-lg font-bold text-emerald-700 dark:text-emerald-300 tabular-nums">{value}</div>
      <div className="text-[10px] uppercase tracking-wider text-emerald-600 dark:text-emerald-400 mt-0.5">{label}</div>
    </div>
  );
}

function SideStep({ n, title, body, done }: { n: string; title: string; body: string; done?: boolean }) {
  return (
    <li className="flex gap-3">
      <span className={"w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-semibold shrink-0 mt-0.5 " + (done ? "bg-gradient-to-br from-emerald-500 to-teal-500 text-white" : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300")}>
        {done ? (
          <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
        ) : n}
      </span>
      <div>
        <div className="text-xs font-medium text-slate-900 dark:text-white">{title}</div>
        <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">{body}</div>
      </div>
    </li>
  );
}

function PrivacyRow({ label, value, last }: { label: string; value: string; last?: boolean }) {
  return (
    <li className={"flex items-center justify-between gap-3 " + (last ? "" : "pb-3 border-b border-slate-100 dark:border-slate-800")}>
      <span className="text-slate-500 dark:text-slate-400">{label}</span>
      <span className="font-medium text-slate-800 dark:text-slate-200 text-right">{value}</span>
    </li>
  );
}

function LivePatientCard({ id, lang, consent, existing, t }: {
  id: string; lang: Lang; consent: boolean; existing: ExistingPatient | null;
  t: (k: string) => string;
}) {
  const complete = id.trim().length > 0 && consent;
  const returning = !!existing;

  return (
    <div className="relative rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
      <div className={"h-1.5 w-full transition-all duration-500 " + (returning ? "bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-500" : complete ? "bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-500" : "bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400")} />
      <div className="p-5">
        <div className="flex items-center justify-between">
          <h3 className="text-[10px] uppercase tracking-widest font-semibold text-slate-500 dark:text-slate-400">{t("card.title")}</h3>
          {(complete || returning) && (
            <span className="flex items-center gap-1 text-[10px] font-medium text-emerald-700 dark:text-emerald-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              {returning ? "Returning" : t("card.ready")}
            </span>
          )}
        </div>

        <div className="mt-4 flex items-center gap-3">
          <div className={"relative w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold text-white shrink-0 shadow-md " + ((complete || returning) ? "bg-gradient-to-br from-emerald-500 to-teal-600" : "bg-gradient-to-br from-blue-500 to-indigo-600")}>
            {(id.trim() || "SY").slice(-2).toUpperCase()}
            {(complete || returning) && (
              <span className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 border-2 border-white dark:border-slate-900 flex items-center justify-center">
                <svg className="w-2 h-2 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
              </span>
            )}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-wider">{t("card.identifier")}</div>
            <div className={"text-sm font-mono font-medium truncate " + (id.trim() ? "text-slate-900 dark:text-white" : "text-slate-400 dark:text-slate-500 italic")}>
              {id.trim() || t("card.not_provided")}
            </div>
          </div>
        </div>

        <dl className="mt-4 space-y-2.5 text-xs">
          <CardRow label={t("card.language")} value={lang === "en" ? "English" : "\u0939\u093f\u0928\u094d\u0926\u0940"} filled />
          <CardRow label={t("card.consent")} value={consent ? t("card.given") : t("card.not_yet")} good={consent} filled={consent} />
          <CardRow label={t("card.attending")} value={t("card.pending")} muted />
        </dl>

        <div className={"mt-4 pt-3 border-t text-[10px] font-mono uppercase tracking-widest " + ((complete || returning) ? "border-emerald-200 dark:border-emerald-900 text-emerald-700 dark:text-emerald-300" : "border-slate-100 dark:border-slate-800 text-slate-400 dark:text-slate-500")}>
          {returning ? t("card.status_returning") : complete ? t("card.status_ready") : t("card.status_incomplete")}
        </div>
      </div>
    </div>
  );
}

function CardRow({ label, value, filled, good, muted }: {
  label: string; value: string; filled?: boolean; good?: boolean; muted?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-3">
      <dt className="text-slate-500 dark:text-slate-400">{label}</dt>
      <dd className={"flex items-center gap-1.5 font-medium " + (muted ? "text-slate-400 dark:text-slate-500 italic" : good ? "text-emerald-700 dark:text-emerald-300" : filled ? "text-slate-900 dark:text-white" : "text-slate-400 dark:text-slate-500 italic")}>
        {value}
        {good && <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>}
      </dd>
    </div>
  );
}
