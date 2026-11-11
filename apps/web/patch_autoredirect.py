from pathlib import Path

f = Path("src/app/intake/page.tsx")
content = f.read_text(encoding="utf-8")

# ---- 1. Add autoRedirecting state ----
if "autoRedirecting" not in content:
    content = content.replace(
        "const [idLocked, setIdLocked] = useState(false);",
        "const [idLocked, setIdLocked] = useState(false);\n"
        "  const [autoRedirecting, setAutoRedirecting] = useState(false);"
    )
    print("  + added autoRedirecting state")

# ---- 2. Add auto-redirect effect right after the lookup effect ----
anchor = "  }, [id, idLocked]);"
effect = '''  }, [id, idLocked]);

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
  }, [existing]);'''

if "Auto-redirect when an existing patient is detected" not in content:
    content = content.replace(anchor, effect)
    print("  + added auto-redirect effect")

# ---- 3. Add overlay to the JSX ----
old_main = '''<main className="relative min-h-screen overflow-hidden bg-slate-50 dark:bg-[#070b18]">
      <div aria-hidden className="pointer-events-none absolute inset-0">'''

overlay = '''<main className="relative min-h-screen overflow-hidden bg-slate-50 dark:bg-[#070b18]">
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

      <div aria-hidden className="pointer-events-none absolute inset-0">'''

if "Auto-redirect overlay" not in content:
    content = content.replace(old_main, overlay)
    print("  + added transition overlay")

f.write_text(content, encoding="utf-8")
print("WROTE src/app/intake/page.tsx")
