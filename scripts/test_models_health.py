import sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import requests, time

models = ['qwen2.5:3b', 'llama3.2:3b', 'gemma2:2b', 'phi3:mini', 'qwen2.5:1.5b']
print("=" * 60)
print("Testing 5 Target Airline Chatbot Models on Ollama:")
print("=" * 60)

for m in models:
    t0 = time.time()
    try:
        r = requests.post('http://127.0.0.1:11434/api/chat', json={
            'model': m,
            'stream': False,
            'options': {'temperature': 0.1, 'num_predict': 15},
            'messages': [{'role': 'user', 'content': 'Merhaba, uçuşum saat kaçta?'}]
        }, timeout=45)
        dt = time.time() - t0
        content = r.json()['message']['content'].strip().replace("\n", " ")
        print(f"✅ {m:15} : {dt:5.2f}s | Yanıt: \"{content[:40]}...\"")
    except Exception as e:
        print(f"❌ {m:15} : HATA -> {e}")

print("=" * 60)
