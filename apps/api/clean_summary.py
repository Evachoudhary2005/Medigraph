import re
from pathlib import Path

f = Path("app/api/v1/summary.py")
lines = f.read_text(encoding="utf-8").splitlines()

funcs = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith("def "):
        start = i
        if i > 0 and lines[i - 1].lstrip().startswith("@"):
            start = i - 1
        end = i + 1
        while end < len(lines):
            nxt = lines[end]
            if nxt.startswith("def ") or nxt.startswith("@router.") or nxt.startswith("class "):
                break
            end += 1
        m = re.match(r"def (\w+)\(", line)
        if m:
            funcs.append({"name": m.group(1), "start": start, "end": end})
        i = end
    else:
        i += 1

seen = {}
keep = []
drop = []
for fn in funcs:
    if fn["name"] in seen:
        drop.append(fn)
    else:
        seen[fn["name"]] = fn
        keep.append(fn)

print(f"Functions found: {len(funcs)}")
print(f"Unique: {len(keep)}")
print(f"To drop: {len(drop)}")
for d in drop:
    print(f"  dropping def {d['name']} (lines {d['start']+1}-{d['end']})")

to_remove = sorted([(d["start"], d["end"]) for d in drop], reverse=True)
kept = list(lines)
for s, e in to_remove:
    del kept[s:e]

f.write_text("\n".join(kept) + "\n", encoding="utf-8")
print("CLEANED")
