from pathlib import Path

f = Path("src/app/intake/page.tsx")
content = f.read_text(encoding="utf-8")

# ---- 1. Auto-detect browser language on first mount (before any typing) ----
old_mount = '''  useEffect(() => { setMounted(true); }, []);'''

new_mount = '''  useEffect(() => {
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
  }, []);'''

if "On first load (no ID typed yet)" not in content:
    content = content.replace(old_mount, new_mount)
    print("  + added browser language detection")

# ---- 2. Persist the user's manual choice so we don't override it later ----
old_langtile_en = '''<LangTile checked={lang === "en"} onChange={() => setLang("en")} label="English" native="English" flag="EN" gradient="from-blue-500 to-indigo-500" />'''
new_langtile_en = '''<LangTile checked={lang === "en"} onChange={() => { setLang("en"); try { window.localStorage.setItem("mg-intake-lang", "en"); } catch {} }} label="English" native="English" flag="EN" gradient="from-blue-500 to-indigo-500" />'''

old_langtile_hi = '''<LangTile checked={lang === "hi"} onChange={() => setLang("hi")} label={t("s1.hi")} native={t("s1.hi")} flag="HI" gradient="from-emerald-500 to-teal-500" />'''
new_langtile_hi = '''<LangTile checked={lang === "hi"} onChange={() => { setLang("hi"); try { window.localStorage.setItem("mg-intake-lang", "hi"); } catch {} }} label={t("s1.hi")} native={t("s1.hi")} flag="HI" gradient="from-emerald-500 to-teal-500" />'''

if old_langtile_en in content:
    content = content.replace(old_langtile_en, new_langtile_en)
    print("  + persisted English choice")
if old_langtile_hi in content:
    content = content.replace(old_langtile_hi, new_langtile_hi)
    print("  + persisted Hindi choice")

# ---- 3. Existing-patient lookup already sets lang; make sure it also persists it ----
old_existing_lang = '''          if (match.preferred_language === "hi" || match.preferred_language === "en") {
            setLang(match.preferred_language as Lang);
          }'''

new_existing_lang = '''          if (match.preferred_language === "hi" || match.preferred_language === "en") {
            setLang(match.preferred_language as Lang);
            try { window.localStorage.setItem("mg-intake-lang", match.preferred_language); } catch {}
          }'''

if old_existing_lang in content:
    content = content.replace(old_existing_lang, new_existing_lang)
    print("  + persisted existing-patient language")

f.write_text(content, encoding="utf-8")
print("WROTE src/app/intake/page.tsx")
