"""
CyberTech - EVREN LLM API Diagnostic & Sanity Test Tool
Tests terms acceptance, model enumeration, and basic inference on EVREN Platform.
"""
import os
import sys
import argparse
import requests
import json

# Ensure UTF-8 output in Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_BASE_URL = "https://evren-llmapi.ssyz.org.tr/v1"

def check_and_accept_terms(base_url: str, api_key: str):
    headers = {
        "X-API-Key": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    print(f"[*] Checking terms status on {base_url}...")
    try:
        resp = requests.get(f"{base_url}/terms/status", headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            curr_version = data.get("current_version", 1)
            accepted = data.get("accepted", False)
            print(f"[+] Terms status: current_version={curr_version}, accepted={accepted}")
            if not accepted:
                print(f"[*] Accepting terms version {curr_version}...")
                acc_resp = requests.post(f"{base_url}/terms/accept", headers=headers, json={"version": curr_version}, timeout=15)
                print(f"[+] Terms accept response: {acc_resp.status_code} - {acc_resp.text}")
            else:
                print("[+] Terms already accepted.")
            return True
        else:
            print(f"[!] Terms check returned HTTP {resp.status_code}: {resp.text}")
            # Try to accept version 1 just in case
            acc_resp = requests.post(f"{base_url}/terms/accept", headers=headers, json={"version": 1}, timeout=15)
            print(f"[*] Fallback terms accept (v1): {acc_resp.status_code} - {acc_resp.text}")
            return True
    except Exception as e:
        print(f"[-] Terms check error: {e}")
        return False

def list_models(base_url: str, api_key: str):
    headers = {
        "X-API-Key": api_key,
        "Authorization": f"Bearer {api_key}"
    }
    print(f"\n[*] Fetching available models from {base_url}/models...")
    try:
        resp = requests.get(f"{base_url}/models", headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            models = data.get("data", [])
            print(f"[+] Successfully retrieved {len(models)} models:")
            for m in models:
                mid = m.get("id") if isinstance(m, dict) else str(m)
                print(f"    - {mid}")
            return [m.get("id") if isinstance(m, dict) else str(m) for m in models]
        else:
            print(f"[-] Failed to fetch models: HTTP {resp.status_code}: {resp.text}")
            return []
    except Exception as e:
        print(f"[-] Error fetching models: {e}")
        return []

def test_completion(base_url: str, api_key: str, model_name: str, prompt: str = "Merhaba, sistem durumunu doğrula."):
    headers = {
        "X-API-Key": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 256,
        "temperature": 0.2
    }
    print(f"\n[*] Testing chat completion with model: '{model_name}'...")
    try:
        resp = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            res_json = resp.json()
            reply = res_json["choices"][0]["message"]["content"]
            usage = res_json.get("usage", {})
            print(f"[+] Success! Response from {model_name}:")
            print(f"    --- START REPLY ---")
            print(f"    {reply.strip()}")
            print(f"    --- END REPLY ---")
            print(f"[+] Usage: {usage}")
            return True
        else:
            print(f"[-] Completion failed: HTTP {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"[-] Completion exception: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="EVREN LLM API Connectivity Test")
    parser.add_argument("--api-key", default=os.getenv("EVREN_API_KEY", ""), help="EVREN API Key (evren_llm_...)")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base API URL")
    parser.add_argument("--model", default="qwen3.8-flash-next", help="Model ID to test")
    parser.add_argument("--prompt", default="Merhaba, kendini kısaca tanıtır mısın?", help="Test prompt")
    args = parser.parse_args()

    api_key = args.api_key.strip()
    if not api_key:
        print("[-] HATA: Lütfen bir API anahtarı sağlayın: --api-key evren_llm_... veya EVREN_API_KEY çevre değişkeni.")
        sys.exit(1)

    print("=" * 60)
    print("EVREN PLATFORMU API BAĞLANTI & SAĞLIK TESTİ")
    print("=" * 60)
    check_and_accept_terms(args.base_url, api_key)
    models = list_models(args.base_url, api_key)
    
    test_model = args.model
    if models and test_model not in models:
        print(f"[!] Belirtilen model '{test_model}' listede doğrudan görünmüyor, listedeki ilk model '{models[0]}' ile test edilebilir.")
    
    test_completion(args.base_url, api_key, test_model, args.prompt)

if __name__ == "__main__":
    main()
