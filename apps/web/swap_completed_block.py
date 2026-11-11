from pathlib import Path
import re

f = Path("src/app/intake/[patientId]/page.tsx")
content = f.read_text(encoding="utf-8")

# Find the "if (completed) {" start
start_marker = "  if (completed) {"
start = content.find(start_marker)
if start < 0:
    print("ERROR: 'if (completed) {' not found")
    raise SystemExit(1)

# Find the "return (" that immediately follows the block — that's where the block ends
# The block ends with "  }\n\n  return ("
end_marker = "\n\n  return ("
end = content.find(end_marker, start)
if end < 0:
    print("ERROR: 'return (' after 'if (completed)' not found")
    raise SystemExit(1)

print(f"Replacing lines {content[:start].count(chr(10))+1} to {content[:end].count(chr(10))+1}")

new_block = '''  if (completed) {
    return (
      <main className="relative min-h-screen bg-slate-50 dark:bg-[#070b18] flex items-center justify-center p-6">
        <div className="max-w-xl w-full anim-slide-up">
          <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-xl">
            <div className="text-center">
              <div className="text-[10px] uppercase tracking-widest font-semibold text-slate-400">
                {pipelineStage === "done" || pipelineStage === "error" ? "Complete" : "Processing"}
              </div>
              <h1 className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
                {pipelineStage === "done"
                  ? (lang === "en" ? "Your report is ready" : "\\u0906\\u092a\\u0915\\u0940 \\u0930\\u093f\\u092a\\u094b\\u0930\\u094d\\u091f \\u0924\\u0948\\u092f\\u093e\\u0930 \\u0939\\u0948")
                  : pipelineStage === "error"
                  ? (lang === "en" ? "Something went wrong" : "\\u0915\\u0941\\u091b \\u0917\\u0932\\u0924 \\u0939\\u094b \\u0917\\u092f\\u093e")
                  : (lang === "en" ? "Preparing your report" : "\\u0930\\u093f\\u092a\\u094b\\u0930\\u094d\\u091f \\u0924\\u0948\\u092f\\u093e\\u0930 \\u0939\\u094b \\u0930\\u0939\\u0940 \\u0939\\u0948")}
              </h1>
              <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                {lang === "en" ? "This may take up to a minute." : "\\u0907\\u0938\\u092e\\u0947\\u0902 \\u090f\\u0915 \\u092e\\u093f\\u0928\\u091f \\u0924\\u0915 \\u0932\\u0917 \\u0938\\u0915\\u0924\\u093e \\u0939\\u0948\\u0964"}
              </p>
            </div>

            <ol className="mt-8 space-y-4">
              <StageRow label={lang === "en" ? "Saving your answers" : "\\u0909\\u0924\\u094d\\u0924\\u0930 \\u0938\\u0939\\u0947\\u091c\\u0947 \\u091c\\u093e \\u0930\\u0939\\u0947 \\u0939\\u0948\\u0902"} state={stageState(pipelineStage, "saving")} />
              <StageRow label={lang === "en" ? "Building your health timeline" : "\\u091f\\u093e\\u0907\\u092e\\u0932\\u093e\\u0907\\u0928 \\u092c\\u0928\\u093e\\u092f\\u093e \\u091c\\u093e \\u0930\\u0939\\u093e \\u0939\\u0948"} state={stageState(pipelineStage, "timeline")} />
              <StageRow label={lang === "en" ? "Generating AI clinical summary" : "AI \\u0938\\u093e\\u0930\\u093e\\u0902\\u0936 \\u092c\\u0928\\u093e\\u092f\\u093e \\u091c\\u093e \\u0930\\u0939\\u093e \\u0939\\u0948"} state={stageState(pipelineStage, "ai")} />
            </ol>

            {pipelineError && (
              <div className="mt-6 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 px-4 py-3 text-xs text-red-800 dark:text-red-300">
                {pipelineError}
              </div>
            )}

            {pipelineStage === "done" && (
              <div className="mt-6 rounded-xl border border-emerald-200 dark:border-emerald-900 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/30 p-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500 text-white flex items-center justify-center shrink-0 shadow-md shadow-emerald-500/30">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                      <polyline points="22 4 12 14.01 9 11.01" />
                    </svg>
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-emerald-900 dark:text-emerald-200">
                      {lang === "en" ? "Sent to your physician" : "\\u091a\\u093f\\u0915\\u093f\\u0924\\u094d\\u0938\\u0915 \\u0915\\u094b \\u092d\\u0947\\u091c\\u093e \\u0917\\u092f\\u093e"}
                    </div>
                    <p className="text-xs text-emerald-800/80 dark:text-emerald-300/80 mt-0.5">
                      {lang === "en" ? "Your doctor will review it before your visit." : "\\u0921\\u0949\\u0915\\u094d\\u091f\\u0930 \\u092f\\u093e\\u0924\\u094d\\u0930\\u093e \\u0938\\u0947 \\u092a\\u0939\\u0932\\u0947 \\u0938\\u092e\\u0940\\u0915\\u094d\\u0937\\u093e \\u0915\\u0930\\u0947\\u0902\\u0917\\u0947\\u0964"}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="mt-6 flex flex-col gap-2">
              {pipelineStage === "done" && (
                <button
                  onClick={() => setCompleted(false)}
                  className="px-4 py-2.5 rounded-lg text-sm font-medium bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 transition-colors">
                  {lang === "en" ? "Review my answers" : "\\u0909\\u0924\\u094d\\u0924\\u0930 \\u0926\\u0947\\u0916\\u0947\\u0902"}
                </button>
              )}
              {pipelineStage === "error" && (
                <button
                  onClick={() => complete()}
                  className="px-4 py-2.5 rounded-lg text-sm font-medium bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 transition-colors">
                  {lang === "en" ? "Try again" : "\\u092a\\u0941\\u0928\\u0903 \\u092a\\u094d\\u0930\\u092f\\u093e\\u0938"}
                </button>
              )}
            </div>
          </div>

          {pipelineStage === "done" && aiReport?.narrative && (
            <details className="mt-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
              <summary className="cursor-pointer px-5 py-4 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 transition-colors select-none">
                {lang === "en" ? "Preview your AI-generated summary" : "AI \\u0938\\u093e\\u0930\\u093e\\u0902\\u0936"}
              </summary>
              <div className="border-t border-slate-100 dark:border-slate-800 px-5 py-4">
                <pre className="text-xs whitespace-pre-wrap font-mono text-slate-700 dark:text-slate-300 max-h-96 overflow-auto leading-relaxed">
                  {aiReport.narrative}
                </pre>
              </div>
            </details>
          )}
        </div>
      </main>
    );
  }'''

content = content[:start] + new_block + content[end:]
f.write_text(content, encoding="utf-8")
print("WROTE src/app/intake/[patientId]/page.tsx")
print("bytes:", f.stat().st_size)

# Verify
raw = f.read_text(encoding="utf-8")
print("still has 'Intake submitted':", "Intake submitted" in raw)
print("has 'Preparing your report':", "Preparing your report" in raw)
print("has pipelineStage:", raw.count("pipelineStage"))
