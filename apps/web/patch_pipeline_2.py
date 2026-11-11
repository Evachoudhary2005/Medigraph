from pathlib import Path

f = Path("src/app/intake/[patientId]/page.tsx")
content = f.read_text(encoding="utf-8")

# Find the existing "if (completed) { ... }" block and replace it fully
import re

pattern = r"  if \(completed\) \{.*?\n  \}\n\n  return \("

new_block = '''  if (completed) {
    return (
      <main className="relative min-h-screen bg-slate-50 dark:bg-[#070b18] flex items-center justify-center p-6">
        <div className="max-w-xl w-full anim-slide-up">
          {/* Stage progress card */}
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
                  : (lang === "en" ? "Preparing your report" : "\\u0906\\u092a\\u0915\\u0940 \\u0930\\u093f\\u092a\\u094b\\u0930\\u094d\\u091f \\u0924\\u0948\\u092f\\u093e\\u0930 \\u0939\\u094b \\u0930\\u0939\\u0940 \\u0939\\u0948")}
              </h1>
              <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                {lang === "en"
                  ? "This may take up to a minute."
                  : "\\u0907\\u0938\\u092e\\u0947\\u0902 \\u090f\\u0915 \\u092e\\u093f\\u0928\\u091f \\u0924\\u0915 \\u0932\\u0917 \\u0938\\u0915\\u0924\\u093e \\u0939\\u0948\\u0964"}
              </p>
            </div>

            {/* 3 stages */}
            <ol className="mt-8 space-y-4">
              <StageRow
                label={lang === "en" ? "Saving your answers" : "\\u0909\\u0924\\u094d\\u0924\\u0930 \\u0938\\u0939\\u0947\\u091c\\u0947 \\u091c\\u093e \\u0930\\u0939\\u0947 \\u0939\\u0948\\u0902"}
                state={stageState(pipelineStage, "saving")}
              />
              <StageRow
                label={lang === "en" ? "Building your health timeline" : "\\u0938\\u094d\\u0935\\u093e\\u0938\\u094d\\u0925\\u094d\\u092f \\u091f\\u093e\\u0907\\u092e\\u0932\\u093e\\u0907\\u0928 \\u092c\\u0928\\u093e\\u092f\\u093e \\u091c\\u093e \\u0930\\u0939\\u093e \\u0939\\u0948"}
                state={stageState(pipelineStage, "timeline")}
              />
              <StageRow
                label={lang === "en" ? "Generating AI clinical summary" : "AI \\u0928\\u0948\\u0926\\u093e\\u0928\\u093f\\u0915 \\u0938\\u093e\\u0930\\u093e\\u0902\\u0936 \\u092c\\u0928\\u093e\\u092f\\u093e \\u091c\\u093e \\u0930\\u0939\\u093e \\u0939\\u0948"}
                state={stageState(pipelineStage, "ai")}
              />
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
                      {lang === "en" ? "Sent to your physician" : "\\u0906\\u092a\\u0915\\u0947 \\u091a\\u093f\\u0915\\u093f\\u0924\\u094d\\u0938\\u0915 \\u0915\\u094b \\u092d\\u0947\\u091c\\u093e \\u0917\\u092f\\u093e"}
                    </div>
                    <p className="text-xs text-emerald-800/80 dark:text-emerald-300/80 mt-0.5">
                      {lang === "en"
                        ? "Your doctor will review it before your visit."
                        : "\\u0906\\u092a\\u0915\\u0947 \\u0921\\u0949\\u0915\\u094d\\u091f\\u0930 \\u0906\\u092a\\u0915\\u0940 \\u092f\\u093e\\u0924\\u094d\\u0930\\u093e \\u0938\\u0947 \\u092a\\u0939\\u0932\\u0947 \\u0907\\u0938\\u0915\\u0940 \\u0938\\u092e\\u0940\\u0915\\u094d\\u0937\\u093e \\u0915\\u0930\\u0947\\u0902\\u0917\\u0947\\u0964"}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="mt-6 flex flex-col gap-2">
              {pipelineStage === "done" && (
                <button
                  onClick={() => setCompleted(false)}
                  className="px-4 py-2.5 rounded-lg text-sm font-medium bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 transition-colors"
                >
                  {lang === "en" ? "Review my answers" : "\\u092e\\u0947\\u0930\\u0947 \\u0909\\u0924\\u094d\\u0924\\u0930 \\u0926\\u0947\\u0916\\u0947\\u0902"}
                </button>
              )}
              {pipelineStage === "error" && (
                <button
                  onClick={() => complete()}
                  className="px-4 py-2.5 rounded-lg text-sm font-medium bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 transition-colors"
                >
                  {lang === "en" ? "Try again" : "\\u092a\\u0941\\u0928\\u0903 \\u092a\\u094d\\u0930\\u092f\\u093e\\u0938 \\u0915\\u0930\\u0947\\u0902"}
                </button>
              )}
              <Link
                href={"/intake/" + patientId + "/documents"}
                className="px-4 py-2.5 rounded-lg text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors text-center"
              >
                {docs.length > 0
                  ? (lang === "en" ? "Add more documents" : "\\u0914\\u0930 \\u0926\\u0938\\u094d\\u0924\\u093e\\u0935\\u0947\\u091c\\u093c \\u091c\\u094b\\u0921\\u093c\\u0947\\u0902")
                  : (lang === "en" ? "Upload documents" : "\\u0926\\u0938\\u094d\\u0924\\u093e\\u0935\\u0947\\u091c\\u093c \\u0905\\u092a\\u0932\\u094b\\u0921")}
              </Link>
            </div>
          </div>

          {/* AI report preview */}
          {pipelineStage === "done" && aiReport?.narrative && (
            <details className="mt-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
              <summary className="cursor-pointer px-5 py-4 text-sm font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors select-none">
                {lang === "en" ? "Preview your AI-generated summary" : "AI \\u0938\\u093e\\u0930\\u093e\\u0902\\u0936 \\u0926\\u0947\\u0916\\u0947\\u0902"}
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
  }

  return ('''

new_content, n = re.subn(pattern, new_block, content, count=1, flags=re.DOTALL)
if n > 0:
    content = new_content
    print("  + replaced success screen with pipeline UI")
else:
    print("  ! could not find 'if (completed)' block to replace")

f.write_text(content, encoding="utf-8")
print("WROTE src/app/intake/[patientId]/page.tsx")
print("bytes:", f.stat().st_size)
