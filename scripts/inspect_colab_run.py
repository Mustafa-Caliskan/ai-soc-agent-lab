import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

nb_path = "Train_XLM_RoBERTa_v4.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb.get('cells', []))}")
for i, cell in enumerate(nb.get("cells", [])):
    cell_type = cell.get("cell_type")
    exec_count = cell.get("execution_count")
    source = "".join(cell.get("source", []))[:60].replace("\n", " ")
    outputs = cell.get("outputs", [])
    errors = [o for o in outputs if o.get("output_type") == "error"]
    err_count = len(errors)
    has_text = any("text" in o for o in outputs)
    has_image = any("image/png" in o.get("data", {}) for o in outputs)
    print(f"Cell {i:2d} [{cell_type:4s}] (exec: {str(exec_count):>4s}): errs={err_count}, img={str(has_image):5s}, text={str(has_text):5s} | {source}")

print("\n" + "="*80)
print("CHECKING ERRORS AND CELL OUTPUTS DETAIL:")
print("="*80)
for i, cell in enumerate(nb.get("cells", [])):
    outputs = cell.get("outputs", [])
    for o in outputs:
        if o.get("output_type") == "error":
            ename = o.get("ename", "Error")
            evalue = o.get("evalue", "")
            trace = "\n".join(o.get("traceback", []))
            print(f"\n--- ERROR IN CELL {i} ({ename}): {evalue} ---")
            print(trace[:1000])
        elif o.get("name") == "stdout" or o.get("name") == "stderr":
            text = "".join(o.get("text", []))
            if "error" in text.lower() or "exception" in text.lower() or "warning" in text.lower() or "val_loss" in text.lower() or "macro" in text.lower():
                print(f"\n[Cell {i} stdout snippet]:\n{text[:400]}")
