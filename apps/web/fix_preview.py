from pathlib import Path

f = Path("src/app/clinician/ai-review/page.tsx")
content = f.read_text(encoding="utf-8")

# 1. Change "Latest version preview" box to always show the full text
old_preview = '''                    <pre className={
                      "whitespace-pre-wrap font-sans text-sm " +
                      (isExpanded ? "" : "line-clamp-4 max-h-24 overflow-hidden")
                    }>
                      {g.latest.preview}
                    </pre>
                    {g.latest.preview.length > 200 && (
                      <button
                        onClick={() => toggleExpand(g.patient_id)}
                        className="mt-2 text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline">
                        {isExpanded ? "Show less" : "Show full text"}
                      </button>
                    )}'''

new_preview = '''                    <pre className="whitespace-pre-wrap font-sans text-sm">
                      {g.latest.preview}
                    </pre>'''

if old_preview in content:
    content = content.replace(old_preview, new_preview)
    print("  + preview now always shows full text")
else:
    print("  ! preview block not found, checking current")
    idx = content.find("Latest version preview")
    if idx > 0:
        print(content[idx:idx+600])

# 2. Remove the unused expanded/toggleExpand state (keep it - harmless)
# Skip for now

f.write_text(content, encoding="utf-8")
print("WROTE src/app/clinician/ai-review/page.tsx")
print("bytes:", f.stat().st_size)
