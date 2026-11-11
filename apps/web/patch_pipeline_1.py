from pathlib import Path

f = Path("src/app/intake/[patientId]/page.tsx")
content = f.read_text(encoding="utf-8")

# ---------- 1. Add pipeline state ----------
old_state = '''  const [completed, setCompleted] = useState(false);
  const [finishing, setFinishing] = useState(false);'''

new_state = '''  const [completed, setCompleted] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [pipelineStage, setPipelineStage] = useState<"idle" | "saving" | "timeline" | "ai" | "done" | "error">("idle");
  const [aiReport, setAiReport] = useState<any | null>(null);
  const [pipelineError, setPipelineError] = useState<string | null>(null);'''

if "const [pipelineStage, setPipelineStage]" not in content:
    content = content.replace(old_state, new_state)
    print("  + added pipeline state")

# ---------- 2. Replace complete() with a full pipeline ----------
old_complete = '''  async function complete() {
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

new_complete = '''  async function complete() {
    if (!session || finishing) return;
    setFinishing(true);
    setPipelineError(null);
    setCompleted(true);
    setPipelineStage("saving");

    try {
      // ---------- Stage 1: mark the session complete ----------
      await fetch("/api/v1/intake-sessions/" + session.id + "/complete", { method: "POST" });
      setPipelineStage("timeline");

      // ---------- Stage 2: rebuild the timeline from answers + documents ----------
      await fetch("/api/v1/timeline/build/" + patientId, { method: "POST" });
      setPipelineStage("ai");

      // ---------- Stage 3: generate the AI clinical report ----------
      const report = await fetch(
        "/api/v1/summary/" + patientId + "/generate?actor=system",
        { method: "POST" }
      ).then(r => {
        if (!r.ok) throw new Error("AI generation failed: " + r.status);
        return r.json();
      });

      setAiReport(report);
      setPipelineStage("done");
    } catch (e: any) {
      setPipelineError(e?.message ?? String(e));
      setPipelineStage("error");
    } finally {
      setFinishing(false);
    }
  }'''

if 'setPipelineStage("saving")' in content:
    print("  = complete() already patched")
elif old_complete in content:
    content = content.replace(old_complete, new_complete)
    print("  + rewrote complete() as a pipeline")
else:
    print("  ! old complete() not found - checking current version")
    idx = content.find("async function complete")
    if idx > 0:
        print(content[idx:idx+600])

f.write_text(content, encoding="utf-8")
print("  staged: wrote complete()")
