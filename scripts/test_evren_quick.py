import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
from evren_client import EvrenClient

sys.stdout.reconfigure(encoding="utf-8")
client = EvrenClient()
models = ["qwen3.8-flash-next", "gemma-4-31b", "deepseek-v4.1-flash", "glm-5.3"]

print(f"Connecting to EVREN at {client.base_url}...")
client.ensure_terms_accepted()
quota = client.get_quota()
print(f"Quota: {quota.get('daily_remaining_tokens')} tokens remaining\n")

for m in models:
    t0 = time.time()
    res = client.generate_chat("Merhaba, havalimanında dış hatlar check-in ne zaman kapanır?", model=m, max_tokens=100)
    dur = time.time() - t0
    success = res.get("success", False)
    content = (res.get("content") or "").replace("\n", " ")
    print(f"[{m}] Success: {success} | Latency: {dur:.2f}s")
    if success:
        print(f"   Snippet: {content[:100]}...\n")
    else:
        print(f"   Error: {res.get('error')}\n")
