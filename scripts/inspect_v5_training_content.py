import json
import re

nb_path = "notebooks/Train_XLM_RoBERTa_v5.ipynb"
nb = json.load(open(nb_path, encoding="utf-8"))

print(f"Total cells in {nb_path}: {len(nb['cells'])}")

# Cell 3 is data creation
c3 = "".join(nb["cells"][3]["source"])

matches = re.findall(r"load_dataset\(\s*[\'\"]([^\'\"]+)[\'\"]", c3)
print("\n--- Datasets Loaded in Cell 3 (v5 training) ---")
for m in sorted(set(matches)):
    print("  *", m)

# Let's inspect the sections in Cell 3
print("\n--- Major Sections in Cell 3 ---")
for line in c3.split("\n"):
    if line.strip().startswith("# =") or line.strip().startswith("# BÖLÜM") or "---" in line:
        if len(line.strip()) > 5:
            print(" ", line.strip()[:80])
