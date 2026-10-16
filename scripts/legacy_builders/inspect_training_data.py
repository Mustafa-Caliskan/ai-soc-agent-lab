import json

with open("notebooks/Train_XLM_RoBERTa_v3.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
for idx, cell in enumerate(nb['cells']):
    src = "".join(cell.get("source", []))
    if any(k in src for k in ["load_dataset", "dataset", "TURKISH", "BENIGN", "MALICIOUS", "corpus", "huggingface"]):
        first_line = src.strip().split("\n")[0][:100]
        print(f"Cell {idx} ({cell['cell_type']}): {first_line}")
        # print first few lines of relevant variables
        for line in src.split("\n"):
            if any(term in line for term in ["load_dataset", "TURKISH_BENIGN", "curated_", "datasets.load", "train_df"]):
                print(f"   -> {line[:120]}")
