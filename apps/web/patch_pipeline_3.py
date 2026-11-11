from pathlib import Path

f = Path("src/app/intake/[patientId]/page.tsx")
content = f.read_text(encoding="utf-8")

# Check if helpers already exist
if "function StageRow(" in content:
    print("  = helpers already present")
else:
    helpers = '''

/* ============ pipeline helpers ============ */

function stageState(current: string, stage: string): "pending" | "active" | "done" {
  const order = ["saving", "timeline", "ai", "done"];
  const ci = order.indexOf(current);
  const si = order.indexOf(stage);
  if (current === "error") return "pending";
  if (ci > si) return "done";
  if (ci === si) return "active";
  return "pending";
}

function StageRow({ label, state }: { label: string; state: "pending" | "active" | "done" }) {
  return (
    <li className="flex items-center gap-3">
      <span className={"w-6 h-6 rounded-full flex items-center justify-center shrink-0 transition-all " + (
        state === "done"
          ? "bg-emerald-500 text-white"
          : state === "active"
          ? "border-2 border-blue-500 bg-blue-50 dark:bg-blue-950/40"
          : "border-2 border-slate-200 dark:border-slate-700 bg-transparent"
      )}>
        {state === "done" ? (
          <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        ) : state === "active" ? (
          <span className="w-3 h-3 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
        ) : null}
      </span>
      <span className={"text-sm transition-colors " + (
        state === "pending"
          ? "text-slate-400 dark:text-slate-500"
          : state === "active"
          ? "text-slate-900 dark:text-white font-medium"
          : "text-slate-700 dark:text-slate-300"
      )}>
        {label}
      </span>
    </li>
  );
}
'''

    content = content.rstrip() + "\n" + helpers
    f.write_text(content, encoding="utf-8")
    print("  + added StageRow + stageState helpers")

print("WROTE src/app/intake/[patientId]/page.tsx")
print("bytes:", f.stat().st_size)
