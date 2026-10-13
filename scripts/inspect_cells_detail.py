import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

nb_path = "Train_XLM_RoBERTa_v4.ipynb"
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for i in range(4, 13):
    cell = nb["cells"][i]
    print(f"\n{'='*70}\nCELL {i} DETAILS (exec count: {cell.get('execution_count')})\n{'='*70}")
    print("SOURCE:")
    source_lines = cell.get("source", [])
    print("".join(source_lines[:20]))
    if len(source_lines) > 20:
        print(f"... ({len(source_lines) - 20} more lines) ...")
        print("".join(source_lines[-10:]))
    
    print("\nOUTPUTS:")
    for out in cell.get("outputs", []):
        if out.get("output_type") == "stream":
            print("STREAM (" + out.get("name") + "):\n" + "".join(out.get("text", [])))
        elif out.get("output_type") == "execute_result":
            print("EXEC_RESULT:\n" + str(out.get("data", {}).get("text/plain", "")))
        elif out.get("output_type") == "display_data":
            keys = list(out.get("data", {}).keys())
            print("DISPLAY_DATA keys:", keys)
        elif out.get("output_type") == "error":
            print("ERROR:", out.get("ename"), out.get("evalue"))
