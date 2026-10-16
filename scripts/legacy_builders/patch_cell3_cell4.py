import json

for path in ["Train_XLM_RoBERTa_v5.ipynb", "notebooks/Train_XLM_RoBERTa_v5.ipynb"]:
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    # ── FIX CELL 4: Import torch, nn, Trainer ──
    c4_lines = nb["cells"][4]["source"]
    new_c4 = []
    for line in c4_lines:
        if "from datasets import Dataset" in line:
            new_c4.append("import torch\n")
            new_c4.append("import torch.nn as nn\n")
            new_c4.append("from datasets import Dataset\n")
            new_c4.append("from transformers import AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding, Trainer\n")
        elif "from transformers import AutoTokenizer" in line:
            continue  # Already imported above
        else:
            new_c4.append(line)
    nb["cells"][4]["source"] = new_c4

    # ── FIX CELL 3: Remove .dropna() on list in extract_chat_or_text ──
    c3_lines = nb["cells"][3]["source"]
    c3_str = "".join(c3_lines)
    
    old_extract_loop = """    extracted = []
    for val in df[target_col].dropna():"""
    
    new_extract_loop = """    col_data = df[target_col]
    if hasattr(col_data, "dropna"):
        items = col_data.dropna()
    elif isinstance(col_data, list):
        items = [x for x in col_data if x is not None]
    else:
        items = list(col_data)

    extracted = []
    for val in items:"""
    
    if old_extract_loop in c3_str:
        c3_str = c3_str.replace(old_extract_loop, new_extract_loop)
        nb["cells"][3]["source"] = [l + "\n" for l in c3_str.split("\n")[:-1]]
        print(f"[+] Fixed extract_chat_or_text in Cell 3 for {path}")
    else:
        print(f"[!] Warning: old_extract_loop pattern not found in Cell 3 for {path}")
        
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"[+] Successfully patched Cell 4 in {path}")
