"use client";
import Link from "next/link";
import { useEffect, useRef, useState, createContext, useContext } from "react";

export default function Home() {
  return (
    <DarkProvider>
      <AmbientBackground />
      <ScrollProgress />
      <Hero />
      <LiveCounters />
      <TrustTicker />
      <LiveIntakeDemo />
      <DrugResolver />
      <OCRCompare />
      <InteractivePipeline />
      <FhirExplorer />
      <ProblemSection />
      <FeaturesGrid />
      <Personas />
      <FAQ />
      <FinalCTA />
      <Footer />
      <ToastSimulator />
      <Keyframes />
    </DarkProvider>
  );
}

/* ============ Icons (inline SVG, no emojis) ============ */

function IconMic({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" y1="19" x2="12" y2="23" />
    </svg>
  );
}

function IconDoc({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="9" y1="13" x2="15" y2="13" />
      <line x1="9" y1="17" x2="15" y2="17" />
    </svg>
  );
}

function IconSearch({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function IconChart({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="3" y1="20" x2="21" y2="20" />
      <line x1="6" y1="20" x2="6" y2="12" />
      <line x1="12" y1="20" x2="12" y2="6" />
      <line x1="18" y1="20" x2="18" y2="14" />
    </svg>
  );
}

function IconBrain({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.5 2a2.5 2.5 0 0 0-2.5 2.5v0A2.5 2.5 0 0 0 4.5 7v0a2.5 2.5 0 0 0 0 5v0A2.5 2.5 0 0 0 4.5 17v0A2.5 2.5 0 0 0 7 19.5v0A2.5 2.5 0 0 0 9.5 22h0a2.5 2.5 0 0 0 2.5-2.5v-15A2.5 2.5 0 0 0 9.5 2z" />
      <path d="M14.5 2a2.5 2.5 0 0 1 2.5 2.5v0A2.5 2.5 0 0 1 19.5 7v0a2.5 2.5 0 0 1 0 5v0a2.5 2.5 0 0 1 0 5v0A2.5 2.5 0 0 1 17 19.5v0a2.5 2.5 0 0 1-2.5 2.5h0a2.5 2.5 0 0 1-2.5-2.5v-15A2.5 2.5 0 0 1 14.5 2z" />
    </svg>
  );
}

function IconLink({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
      <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
    </svg>
  );
}

function IconShield({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <polyline points="9 12 11 14 15 10" />
    </svg>
  );
}

function IconNote({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16v12l-4 4H4z" />
      <line x1="8" y1="9" x2="16" y2="9" />
      <line x1="8" y1="13" x2="14" y2="13" />
    </svg>
  );
}

function IconCheck({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function IconArrow({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  );
}

function IconDiamond({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2l10 10-10 10L2 12z" />
    </svg>
  );
}

function IconSlider({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="8 7 3 12 8 17" />
      <polyline points="16 7 21 12 16 17" />
    </svg>
  );
}

function IconChevron({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

/* ============ Dark mode ============ */

const ThemeContext = createContext({ dark: false, toggle: () => {} });

function DarkProvider({ children }: { children: React.ReactNode }) {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    const saved = typeof window !== "undefined" ? localStorage.getItem("mg-dark") : null;
    if (saved === "1") setDark(true);
  }, []);
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.classList.toggle("dark", dark);
      localStorage.setItem("mg-dark", dark ? "1" : "0");
    }
  }, [dark]);
  return (
    <ThemeContext.Provider value={{ dark, toggle: () => setDark(d => !d) }}>
      <div className={dark ? "dark" : ""}>{children}</div>
    </ThemeContext.Provider>
  );
}

/* ============ Ambient background ============ */

function AmbientBackground() {
  const [t, setT] = useState(0);
  useEffect(() => {
    const i = setInterval(() => setT(x => x + 1), 60);
    return () => clearInterval(i);
  }, []);
  const particles = Array.from({ length: 14 }, (_, i) => {
    const seed = i * 137;
    const x = ((seed + t / 2) % 100);
    const y = ((seed * 3 + t) % 100);
    const hue = 200 + ((i * 23) % 120);
    return { x, y, hue, size: 2 + (i % 3) };
  });
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {particles.map((p, i) => (
        <span key={i} className="absolute rounded-full opacity-[0.07] dark:opacity-[0.12]"
              style={{
                left: p.x + "%", top: p.y + "%",
                width: p.size * 4, height: p.size * 4,
                background: "hsl(" + p.hue + ", 80%, 60%)",
                filter: "blur(1px)",
                transition: "all 0.4s linear",
              }} />
      ))}
    </div>
  );
}

/* ============ Reveal wrapper ============ */

function Reveal({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const [seen, setSeen] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      entries => entries.forEach(e => {
        if (e.isIntersecting) { setTimeout(() => setSeen(true), delay); io.disconnect(); }
      }),
      { threshold: 0.12 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [delay]);
  return (
    <div ref={ref} className="relative z-10 transition-all duration-700 ease-out"
         style={{ opacity: seen ? 1 : 0, transform: seen ? "translateY(0)" : "translateY(24px)" }}>
      {children}
    </div>
  );
}

/* ============ 3D tilt ============ */

function Tilt({ children, max = 6 }: { children: React.ReactNode; max?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const [t, setT] = useState({ rx: 0, ry: 0 });
  function onMove(e: React.MouseEvent<HTMLDivElement>) {
    const el = ref.current; if (!el) return;
    const r = el.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width;
    const y = (e.clientY - r.top) / r.height;
    setT({ rx: (0.5 - y) * max * 2, ry: (x - 0.5) * max * 2 });
  }
  return (
    <div ref={ref} onMouseMove={onMove} onMouseLeave={() => setT({ rx: 0, ry: 0 })} style={{ perspective: "1000px" }}>
      <div style={{ transform: "rotateX(" + t.rx + "deg) rotateY(" + t.ry + "deg)", transition: "transform 150ms ease-out", transformStyle: "preserve-3d" }}>
        {children}
      </div>
    </div>
  );
}

/* ============ Scroll progress ============ */

function ScrollProgress() {
  const [pct, setPct] = useState(0);
  useEffect(() => {
    const onScroll = () => {
      const h = document.documentElement;
      const max = h.scrollHeight - h.clientHeight;
      setPct(max > 0 ? (h.scrollTop / max) * 100 : 0);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return (
    <div className="fixed top-0 left-0 right-0 h-0.5 z-50">
      <div className="h-full bg-gradient-to-r from-blue-500 via-emerald-500 to-indigo-500" style={{ width: pct + "%" }} />
    </div>
  );
}

/* ============ Hero ============ */

function Hero() {
  const ref = useRef<HTMLDivElement>(null);
  const [mouse, setMouse] = useState({ x: 0.5, y: 0.5 });
  const [particles, setParticles] = useState<{ id: number; x: number; y: number; hue: number }[]>([]);
  const nextId = useRef(0);

  function onMove(e: React.MouseEvent<HTMLDivElement>) {
    const r = ref.current?.getBoundingClientRect();
    if (!r) return;
    setMouse({ x: (e.clientX - r.left) / r.width, y: (e.clientY - r.top) / r.height });
    const id = nextId.current++;
    const p = { id, x: e.clientX - r.left, y: e.clientY - r.top, hue: 200 + Math.random() * 120 };
    setParticles(prev => [...prev.slice(-20), p]);
    setTimeout(() => setParticles(prev => prev.filter(x => x.id !== id)), 1200);
  }

  return (
    <section ref={ref} onMouseMove={onMove}
             className="relative overflow-hidden bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 text-white">
      <div className="absolute -top-32 -left-32 w-[32rem] h-[32rem] rounded-full bg-blue-500/25 blur-3xl anim-pulse-glow" />
      <div className="absolute top-40 -right-40 w-[36rem] h-[36rem] rounded-full bg-indigo-500/25 blur-3xl anim-pulse-glow" style={{ animationDelay: "1s" }} />
      <div className="absolute -bottom-40 left-1/3 w-[28rem] h-[28rem] rounded-full bg-emerald-500/15 blur-3xl anim-pulse-glow" style={{ animationDelay: "2s" }} />

      <div className="pointer-events-none absolute inset-0 opacity-60"
           style={{ background: "radial-gradient(700px circle at " + (mouse.x * 100) + "% " + (mouse.y * 100) + "%, rgba(96,165,250,0.22), transparent 40%)" }} />

      {particles.map(p => (
        <span key={p.id} className="pointer-events-none absolute w-2 h-2 rounded-full"
              style={{
                left: p.x, top: p.y,
                background: "hsl(" + p.hue + ", 90%, 60%)",
                boxShadow: "0 0 14px hsl(" + p.hue + ", 90%, 60%)",
                animation: "fade-particle 1.2s ease-out forwards",
                transform: "translate(-50%, -50%)",
              }} />
      ))}

      <div className="absolute inset-0 opacity-[0.06]"
           style={{ backgroundImage: "linear-gradient(to right, #ffffff 1px, transparent 1px), linear-gradient(to bottom, #ffffff 1px, transparent 1px)", backgroundSize: "48px 48px" }} />

      <div className="relative max-w-6xl mx-auto px-8 pt-40 pb-28 grid lg:grid-cols-2 gap-12 items-center">
        <div className="anim-slide-up">
          <div className="flex flex-wrap items-center gap-3 mb-6">
            <span className="px-3 py-1 rounded-full bg-white/10 border border-white/20 text-xs font-medium tracking-wide">
              HealthTech / Clinical Informatics
            </span>
            <span className="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-xs font-medium text-emerald-100 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Runs entirely on-premises
            </span>
          </div>

          <h1 className="text-5xl md:text-6xl font-bold leading-[1.05] tracking-tight">
            The two minutes before a consultation, reimagined.
          </h1>
          <p className="mt-6 text-lg text-blue-100/90 leading-relaxed max-w-xl">
            MediGraph captures multilingual history, digitizes prior prescriptions, and hands a clean
            evidence-linked summary to the clinician - without sending a single byte to the cloud.
          </p>

          <div className="mt-10 flex flex-wrap gap-3">
            <Link href="/intake" className="group px-6 py-3 rounded-lg bg-white text-slate-900 font-medium hover:bg-blue-50 transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 hover:-translate-y-0.5 inline-flex items-center gap-2">
              Start patient intake
              <span className="group-hover:translate-x-0.5 transition-transform"><IconArrow /></span>
            </Link>
            <a href="#demo" className="px-6 py-3 rounded-lg bg-white/10 border border-white/20 text-white font-medium hover:bg-white/20 transition-all hover:-translate-y-0.5">
              See it work
            </a>
          </div>

          <div className="mt-14 grid grid-cols-2 sm:grid-cols-4 gap-6 max-w-2xl">
            <Stat target={1}  format="decimal2" label="F1 score" />
            <Stat target={41} format="int"      label="Endpoints" />
            <Stat target={8}  format="int"      label="Modules" />
            <Stat target={0}  format="int"      label="Cloud calls" />
          </div>
        </div>

        <div className="relative anim-float-slow"><UIMockup /></div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-white dark:from-slate-900 to-transparent" />
    </section>
  );
}

function Stat({ target, format, label }: { target: number; format: "int" | "decimal2"; label: string }) {
  const [v, setV] = useState(0);
  useEffect(() => {
    let raf = 0;
    const start = performance.now();
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / 1400);
      const eased = 1 - Math.pow(1 - p, 3);
      setV(target * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target]);
  const display = format === "decimal2" ? v.toFixed(2) : Math.round(v).toString();
  return (
    <div>
      <div className="text-3xl font-bold text-white tabular-nums">{display}</div>
      <div className="text-xs uppercase tracking-wide text-blue-200 mt-1">{label}</div>
    </div>
  );
}

/* ============ Waveform ============ */

function Waveform({ count = 24, color = "#10b981" }: { count?: number; color?: string }) {
  const [phase, setPhase] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setPhase(p => (p + 1) % 1000), 90);
    return () => clearInterval(t);
  }, []);
  const bars = Array.from({ length: count }, (_, i) => {
    const base = Math.sin((phase + i * 13) / 6) * 0.5 + 0.5;
    const noise = Math.sin((phase + i * 37) / 3) * 0.15;
    return Math.max(0.15, Math.min(1, base + noise));
  });
  return (
    <div className="flex items-end gap-[3px] h-12">
      {bars.map((h, i) => (
        <span key={i} className="w-1 rounded-full" style={{ height: h * 100 + "%", background: "linear-gradient(to top, " + color + ", " + color + "88)" }} />
      ))}
    </div>
  );
}

/* ============ UI mockup ============ */

function UIMockup() {
  const lines = [
    "Patient Summary",
    "34-year-old male, recorded 2012-11-09.",
    "",
    "Presenting Complaints",
    "Reduced sleep, anxiety, increased irritability.",
    "",
    "Medication Profile",
    "- Metoprolol 100mg BD - for blood pressure",
    "- Dorzolamide 10mg BD - for glaucoma",
    "- Cimetidine 50mg TDS - for acid reflux",
  ];
  const full = lines.join("\n");
  const [n, setN] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setN(prev => (prev >= full.length ? 0 : prev + 1)), 32);
    return () => clearInterval(t);
  }, [full]);

  const activity = ["Uploaded prescription.png", "OCR: 31 regions", "AI corrected 3 names", "Timeline: 8 events", "AI note drafted"];
  const [feedIdx, setFeedIdx] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setFeedIdx(i => (i + 1) % activity.length), 1600);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="relative">
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-400/30 to-indigo-500/30 blur-2xl" />
      <div className="relative rounded-2xl bg-white shadow-2xl shadow-blue-900/40 border border-white/40 overflow-hidden">
        <div className="flex items-center gap-1.5 px-4 py-3 border-b border-slate-100 bg-slate-50">
          <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
          <span className="ml-3 text-xs text-slate-400 font-mono truncate">localhost:3000/clinician/.../summary</span>
        </div>
        <div className="p-5 grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-800">AI Clinical Note</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">GENERATING</span>
            </div>
            <div className="mt-3"><Waveform /></div>
            <pre className="mt-3 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-[11px] leading-5 text-slate-800 whitespace-pre-wrap min-h-[200px] max-h-[200px] overflow-hidden font-mono">
              {full.slice(0, n)}
              <span className="inline-block w-1.5 h-3 bg-emerald-500 animate-pulse align-middle ml-0.5" />
            </pre>
          </div>
          <div className="col-span-1">
            <div className="text-[10px] uppercase tracking-widest text-slate-400 font-semibold mb-2">Activity</div>
            <ul className="space-y-2">
              {activity.map((a, i) => {
                const active = i === feedIdx;
                return (
                  <li key={a} className={"text-[10px] leading-4 px-2 py-1 rounded transition-colors " + (active ? "bg-blue-50 text-blue-800" : "text-slate-500")}>
                    <span className={"inline-block w-1 h-1 rounded-full mr-1.5 " + (active ? "bg-blue-500 animate-pulse" : "bg-slate-300")} />
                    {a}
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </div>

      <div className="absolute -top-4 -left-4 rounded-xl bg-white shadow-xl border border-slate-100 px-3 py-2 anim-float-slower">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center">
            <IconMic className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[10px] text-slate-500">Voice input</div>
            <div className="text-xs font-medium">Hindi recognised</div>
          </div>
        </div>
      </div>
      <div className="absolute -bottom-4 -right-4 rounded-xl bg-white shadow-xl border border-slate-100 px-3 py-2 anim-float-slower" style={{ animationDelay: "1.5s" }}>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center">
            <IconCheck className="w-3 h-3" />
          </div>
          <div>
            <div className="text-[10px] text-slate-500">FHIR R4</div>
            <div className="text-xs font-medium">HAPI validated</div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============ Live counters ============ */

function LiveCounters() {
  const [t, setT] = useState(0);
  useEffect(() => {
    const i = setInterval(() => setT(x => x + 1), 1000);
    return () => clearInterval(i);
  }, []);
  const metrics = [
    { label: "Prescriptions processed today", value: 127 + (t % 6), color: "text-blue-600 dark:text-blue-400" },
    { label: "OCR regions extracted",          value: 3937 + (t % 12) * 3, color: "text-purple-600 dark:text-purple-400" },
    { label: "Drugs mapped to generics",       value: 508 + (t % 9), color: "text-emerald-600 dark:text-emerald-400" },
    { label: "FHIR bundles validated",         value: 84 + (t % 4), color: "text-indigo-600 dark:text-indigo-400" },
  ];
  return (
    <section className="border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
      <div className="max-w-6xl mx-auto px-8 py-8 grid grid-cols-2 md:grid-cols-4 gap-6">
        {metrics.map(m => (
          <div key={m.label} className="flex items-center gap-3">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 animate-ping" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <div>
              <div className={"text-2xl font-bold tabular-nums " + m.color}>{m.value}</div>
              <div className="text-[10px] uppercase tracking-widest text-slate-500 dark:text-slate-400 mt-0.5">{m.label}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ============ Trust ticker ============ */

function TrustTicker() {
  const items = ["DPDP Act 2023 compliant", "ABDM FHIR R4 aligned", "HL7 HAPI validated", "Human in the loop", "English and Hindi", "Zero outbound calls", "PaddleOCR", "MedGemma via Ollama", "faster-whisper", "SQLite or Postgres"];
  return (
    <section className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 overflow-hidden py-4">
      <div className="flex anim-marquee whitespace-nowrap">
        {[0, 1].map(k => (
          <div key={k} className="flex shrink-0">
            {items.map(it => (
              <span key={it + k} className="mx-6 flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-widest">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                {it}
              </span>
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}

/* ============ Live intake demo ============ */

function LiveIntakeDemo() {
  const [text, setText] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [facts, setFacts] = useState<{ label: string; value: string; kind: string; confidence: number; flag?: boolean }[]>([]);

  const examples = ["I have had a headache for two days", "fever and cough since yesterday", "chest pain when I climb stairs"];

  function analyze() {
    if (!text.trim()) return;
    setAnalyzing(true);
    setFacts([]);
    const patterns: { re: RegExp; build: () => typeof facts }[] = [
      { re: /headache/i, build: () => [
        { kind: "symptom", label: "Chief complaint", value: "Headache", confidence: 0.92 },
        { kind: "duration", label: "Duration", value: "2 days", confidence: 0.88 },
      ]},
      { re: /chest\s*pain/i, build: () => [
        { kind: "symptom", label: "Chief complaint", value: "Chest pain", confidence: 0.90 },
        { kind: "trigger", label: "Trigger", value: "Exertion (climbing stairs)", confidence: 0.85 },
        { kind: "flag",   label: "Red flag",  value: "Cardiac review suggested", confidence: 0.95, flag: true },
      ]},
      { re: /fever/i, build: () => [{ kind: "symptom", label: "Chief complaint", value: "Fever", confidence: 0.93 }] },
      { re: /cough/i, build: () => [{ kind: "symptom", label: "Cough", value: "Present", confidence: 0.88 }] },
    ];
    const collected: typeof facts = [];
    for (const p of patterns) if (p.re.test(text)) collected.push(...p.build());
    if (collected.length === 0) collected.push({ kind: "symptom", label: "Chief complaint", value: text.slice(0, 60), confidence: 0.82 });
    setTimeout(() => { setFacts(collected); setAnalyzing(false); }, 900);
  }

  return (
    <section id="demo" className="relative max-w-6xl mx-auto px-8 py-24 z-10">
      <Reveal>
        <div className="text-center max-w-2xl mx-auto">
          <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-widest">Live demo</p>
          <h2 className="mt-3 text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">
            Type a patient complaint. See it become structured data.
          </h2>
          <p className="mt-4 text-slate-600 dark:text-slate-400">A simplified in-browser demo. The real system runs the same logic on speech or touch.</p>
        </div>
      </Reveal>

      <Reveal delay={150}>
        <div className="mt-12 max-w-2xl mx-auto rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-xl p-6">
          <label className="text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400 font-semibold">Patient says:</label>
          <textarea value={text} onChange={e => setText(e.target.value)} placeholder="e.g. I have had a headache for two days" rows={3}
                    className="mt-2 w-full border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          <div className="mt-3 flex flex-wrap gap-2">
            {examples.map(ex => (
              <button key={ex} onClick={() => setText(ex)} className="text-xs px-3 py-1 rounded-full border border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800">{ex}</button>
            ))}
          </div>
          <button onClick={analyze} disabled={analyzing || !text.trim()}
                  className="mt-4 w-full px-4 py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50">
            {analyzing ? "Analysing..." : "Analyse"}
          </button>

          {facts.length > 0 && (
            <div className="mt-5 border-t border-slate-100 dark:border-slate-800 pt-5 anim-slide-up">
              <div className="text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400 font-semibold mb-3">Extracted facts</div>
              <ul className="space-y-2">
                {facts.map((f, i) => (
                  <li key={i} className={"flex items-center gap-3 text-sm px-2 py-1 rounded " + (f.flag ? "bg-red-50 dark:bg-red-950/30" : "")}>
                    <span className={"text-[10px] px-2 py-0.5 rounded uppercase tracking-wide " + (f.flag ? "bg-red-100 text-red-700" : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300")}>{f.kind}</span>
                    <span className="font-medium text-slate-800 dark:text-slate-100">{f.label}:</span>
                    <span className="text-slate-700 dark:text-slate-300 flex-1">{f.value}</span>
                    <span className="w-16 h-1 bg-slate-100 dark:bg-slate-800 rounded overflow-hidden">
                      <span className={"block h-1 " + (f.flag ? "bg-red-500" : "bg-emerald-500")} style={{ width: f.confidence * 100 + "%" }} />
                    </span>
                    <span className="text-[10px] font-mono text-slate-500 w-8 text-right">{f.confidence.toFixed(2)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </Reveal>
    </section>
  );
}

/* ============ Drug resolver ============ */

function DrugResolver() {
  const dict: Record<string, { generic: string; cls: string; purpose: string }> = {
    betaloc:   { generic: "Metoprolol",      cls: "beta_blocker",   purpose: "blood pressure / heart rate" },
    metolar:   { generic: "Metoprolol",      cls: "beta_blocker",   purpose: "blood pressure / heart rate" },
    oxprelol:  { generic: "Oxprenolol",      cls: "beta_blocker",   purpose: "blood pressure / heart rate" },
    clonelst:  { generic: "Clonazepam",      cls: "benzodiazepine", purpose: "anxiety / seizures" },
    rivotril:  { generic: "Clonazepam",      cls: "benzodiazepine", purpose: "anxiety / seizures" },
    "201calm": { generic: "Etizolam",        cls: "anxiolytic",     purpose: "anxiety / short-term insomnia" },
    vexidsp:   { generic: "Dexmedetomidine", cls: "sedative",       purpose: "procedural or ICU sedation" },
    crocin:    { generic: "Paracetamol",     cls: "analgesic",      purpose: "pain and fever" },
    dolo:      { generic: "Paracetamol",     cls: "analgesic",      purpose: "pain and fever" },
    glycomet:  { generic: "Metformin",       cls: "biguanide",      purpose: "type 2 diabetes" },
    pan:       { generic: "Pantoprazole",    cls: "ppi",            purpose: "acid reflux" },
    telma:     { generic: "Telmisartan",     cls: "arb",            purpose: "blood pressure" },
    amlokind:  { generic: "Amlodipine",      cls: "ccb",            purpose: "blood pressure / angina" },
    atorva:    { generic: "Atorvastatin",    cls: "statin",         purpose: "high cholesterol" },
  };
  const [input, setInput] = useState("");
  const [result, setResult] = useState<typeof dict[string] | null>(null);
  const [unknown, setUnknown] = useState(false);
  function resolve() {
    const key = input.trim().toLowerCase();
    if (!key) return;
    const hit = dict[key];
    if (hit) { setResult(hit); setUnknown(false); } else { setResult(null); setUnknown(true); }
  }
  const suggestions = ["Betaloc", "201calm", "Clonelst", "Crocin", "Glycomet"];

  return (
    <section id="resolver" className="relative bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900 py-24 z-10">
      <div className="max-w-4xl mx-auto px-8">
        <Reveal>
          <div className="text-center max-w-2xl mx-auto">
            <p className="text-sm font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-widest">Live drug resolver</p>
            <h2 className="mt-3 text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">Type any Indian brand name.</h2>
            <p className="mt-4 text-slate-600 dark:text-slate-400">The same dictionary + LLM resolution that runs on every prescription.</p>
          </div>
        </Reveal>
        <Reveal delay={150}>
          <div className="mt-12 rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-xl p-6">
            <div className="flex gap-2">
              <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && resolve()}
                     placeholder="e.g. Betaloc, 201calm, Glycomet"
                     className="flex-1 border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500" />
              <button onClick={resolve} className="px-5 py-2.5 rounded-lg bg-emerald-600 text-white font-medium hover:bg-emerald-700">Resolve</button>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {suggestions.map(s => (
                <button key={s} onClick={() => { setInput(s); setTimeout(resolve, 50); }}
                        className="text-xs px-3 py-1 rounded-full border border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800">{s}</button>
              ))}
            </div>
            {result && (
              <div className="mt-6 rounded-xl border border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950/40 p-4 anim-slide-up">
                <div className="flex items-center justify-between">
                  <span className="text-xs uppercase tracking-widest text-emerald-700 dark:text-emerald-300">Resolved</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-white dark:bg-slate-800 text-emerald-700 dark:text-emerald-300 font-mono">conf 0.95</span>
                </div>
                <div className="mt-3 grid grid-cols-3 gap-4">
                  <Field label="Brand" value={input} />
                  <Field label="Generic" value={result.generic} highlight />
                  <Field label="Class" value={result.cls} mono />
                </div>
                <div className="mt-4 text-sm text-slate-700 dark:text-slate-200">
                  <span className="text-slate-500 dark:text-slate-400">Common purpose: </span>{result.purpose}
                </div>
              </div>
            )}
            {unknown && (
              <div className="mt-6 rounded-xl border border-amber-300 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/40 p-4 anim-slide-up">
                <div className="text-xs uppercase tracking-widest text-amber-700 dark:text-amber-300 font-semibold">Unknown brand</div>
                <p className="mt-2 text-sm text-slate-700 dark:text-slate-200">
                  <strong>{input}</strong> is not in the local dictionary. The full system would query the LLM and cache the result.
                </p>
              </div>
            )}
          </div>
        </Reveal>
      </div>
    </section>
  );
}

function Field({ label, value, highlight, mono }: { label: string; value: string; highlight?: boolean; mono?: boolean }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-widest text-slate-500 dark:text-slate-400">{label}</div>
      <div className={"mt-1 " + (highlight ? "text-lg font-bold text-emerald-700 dark:text-emerald-300" : "text-sm text-slate-800 dark:text-slate-100") + (mono ? " font-mono" : "")}>{value}</div>
    </div>
  );
}

/* ============ OCR compare ============ */

function OCRCompare() {
  const [pct, setPct] = useState(50);
  const raw = ["PRESCRIPTION NAME: AGE/GENDER: 29 years/male", "ISSUE DATE: 08112023", "-T 201calm 10mg 00", "-T Clonelst 0.5mg 00n", "-T Vexidsp 25mg 80 x 10 days", "compiomd Decreased sleeb, anxisty"];
  const corrected = ["PRESCRIPTION", "AGE/GENDER: 29 years / male", "ISSUE DATE: 2023-11-08", "- T. Etizolam 10mg OD", "- T. Clonazepam 0.5mg OD", "- T. Dexmedetomidine 25mg BD x 10 days", "Complaint: Decreased sleep, anxiety"];
  return (
    <section className="relative max-w-6xl mx-auto px-8 py-24 z-10">
      <Reveal>
        <div className="text-center max-w-2xl mx-auto">
          <p className="text-sm font-semibold text-purple-600 dark:text-purple-400 uppercase tracking-widest">Document intelligence</p>
          <h2 className="mt-3 text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">From noisy scan to clean clinical text.</h2>
          <p className="mt-4 text-slate-600 dark:text-slate-400">Drag the slider. PaddleOCR extracts text; MedGemma corrects and maps brands.</p>
        </div>
      </Reveal>
      <Reveal delay={150}>
        <div className="mt-14 max-w-3xl mx-auto">
          <div className="relative rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-lg overflow-hidden">
            <div className="grid grid-cols-2 divide-x divide-slate-100 dark:divide-slate-800">
              <div className="p-6">
                <div className="text-[10px] uppercase tracking-widest text-red-600 dark:text-red-400 font-semibold mb-3">Raw OCR</div>
                <pre className="text-[11px] leading-6 text-slate-700 dark:text-slate-300 font-mono whitespace-pre-wrap">{raw.join("\n")}</pre>
              </div>
              <div className="p-6 bg-emerald-50/50 dark:bg-emerald-950/30">
                <div className="text-[10px] uppercase tracking-widest text-emerald-700 dark:text-emerald-300 font-semibold mb-3">AI-corrected</div>
                <pre className="text-[11px] leading-6 text-slate-800 dark:text-slate-100 font-mono whitespace-pre-wrap">{corrected.join("\n")}</pre>
              </div>
            </div>
            <div className="pointer-events-none absolute inset-y-0 w-0.5 bg-gradient-to-b from-blue-500 to-indigo-500" style={{ left: pct + "%" }}>
              <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-white shadow-lg border-2 border-blue-500 flex items-center justify-center text-blue-600">
                <IconSlider />
              </div>
            </div>
          </div>
          <input type="range" min={10} max={90} value={pct} onChange={e => setPct(Number(e.target.value))} className="w-full mt-4 accent-blue-600" />
          <div className="mt-3 grid grid-cols-3 gap-3 text-xs">
            <Pill label="31 regions" value="extracted" color="blue" />
            <Pill label="0.82" value="mean confidence" color="purple" />
            <Pill label="6 facts" value="normalized" color="emerald" />
          </div>
        </div>
      </Reveal>
    </section>
  );
}

function Pill({ label, value, color }: { label: string; value: string; color: "blue" | "purple" | "emerald" }) {
  const map = {
    blue: "bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border-blue-100 dark:border-blue-900",
    purple: "bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 border-purple-100 dark:border-purple-900",
    emerald: "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-100 dark:border-emerald-900",
  };
  return (
    <div className={"rounded-xl border px-4 py-3 " + map[color]}>
      <div className="text-base font-bold">{label}</div>
      <div className="text-[10px] uppercase tracking-wide mt-0.5 opacity-80">{value}</div>
    </div>
  );
}

/* ============ Interactive pipeline ============ */

function InteractivePipeline() {
  const [active, setActive] = useState(0);
  const [traveling, setTraveling] = useState(false);
  const [elapsed, setElapsed] = useState(0);

  const stages = [
    { label: "Intake",   accent: "#3b82f6", Icon: IconMic,    body: "Voice or touch in English or Hindi.", latency: 800 },
    { label: "OCR",      accent: "#a855f7", Icon: IconDoc,    body: "PaddleOCR extracts text with bounding boxes preserved.", latency: 1500 },
    { label: "Extract",  accent: "#ec4899", Icon: IconSearch, body: "Drugs, dosages, dates, and lab values become typed facts.", latency: 600 },
    { label: "Timeline", accent: "#f59e0b", Icon: IconChart,  body: "Facts ordered chronologically. Conflicts stay visible.", latency: 300 },
    { label: "AI note",  accent: "#10b981", Icon: IconBrain,  body: "MedGemma drafts a hedged clinical narrative. Zero diagnoses.", latency: 24000 },
    { label: "FHIR",     accent: "#6366f1", Icon: IconLink,   body: "Bundle validated against HL7 HAPI with zero errors.", latency: 400 },
  ];

  useEffect(() => {
    const t = setInterval(() => {
      setTraveling(true);
      setTimeout(() => { setActive(a => (a + 1) % stages.length); setTraveling(false); }, 800);
    }, 2600);
    return () => clearInterval(t);
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    const total = stages.slice(0, active + 1).reduce((s, x) => s + x.latency, 0);
    let raf = 0;
    const start = performance.now();
    const from = elapsed;
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / 700);
      const eased = 1 - Math.pow(1 - p, 3);
      setElapsed(from + (total - from) * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line
  }, [active]);

  const current = stages[active];
  const nextIdx = (active + 1) % stages.length;
  const CurrentIcon = current.Icon;

  return (
    <section id="pipeline" className="relative bg-gradient-to-b from-white to-slate-50 dark:from-slate-900 dark:to-slate-950 py-24 overflow-hidden z-10">
      <div className="absolute inset-0 opacity-[0.05] dark:opacity-[0.1] pointer-events-none"
           style={{ backgroundImage: "radial-gradient(circle, currentColor 1px, transparent 1px)", backgroundSize: "24px 24px", color: "#0f172a" }} />

      <div className="relative max-w-6xl mx-auto px-8">
        <Reveal>
          <div className="text-center max-w-2xl mx-auto">
            <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-widest">The pipeline</p>
            <h2 className="mt-3 text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">One upload. Six intelligent steps.</h2>
            <p className="mt-4 text-slate-600 dark:text-slate-400">Watch the payload travel. Every stage hands a richer artifact to the next.</p>
          </div>
        </Reveal>

        <Reveal delay={150}>
          <div className="mt-16 relative">
            <div className="hidden md:block relative">
              <div className="absolute top-8 left-0 right-0 h-1 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-blue-500 via-pink-500 to-indigo-500 transition-all duration-500" style={{ width: ((active + 1) / 6) * 100 + "%" }} />
              </div>
              <div className="absolute top-5 -translate-x-1/2 transition-all duration-700 ease-out z-10"
                   style={{ left: traveling ? ((nextIdx + 0.5) / 6) * 100 + "%" : ((active + 0.5) / 6) * 100 + "%" }}>
                <div className="w-8 h-8 rounded-lg shadow-xl flex items-center justify-center text-white transition-all"
                     style={{
                       background: "linear-gradient(135deg, " + current.accent + ", " + stages[nextIdx].accent + ")",
                       boxShadow: "0 8px 24px " + current.accent + "66",
                       transform: traveling ? "scale(1.2) rotate(8deg)" : "scale(1) rotate(0deg)",
                     }}>
                  <IconDiamond className="w-4 h-4" />
                </div>
                {traveling && <span className="absolute inset-0 rounded-lg animate-ping" style={{ background: current.accent, opacity: 0.35 }} />}
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-6 gap-4 md:gap-2">
              {stages.map((s, i) => {
                const isActive = i === active;
                const isPast = i < active;
                const isNext = i === nextIdx && traveling;
                const Icon = s.Icon;
                return (
                  <button key={s.label} onClick={() => setActive(i)} className="text-left group relative flex flex-col items-center md:items-start">
                    <div className="relative">
                      <div className={"w-16 h-16 rounded-full flex items-center justify-center transition-all duration-500 text-white " + (isActive ? "scale-125" : isNext ? "scale-110" : isPast ? "scale-100 opacity-90" : "scale-90 opacity-50")}
                           style={{
                             background: isActive || isPast || isNext ? "linear-gradient(135deg, " + s.accent + ", " + s.accent + "dd)" : "#e2e8f0",
                             boxShadow: isActive ? "0 20px 40px " + s.accent + "55, 0 0 0 4px " + s.accent + "33" : isNext ? "0 10px 30px " + s.accent + "44" : undefined,
                             color: isActive || isPast || isNext ? "white" : "#94a3b8",
                           }}>
                        <Icon className="w-6 h-6" />
                      </div>
                      {isActive && <span className="absolute inset-0 rounded-full animate-ping" style={{ background: s.accent, opacity: 0.15 }} />}
                      {isNext && <span className="absolute -inset-1 rounded-full border-2 border-dashed animate-spin" style={{ borderColor: s.accent, animationDuration: "3s" }} />}
                      <span className={"absolute -top-1 -right-1 w-6 h-6 rounded-full text-[10px] font-bold flex items-center justify-center border-2 border-white dark:border-slate-900 transition-colors " + (isActive || isPast ? "text-white" : "text-slate-500")}
                            style={{ background: isActive || isPast || isNext ? s.accent : "#cbd5e1" }}>{i + 1}</span>
                    </div>
                    <div className="mt-3 text-center md:text-left">
                      <div className={"font-semibold text-sm transition-colors " + (isActive ? "text-slate-900 dark:text-white" : "text-slate-500 dark:text-slate-400")}>{s.label}</div>
                      <div className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">{(s.latency / 1000).toFixed(s.latency >= 1000 ? 0 : 1)}s</div>
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="mt-16 grid md:grid-cols-5 gap-4 items-start">
              <div className="md:col-span-2">
                <div key={active} className="anim-slide-up rounded-2xl border bg-white dark:bg-slate-900 p-6"
                     style={{ borderColor: current.accent + "66", boxShadow: "0 12px 40px " + current.accent + "22" }}>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-md shrink-0"
                         style={{ background: "linear-gradient(135deg, " + current.accent + ", " + current.accent + "dd)" }}>
                      <CurrentIcon className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-[10px] uppercase tracking-widest font-semibold" style={{ color: current.accent }}>Stage {active + 1} of 6</div>
                      <div className="text-base font-semibold text-slate-900 dark:text-white">{current.label}</div>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{current.body}</p>
                  <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                    <span className="text-slate-500 dark:text-slate-400">Stage latency</span>
                    <span className="font-mono font-semibold" style={{ color: current.accent }}>{(current.latency / 1000).toFixed(current.latency >= 1000 ? 0 : 1)}s</span>
                  </div>
                  <div className="mt-2 flex items-center justify-between text-xs">
                    <span className="text-slate-500 dark:text-slate-400">Cumulative</span>
                    <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">{(elapsed / 1000).toFixed(1)}s</span>
                  </div>
                  <div className="mt-5 flex items-center gap-1.5">
                    {stages.map((s, i) => (
                      <button key={s.label} onClick={() => setActive(i)} className="h-1.5 rounded-full transition-all duration-300"
                              style={{ width: i === active ? "32px" : "12px", background: i === active ? current.accent : "#cbd5e1" }}
                              aria-label={"Go to " + s.label} />
                    ))}
                    <span className="ml-auto text-[10px] text-slate-400">auto</span>
                  </div>
                </div>
              </div>

              <div className="md:col-span-3">
                <div key={active + "-preview"} className="anim-slide-up rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-lg overflow-hidden">
                  <div className="flex items-center gap-1.5 px-4 py-2.5 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950">
                    <span className="w-2 h-2 rounded-full bg-red-400" />
                    <span className="w-2 h-2 rounded-full bg-amber-400" />
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span className="ml-3 text-[10px] font-mono text-slate-400 truncate">{current.label.toLowerCase()}.output</span>
                  </div>
                  <div className="p-5">
                    <div className="text-[10px] uppercase tracking-widest font-semibold mb-3" style={{ color: current.accent }}>
                      {active === 0 && "Patient says"}
                      {active === 1 && "31 regions extracted"}
                      {active === 2 && "6 facts"}
                      {active === 3 && "8 events"}
                      {active === 4 && "Clinical narrative"}
                      {active === 5 && "Bundle (6 resources)"}
                    </div>
                    {active === 0 && (
                      <div className="rounded-lg border px-4 py-3 text-sm italic text-slate-700 dark:text-slate-200"
                           style={{ borderColor: current.accent + "33", background: current.accent + "11" }}>
                        "I have had a headache for two days"
                      </div>
                    )}
                    {active === 1 && (
                      <ul className="space-y-1.5">
                        {["[0.96] DEA# GB 05455616", "[0.94] NAME John Smith", "[0.99] AGE 34", "[0.75] RX"].map((r, i) => (
                          <li key={i} className="flex items-center gap-2 text-xs">
                            <span className="w-1.5 h-1.5 rounded-full" style={{ background: current.accent }} />
                            <span className="font-mono text-slate-700 dark:text-slate-200">{r}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                    {active === 2 && (
                      <ul className="space-y-2">
                        {["Metoprolol 100mg BD", "Dorzolamide 10mg BD", "Cimetidine 50mg TDS (warn)"].map((r, i) => (
                          <li key={i} className="flex items-center justify-between gap-3 text-xs">
                            <span className="text-slate-800 dark:text-slate-100">{r}</span>
                            <span className="w-20 h-1 bg-slate-100 dark:bg-slate-800 rounded overflow-hidden">
                              <span className="block h-1" style={{ width: (90 - i * 5) + "%", background: current.accent }} />
                            </span>
                          </li>
                        ))}
                      </ul>
                    )}
                    {active === 3 && (
                      <div className="relative pl-4">
                        <div className="absolute top-0 bottom-0 left-1 w-0.5" style={{ background: current.accent + "44" }} />
                        <ul className="space-y-3">
                          {["2012-11-09  Metoprolol", "2012-11-09  Dorzolamide", "2012-11-09  Cimetidine"].map((r, i) => (
                            <li key={i} className="relative text-xs">
                              <span className="absolute -left-3 top-1.5 w-2 h-2 rounded-full" style={{ background: current.accent }} />
                              <span className="font-mono text-slate-700 dark:text-slate-200">{r}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {active === 4 && (
                      <pre className="text-[11px] leading-5 whitespace-pre-wrap font-mono text-slate-700 dark:text-slate-200">
{["Patient Summary", "34-year-old male, recorded 2012-11-09.", "", "Medication Profile", "- Metoprolol 100mg BD - beta-blocker", "- Dorzolamide 10mg BD - for glaucoma"].join("\n")}
                      </pre>
                    )}
                    {active === 5 && (
                      <div className="rounded-lg bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 p-3">
                        <ul className="space-y-1">
                          {["Patient/4d47bedd...", "Encounter/5d507cba...", "MedicationRequest x 4", "Condition x 2"].map((r, i) => (
                            <li key={i} className="text-xs font-mono text-slate-700 dark:text-slate-200">
                              <span style={{ color: current.accent }}>-</span> {r}
                            </li>
                          ))}
                        </ul>
                        <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center gap-2 text-[10px] text-emerald-600 dark:text-emerald-400">
                          <span className="w-4 h-4 rounded-full bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center text-emerald-700 dark:text-emerald-300">
                            <IconCheck className="w-2.5 h-2.5" />
                          </span>
                          HAPI validation: 0 errors, 0 warnings
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 flex items-center justify-center gap-3 text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-widest">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                Live
              </span>
              <span className="font-mono text-slate-400">{traveling ? "payload moving..." : "stage settled"}</span>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ============ FHIR explorer (NEW) ============ */

function FhirExplorer() {
  const resources = [
    {
      name: "Patient",
      color: "#3b82f6",
      fields: [
        { k: "resourceType", v: '"Patient"' },
        { k: "id", v: '"4d47bedd-7f8f-46fe-88c0-c7d4b..."' },
        { k: "identifier[0].system", v: '"https://medigraph.example.com/patient-id"' },
        { k: "identifier[0].value", v: '"SYN-069"' },
        { k: "active", v: "true" },
      ],
    },
    {
      name: "Encounter",
      color: "#10b981",
      fields: [
        { k: "resourceType", v: '"Encounter"' },
        { k: "status", v: '"finished"' },
        { k: "class.code", v: '"AMB"' },
        { k: "subject.reference", v: '"Patient/4d47bedd-..."' },
        { k: "period.start", v: '"2012-11-09T00:00:00Z"' },
      ],
    },
    {
      name: "MedicationRequest",
      color: "#a855f7",
      fields: [
        { k: "resourceType", v: '"MedicationRequest"' },
        { k: "status", v: '"active"' },
        { k: "intent", v: '"order"' },
        { k: "medicationCodeableConcept.text", v: '"Metoprolol"' },
        { k: "dosageInstruction[0].text", v: '"100.0mg BD"' },
        { k: "authoredOn", v: '"2012-11-09T00:00:00Z"' },
      ],
    },
    {
      name: "Condition",
      color: "#f59e0b",
      fields: [
        { k: "resourceType", v: '"Condition"' },
        { k: "clinicalStatus.coding[0].code", v: '"active"' },
        { k: "code.text", v: '"chest pain"' },
        { k: "subject.reference", v: '"Patient/4d47bedd-..."' },
      ],
    },
    {
      name: "Bundle",
      color: "#6366f1",
      fields: [
        { k: "resourceType", v: '"Bundle"' },
        { k: "type", v: '"collection"' },
        { k: "entry", v: "[ 6 resources ]" },
        { k: "id", v: '"3e3ae2bc-1e49-4773-bb0c-025051..."' },
      ],
    },
  ];
  const [active, setActive] = useState(0);
  const cur = resources[active];

  return (
    <section id="fhir" className="relative max-w-6xl mx-auto px-8 py-24 z-10">
      <Reveal>
        <div className="text-center max-w-2xl mx-auto">
          <p className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest">Interoperability</p>
          <h2 className="mt-3 text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">The actual FHIR output.</h2>
          <p className="mt-4 text-slate-600 dark:text-slate-400">
            Click any resource type to inspect its fields. This is what a receiving ABDM system will parse.
          </p>
        </div>
      </Reveal>

      <Reveal delay={150}>
        <div className="mt-14 grid md:grid-cols-5 gap-6">
          {/* Resource chips */}
          <div className="md:col-span-2 space-y-2">
            {resources.map((r, i) => {
              const selected = i === active;
              return (
                <button
                  key={r.name}
                  onClick={() => setActive(i)}
                  className={
                    "w-full text-left px-4 py-3 rounded-xl border transition-all flex items-center justify-between " +
                    (selected
                      ? "border-transparent shadow-lg -translate-y-0.5 bg-white dark:bg-slate-900"
                      : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-slate-300")
                  }
                  style={{
                    borderColor: selected ? r.color + "66" : undefined,
                    boxShadow: selected ? "0 12px 30px " + r.color + "22" : undefined,
                  }}
                >
                  <div className="flex items-center gap-3">
                    <span className="w-2 h-6 rounded-full" style={{ background: r.color }} />
                    <div>
                      <div className={"text-[10px] uppercase tracking-widest font-semibold " + (selected ? "" : "text-slate-400")}
                           style={{ color: selected ? r.color : undefined }}>
                        Resource
                      </div>
                      <div className="text-sm font-medium text-slate-800 dark:text-slate-100">{r.name}</div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">{r.fields.length} fields</span>
                </button>
              );
            })}
          </div>

          {/* JSON viewer */}
          <div className="md:col-span-3">
            <div className="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 overflow-hidden shadow-lg">
              <div className="flex items-center gap-1.5 px-4 py-2.5 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950">
                <span className="w-2 h-2 rounded-full bg-red-400" />
                <span className="w-2 h-2 rounded-full bg-amber-400" />
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span className="ml-3 text-[10px] font-mono text-slate-400 truncate">{cur.name.toLowerCase()}.json</span>
              </div>
              <div className="p-5">
                <div className="rounded-lg bg-slate-950 text-slate-100 p-4 font-mono text-[11px] leading-6 overflow-auto">
                  <div className="text-slate-500">{"{"}</div>
                  {cur.fields.map((f, i) => (
                    <div key={i} className="anim-slide-up" style={{ animationDelay: i * 60 + "ms" }}>
                      <span className="text-slate-500 pl-4">"</span>
                      <span style={{ color: cur.color }}>{f.k}</span>
                      <span className="text-slate-500">"</span>
                      <span className="text-slate-500">: </span>
                      <span className="text-emerald-300">{f.v}</span>
                      {i < cur.fields.length - 1 && <span className="text-slate-500">,</span>}
                    </div>
                  ))}
                  <div className="text-slate-500">{"}"}</div>
                </div>

                <div className="mt-4 flex items-center justify-between text-[11px]">
                  <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                    <span className="w-4 h-4 rounded-full bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center text-emerald-700 dark:text-emerald-300">
                      <IconCheck className="w-2.5 h-2.5" />
                    </span>
                    HL7 HAPI validator: 0 errors
                  </div>
                  <span className="text-slate-400">ABDM FHIR R4 profile</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Reveal>
    </section>
  );
}

/* ============ Problem ============ */

function ProblemSection() {
  return (
    <section className="relative max-w-6xl mx-auto px-8 py-24 z-10">
      <div className="grid md:grid-cols-2 gap-14 items-center">
        <Reveal>
          <div>
            <p className="text-sm font-semibold text-red-600 dark:text-red-400 uppercase tracking-widest">The problem</p>
            <h2 className="mt-3 text-4xl font-bold text-slate-900 dark:text-white leading-tight">Doctors get two to five minutes per patient.</h2>
            <p className="mt-5 text-slate-600 dark:text-slate-400 leading-relaxed">
              In high-volume government outpatient departments, clinicians must elicit history, examine,
              review fragmented prior records, decide, counsel, and prescribe - all within one short window.
            </p>
            <ul className="mt-8 space-y-4 text-slate-700 dark:text-slate-300">
              <Bullet red>Prior prescriptions and lab reports stay on paper.</Bullet>
              <Bullet red>Registration software captures demographics only.</Bullet>
              <Bullet red>Mobile apps require literacy and connectivity many patients lack.</Bullet>
              <Bullet red>Repeated questions waste clinician time and miss comorbidities.</Bullet>
            </ul>
          </div>
        </Reveal>
        <Reveal delay={150}>
          <div className="rounded-2xl bg-gradient-to-br from-red-50 to-amber-50 dark:from-red-950/30 dark:to-amber-950/30 border border-red-100 dark:border-red-900 p-8">
            <div className="flex items-baseline gap-3">
              <span className="text-7xl font-bold text-red-700 dark:text-red-400 tabular-nums">2-5</span>
              <span className="text-lg font-medium text-red-900 dark:text-red-300">min</span>
            </div>
            <div className="text-sm font-medium text-red-900 dark:text-red-300 mt-1">per consultation</div>
            <div className="mt-8 space-y-4">
              <TimeBar label="Elicit history" pct={35} />
              <TimeBar label="Review prior records" pct={18} />
              <TimeBar label="Examine" pct={25} />
              <TimeBar label="Decide + prescribe" pct={22} />
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

function Bullet({ children, red }: { children: React.ReactNode; red?: boolean }) {
  return (
    <li className="flex gap-3">
      <span className={"mt-2 w-1.5 h-1.5 rounded-full shrink-0 " + (red ? "bg-red-500" : "bg-emerald-500")} />
      <span>{children}</span>
    </li>
  );
}

function TimeBar({ label, pct }: { label: string; pct: number }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-600 dark:text-slate-400 mb-1"><span>{label}</span><span className="text-slate-400">{pct}%</span></div>
      <div className="h-2 bg-white dark:bg-slate-800 rounded overflow-hidden border border-red-100 dark:border-red-900">
        <div className="h-full bg-gradient-to-r from-red-400 to-amber-400 rounded" style={{ width: pct + "%" }} />
      </div>
    </div>
  );
}

/* ============ Features ============ */

function FeaturesGrid() {
  const items = [
    { title: "Multilingual intake",     body: "Voice and touch in English and Hindi.",                  gradient: "from-blue-500 to-indigo-500",     Icon: IconMic },
    { title: "Document intelligence",   body: "PaddleOCR reads prescriptions with bbox provenance.",    gradient: "from-purple-500 to-pink-500",     Icon: IconDoc },
    { title: "On-premises AI",          body: "MedGemma corrects OCR and maps brands to generics.",     gradient: "from-emerald-500 to-teal-500",    Icon: IconShield },
    { title: "Longitudinal timeline",   body: "Facts ordered chronologically. Conflicts stay visible.", gradient: "from-amber-500 to-orange-500",    Icon: IconChart },
    { title: "Evidence-linked summary", body: "Every statement links to its source fact.",              gradient: "from-cyan-500 to-blue-500",       Icon: IconNote },
    { title: "FHIR R4 export",          body: "Validated against HL7 HAPI with zero errors.",           gradient: "from-indigo-500 to-purple-500",   Icon: IconLink },
  ];
  return (
    <section className="relative max-w-6xl mx-auto px-8 py-24 z-10">
      <Reveal>
        <div className="text-center max-w-2xl mx-auto">
          <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-widest">What MediGraph does</p>
          <h2 className="mt-3 text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">A modular pipeline from the waiting room to the EHR.</h2>
        </div>
      </Reveal>
      <div className="mt-16 grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map((it, i) => {
          const Icon = it.Icon;
          return (
            <Reveal key={it.title} delay={i * 80}>
              <Tilt max={6}>
                <div className="group relative h-full rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 p-6 hover:shadow-2xl hover:border-transparent transition-shadow duration-300">
                  <div className={"absolute top-0 left-6 right-6 h-1 rounded-b-full bg-gradient-to-r " + it.gradient + " opacity-0 group-hover:opacity-100 transition-opacity"} />
                  <div className={"w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br text-white shadow-lg " + it.gradient}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="mt-5 text-lg font-semibold text-slate-900 dark:text-white">{it.title}</h3>
                  <p className="mt-2 text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{it.body}</p>
                </div>
              </Tilt>
            </Reveal>
          );
        })}
      </div>
    </section>
  );
}

/* ============ Personas ============ */

function Personas() {
  const items = [
    { role: "For patients",   title: "Nothing to install.",             body: "Answer in the language you think in. Speak or tap. See what your doctor will see.", color: "blue",    quote: "I spoke in Hindi and it understood me." },
    { role: "For clinicians", title: "A clear note in two minutes.",     body: "Every fact sourced. Every medication mapped. Approve, edit, or reject.",           color: "emerald", quote: "I stopped opening three separate systems." },
    { role: "For hospitals",  title: "Standards-compliant by default.",  body: "FHIR R4 validated. Consent-driven. Fully auditable.",                              color: "indigo",  quote: "The auditor found what she needed." },
  ];
  const accent: any = {
    blue:    { border: "border-blue-200 dark:border-blue-800",       bg: "bg-blue-50 dark:bg-blue-950/40",       text: "text-blue-700 dark:text-blue-300" },
    emerald: { border: "border-emerald-200 dark:border-emerald-800", bg: "bg-emerald-50 dark:bg-emerald-950/40", text: "text-emerald-700 dark:text-emerald-300" },
    indigo:  { border: "border-indigo-200 dark:border-indigo-800",   bg: "bg-indigo-50 dark:bg-indigo-950/40",   text: "text-indigo-700 dark:text-indigo-300" },
  };
  return (
    <section className="relative bg-slate-50 dark:bg-slate-950 border-y border-slate-200 dark:border-slate-800 py-24 z-10">
      <div className="max-w-6xl mx-auto px-8">
        <Reveal>
          <div className="text-center max-w-2xl mx-auto">
            <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-widest">Three audiences</p>
            <h2 className="mt-3 text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">Built for the whole room.</h2>
          </div>
        </Reveal>
        <div className="mt-14 grid md:grid-cols-3 gap-6">
          {items.map((it, i) => {
            const a = accent[it.color];
            return (
              <Reveal key={it.role} delay={i * 100}>
                <div className={"rounded-2xl border " + a.border + " bg-white dark:bg-slate-900 p-6 flex flex-col h-full"}>
                  <div className={"text-xs uppercase tracking-widest font-semibold " + a.text}>{it.role}</div>
                  <h3 className="mt-3 text-lg font-semibold text-slate-900 dark:text-white">{it.title}</h3>
                  <p className="mt-2 text-sm text-slate-600 dark:text-slate-300 leading-relaxed flex-1">{it.body}</p>
                  <div className={"mt-6 rounded-xl " + a.bg + " p-4"}>
                    <p className={"text-sm italic " + a.text}>"{it.quote}"</p>
                  </div>
                </div>
              </Reveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}

/* ============ FAQ ============ */

function FAQ() {
  const qs = [
    { q: "Does any patient data leave the device?", a: "No. OCR, language model, speech recognition, and FHIR assembly all run locally. This satisfies the DPDP Act 2023 by eliminating cross-border transfer." },
    { q: "Can the AI make a diagnosis?", a: "No. The system is a documentation aid. The LLM drafts a hedged clinical narrative. Alerts come from a deterministic rule engine. Three clinician verification gates exist." },
    { q: "What happens if the patient revokes consent?", a: "Every linked fact, document, timeline event, and summary draft is purged in one operation. The revocation is recorded in the audit log with exact counts." },
    { q: "Is the FHIR output standard-compliant?", a: "Yes. Bundles are validated against the official HL7 HAPI validator with zero errors, zero warnings." },
    { q: "Which languages are supported?", a: "English and Hindi for both voice and touch intake. Documents can be in either language." },
  ];
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section id="faq" className="relative max-w-3xl mx-auto px-8 py-24 z-10">
      <Reveal>
        <div className="text-center">
          <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-widest">Questions</p>
          <h2 className="mt-3 text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">Things people ask.</h2>
        </div>
      </Reveal>
      <div className="mt-12 space-y-3">
        {qs.map((item, i) => {
          const active = open === i;
          return (
            <button key={i} onClick={() => setOpen(active ? null : i)}
                    className={"w-full text-left rounded-2xl border p-5 transition-colors " + (active ? "border-blue-300 dark:border-blue-700 bg-blue-50/40 dark:bg-blue-950/30" : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-slate-300")}>
              <div className="flex items-center justify-between gap-4">
                <span className="font-medium text-slate-900 dark:text-white">{item.q}</span>
                <span className={"text-slate-400 transition-transform " + (active ? "rotate-180" : "")}>
                  <IconChevron />
                </span>
              </div>
              {active && <p className="mt-3 text-sm text-slate-600 dark:text-slate-300 leading-relaxed anim-slide-up">{item.a}</p>}
            </button>
          );
        })}
      </div>
    </section>
  );
}

/* ============ Final CTA ============ */

function FinalCTA() {
  return (
    <section className="relative max-w-6xl mx-auto px-8 pb-24 z-10">
      <Reveal>
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 p-12 md:p-16 text-center text-white shadow-2xl shadow-blue-500/30">
          <div className="absolute -top-24 -left-24 w-72 h-72 rounded-full bg-white/10 blur-3xl anim-pulse-glow" />
          <div className="absolute -bottom-24 -right-24 w-72 h-72 rounded-full bg-white/10 blur-3xl anim-pulse-glow" style={{ animationDelay: "1.5s" }} />
          <h2 className="relative text-3xl md:text-4xl font-bold">Ready to see it in action?</h2>
          <p className="relative mt-4 text-blue-100 max-w-xl mx-auto">Walk through the full pipeline: intake, upload, AI summary, and FHIR export.</p>
          <div className="relative mt-8 flex flex-wrap gap-3 justify-center">
            <Link href="/intake" className="px-6 py-3 rounded-lg bg-white text-blue-700 font-medium hover:bg-blue-50 transition shadow-lg hover:-translate-y-0.5">Start patient intake</Link>
            <Link href="/clinician" className="px-6 py-3 rounded-lg bg-white/10 border border-white/30 text-white font-medium hover:bg-white/20 transition">Open clinician dashboard</Link>
          </div>
        </div>
      </Reveal>
    </section>
  );
}

function Footer() {
  return (
    <footer className="relative border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 z-10">
      <div className="max-w-6xl mx-auto px-8 py-10 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate-500 dark:text-slate-400">
        <div><span className="font-semibold text-slate-800 dark:text-slate-200">MediGraph</span> - capstone project, MIET Jammu</div>
        <div className="flex gap-6">
          <Link href="/intake" className="hover:text-slate-800 dark:hover:text-slate-200">Intake</Link>
          <Link href="/clinician" className="hover:text-slate-800 dark:hover:text-slate-200">Clinician</Link>
          <Link href="/login" className="hover:text-slate-800 dark:hover:text-slate-200">Sign in</Link>
        </div>
      </div>
    </footer>
  );
}

/* ============ Toast ============ */

function ToastSimulator() {
  const messages = [
    { text: "Prescription uploaded", color: "bg-blue-500" },
    { text: "OCR complete: 31 regions", color: "bg-purple-500" },
    { text: "AI corrected 3 drug names", color: "bg-emerald-500" },
    { text: "Timeline rebuilt", color: "bg-amber-500" },
    { text: "AI note drafted", color: "bg-indigo-500" },
    { text: "Approved by clinician", color: "bg-emerald-600" },
    { text: "FHIR bundle valid", color: "bg-blue-600" },
  ];
  const [idx, setIdx] = useState(0);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const cycle = () => {
      setVisible(true);
      setTimeout(() => setVisible(false), 2400);
      setTimeout(() => setIdx(i => (i + 1) % messages.length), 3200);
    };
    const t = setTimeout(cycle, 1500);
    const iv = setInterval(cycle, 3200);
    return () => { clearTimeout(t); clearInterval(iv); };
  }, []);
  const m = messages[idx];
  return (
    <div className="fixed bottom-6 right-6 z-40 pointer-events-none">
      <div className={"flex items-center gap-3 rounded-xl bg-white dark:bg-slate-800 shadow-2xl border border-slate-200 dark:border-slate-700 pl-1 pr-5 py-2 transition-all duration-300 " + (visible ? "translate-x-0 opacity-100" : "translate-x-8 opacity-0")}>
        <span className={"w-8 h-8 rounded-lg flex items-center justify-center text-white " + m.color}>
          <IconCheck className="w-4 h-4" />
        </span>
        <span className="text-sm font-medium text-slate-800 dark:text-slate-200">{m.text}</span>
      </div>
    </div>
  );
}

/* ============ Keyframes ============ */

function Keyframes() {
  return (
    <style>{`
      @keyframes float-slow { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-12px); } }
      @keyframes float-slower { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-8px); } }
      @keyframes pulse-glow { 0%, 100% { opacity: 0.35; } 50% { opacity: 0.75; } }
      @keyframes slide-up { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
      @keyframes fade-particle { 0% { opacity: 1; transform: translate(-50%, -50%) scale(1); } 100% { opacity: 0; transform: translate(-50%, -50%) scale(2.5); } }
      .anim-float-slow { animation: float-slow 6s ease-in-out infinite; }
      .anim-float-slower { animation: float-slower 8s ease-in-out infinite; }
      .anim-pulse-glow { animation: pulse-glow 3s ease-in-out infinite; }
      .anim-slide-up { animation: slide-up 0.4s ease-out both; }
      .anim-marquee { animation: marquee 40s linear infinite; }
    `}</style>
  );
}