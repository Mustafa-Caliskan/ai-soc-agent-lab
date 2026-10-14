import json
import ast
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

nb_path = "notebooks/Train_XLM_RoBERTa_v5.ipynb"
nb = json.load(open(nb_path, encoding="utf-8"))
print(f"Loaded {nb_path} - Total cells: {len(nb['cells'])}")

for i, cell in enumerate(nb["cells"]):
    c_type = cell["cell_type"]
    src = "".join(cell["source"])
    lines = len(cell["source"])
    first_line = cell["source"][0].strip() if cell["source"] else "EMPTY"
    
    ast_status = "N/A"
    if c_type == "code":
        try:
            ast.parse(src)
            ast_status = "VALID AST"
        except Exception as e:
            ast_status = f"SYNTAX ERROR: {e}"
            
    print(f"Cell {i:2d} [{c_type:4s}] ({lines:3d} lines, {ast_status:9s}) -> {first_line[:65]}")

print("\n" + "="*80)
print("DEEP AUDIT OF CRITICAL CELLS (4, 5, 10, 12):")
print("="*80)

# Check Cell 4
c4 = "".join(nb["cells"][4]["source"])
print(f"Cell 4 has CyberFocalLossTrainer: {'CyberFocalLossTrainer' in c4}")

# Check Cell 5
c5 = "".join(nb["cells"][5]["source"])
print(f"Cell 5 trainer is CyberFocalLossTrainer: {'trainer = CyberFocalLossTrainer(' in c5}")
print(f"Cell 5 num_train_epochs: {'num_train_epochs=2' in c5}")
print(f"Cell 5 metric_for_best_model: {'metric_for_best_model=\"eval_loss\"' in c5}")
print(f"Cell 5 output_dir is v5: {'checkpoints_xlm_roberta_v5' in c5}")

# Check Cell 10
c10 = "".join(nb["cells"][10]["source"])
print(f"Cell 10 has no old it_probe_queries bug: {'it_probe_queries' not in c10}")

# Check Cell 12
c12 = "".join(nb["cells"][12]["source"])
print(f"Cell 12 archive is v5: {'neuralshield_v5_academic_bundle' in c12}")
print(f"Cell 12 has files.download: {'files.download' in c12}")

