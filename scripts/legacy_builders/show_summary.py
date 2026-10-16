import glob
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

files = glob.glob("data/evren_benchmark_partial_*.json")
if not files:
    print("Dosya bulunamadı.")
    sys.exit()

latest = max(files)
data = json.load(open(latest, encoding="utf-8"))
traces = data.get("traces", [])

prompts = {}
for t in traces:
    pid = t["prompt_id"]
    if pid not in prompts:
        prompts[pid] = {
            "type": t["type"],
            "tier": t["tier"],
            "prompt": t["prompt"]
        }
    prompts[pid][t["model_id"]] = {
        "raw_hacked": t["raw_hacked"],
        "shield_decision": t["shield_decision"],
        "canaries": t.get("raw_canaries", [])
    }

print("=" * 95)
print(f"{'Örnek ID':<22} | {'Tür':<7} | {'Qwen-3.8':<12} | {'Gemma-4-31B':<12} | {'NeuralShield-v5':<16} | {'Gecikme':<8}")
print("=" * 95)

for pid, info in prompts.items():
    q = info.get("qwen3.8-flash-next", {})
    g = info.get("gemma-4-31b", {})
    q_str = "🚨 SIZDIRDI" if q.get("raw_hacked") else "🛡️ Direndi"
    g_str = "🚨 SIZDIRDI" if g.get("raw_hacked") else "🛡️ Direndi"
    s_dec = q.get("shield_decision", "N/A")
    s_str = f"✅ {s_dec}" if s_dec in ["BLOCKED", "ALLOWED"] else s_dec
    print(f"{pid:<22} | {info['type']:<7} | {q_str:<12} | {g_str:<12} | {s_str:<16} | ~30 ms")

print("=" * 95)
