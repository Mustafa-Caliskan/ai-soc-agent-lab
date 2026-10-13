import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

nb_path = r"c:\Users\Mustafa\Downloads\Train_XLM_RoBERTa_v5.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells in downloaded v5: {len(nb.get('cells', []))}")
for i, cell in enumerate(nb.get("cells", [])):
    c_type = cell.get("cell_type")
    exec_count = cell.get("execution_count")
    source = "".join(cell.get("source", []))[:60].replace("\n", " ")
    outputs = cell.get("outputs", [])
    errors = [o for o in outputs if o.get("output_type") == "error"]
    err_count = len(errors)
    has_text = any("text" in o for o in outputs)
    has_image = any("image/png" in o.get("data", {}) for o in outputs)
    print(f"Cell {i:2d} [{c_type:4s}] (exec: {str(exec_count):>4s}): errs={err_count}, img={str(has_image):5s}, text={str(has_text):5s} | {source}")

print("\n" + "="*80)
print("CELL OUTPUTS AND METRICS DETAILED INSPECTION:")
print("="*80)

for i in range(5, len(nb.get("cells", []))):
    cell = nb["cells"][i]
    print(f"\n--- CELL {i} (exec: {cell.get('execution_count')}) ---")
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            print(f"[{o.get('name')}]:\n" + "".join(o.get("text", []))[:1500])
        elif o.get("output_type") == "execute_result":
            print("[exec_result]:\n" + str(o.get("data", {}).get("text/plain", ""))[:500])
        elif o.get("output_type") == "display_data":
            data = o.get("data", {})
            if "text/html" in data:
                print("[HTML]:\n" + "".join(data["text/html"])[:800])
            if "image/png" in data:
                print("[IMAGE]: PNG present (length:", len(data["image/png"]), ")")
        elif o.get("output_type") == "error":
            print(f"[ERROR]: {o.get('ename')}: {o.get('evalue')}")
            print("\n".join(o.get("traceback", []))[:800])
