import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

nb_path = os.path.abspath("archive/colab_legacy_v22.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

legacy_benign = []
legacy_attack = []

# Regex patterns for Python string literals in lists
str_pattern = re.compile(r'["\']([^"\']{5,})["\']')

current_context = None

for i, cell in enumerate(nb["cells"]):
    source_lines = cell.get("source", [])
    src = "".join(source_lines)
    
    # Check variable names defined in cell
    for line in source_lines:
        lower = line.lower()
        if "benign" in lower and ("=" in lower or "[" in lower):
            current_context = "benign"
        elif "attack" in lower and ("=" in lower or "[" in lower):
            current_context = "attack"
        elif "zero_day_benign" in lower or "hard_benign" in lower or "short_benign" in lower:
            current_context = "benign"
        elif "zero_day_attack" in lower or "hard_attack" in lower or "short_attack" in lower:
            current_context = "attack"
            
        if current_context:
            for match in str_pattern.findall(line):
                m_clean = match.strip()
                if len(m_clean) > 8 and not m_clean.startswith("http") and not m_clean.endswith(".py") and not m_clean.endswith(".zip"):
                    if current_context == "benign":
                        legacy_benign.append(m_clean)
                    elif current_context == "attack":
                        legacy_attack.append(m_clean)

# Deduplicate
legacy_benign = list(set(legacy_benign))
legacy_attack = list(set(legacy_attack))

print(f"✅ Çıkarılan Eski Masum (Benign) Cümleler: {len(legacy_benign):,}")
print(f"✅ Çıkarılan Eski Saldırı (Attack) Cümleleri: {len(legacy_attack):,}")

# Save to json so we can easily import in Colab and scripts
out_json = os.path.abspath("data/legacy_handcrafted_prompts.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump({
        "benign": legacy_benign,
        "attack": legacy_attack
    }, f, ensure_ascii=False, indent=2)

print(f"💾 Kaydedildi: {out_json}")
