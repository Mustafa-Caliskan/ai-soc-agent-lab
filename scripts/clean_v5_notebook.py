import json
import ast
import shutil
import os
import base64

def clean_notebook(path):
    print(f"\nProcessing {path}...")
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    cells = nb["cells"]
    print(f"Original cell count: {len(cells)}")
    
    if len(cells) == 14:
        c10_src = "".join(cells[10]["source"])
        c11_src = "".join(cells[11]["source"])
        if "scores =" not in c10_src and "scores =" in c11_src:
            print("Deleting duplicate broken Cell 10...")
            del cells[10]
            print(f"New cell count: {len(cells)}")
    elif len(cells) == 13:
        print("Cell count is already 13 (duplicate cell 10 already removed).")
    
    # 3. Update Cell 8 titles (NeuralShield-v3 -> NeuralShield-v5)
    c8_src = "".join(cells[8]["source"])
    c8_src = c8_src.replace('NeuralShield-v3 (XLM-RoBERTa)', 'NeuralShield-v5 (XLM-RoBERTa)')
    c8_src = c8_src.replace('NeuralShield-v3 - Doğrulama Kümesi', 'NeuralShield-v5 - Doğrulama Kümesi')
    cells[8]["source"] = [l + "\n" for l in c8_src.split("\n")[:-1]] if c8_src.endswith("\n") else [l + "\n" for l in c8_src.split("\n")]
    print("Updated Cell 8 titles to NeuralShield-v5.")

    # 3.1 Embed verified NeuralShield-v5 images into Cell 8 inline outputs
    with open("docs/figures/sekil_1_loss_egrisi.png", "rb") as f_img1:
        b64_fig1 = base64.b64encode(f_img1.read()).decode("utf-8")
    with open("docs/figures/sekil_2_metrik_ilerlemesi.png", "rb") as f_img2:
        b64_fig2 = base64.b64encode(f_img2.read()).decode("utf-8")
    
    if len(cells[8].get("outputs", [])) >= 2:
        if "data" in cells[8]["outputs"][0] and "image/png" in cells[8]["outputs"][0]["data"]:
            cells[8]["outputs"][0]["data"]["image/png"] = b64_fig1
        if "data" in cells[8]["outputs"][1] and "image/png" in cells[8]["outputs"][1]["data"]:
            cells[8]["outputs"][1]["data"]["image/png"] = b64_fig2
        print("Embedded verified NeuralShield-v5 figures into Cell 8 outputs.")
    
    # 4. Enhance Determinism in Cell 3 (seeds)
    c3_src = "".join(cells[3]["source"])
    old_seed = "SEED = 42\nrandom.seed(SEED)"
    new_seed = """SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)
transformers.set_seed(SEED)
print(f"🔒 Tam Akademik Determinizm Aktif (Seed={SEED})")"""
    if old_seed in c3_src:
        c3_src = c3_src.replace(old_seed, new_seed)
        cells[3]["source"] = [l + "\n" for l in c3_src.split("\n")[:-1]] if c3_src.endswith("\n") else [l + "\n" for l in c3_src.split("\n")]
        print("Enhanced determinism seeds in Cell 3.")
    
    # 5. Renumber headings and verify AST
    for idx, c in enumerate(cells):
        if c["cell_type"] == "code":
            src = "".join(c["source"])
            try:
                ast.parse(src)
            except Exception as e:
                print(f"ERROR: Cell {idx} has invalid AST: {e}")
                raise e
            first_line = c["source"][0].strip() if c["source"] else ""
            print(f"Cell {idx:2d} [code] (outputs: {len(c.get('outputs', [])):2d}) -> {first_line[:65]}")
    
    # 6. Save cleaned notebook
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"Successfully cleaned and saved {path}!")

if __name__ == "__main__":
    clean_notebook("notebooks/Train_XLM_RoBERTa_v5.ipynb")
    clean_notebook("neuralshield_v5_academic_bundle/Train_XLM_RoBERTa_v5.ipynb")
