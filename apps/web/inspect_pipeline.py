from pathlib import Path
f = Path("src/app/intake/[patientId]/page.tsx")
c = f.read_text(encoding="utf-8")

print("File size:", f.stat().st_size)
print()
print("Marker checks:")
print("  pipelineStage in file:",  "pipelineStage" in c)
print("  StageRow in file:      ",  "function StageRow" in c)
print("  stageState in file:    ",  "function stageState" in c)
print("  OLD 'Intake submitted':",  "Intake submitted" in c)
print()
print("Lines around 'if (completed)':")
lines = c.splitlines()
for i, line in enumerate(lines):
    if "if (completed)" in line:
        for j in range(i, min(i+40, len(lines))):
            print(f"{j+1:5}  {lines[j]}")
        break
