import json
import re

replacement_b75 = '''# ==============================================================================
# BÖLÜM 7.5: v5 ÖZEL TÜRKÇE OTORİTE BYPASS, EVASION VE SİBER GÜVENLİK HAVUZLARI
# ==============================================================================
print("\\n--- v5 Özel Bilişim Masum ve Sinsi Saldırı Havuzları Enjekte Ediliyor ---")

def load_hf_df_robust(dataset_name, preferred_splits=["train", "turkish"]):
    """Hugging Face veri setini uygun split ile güvenle yükleyip DataFrame döndürür."""
    for sp in preferred_splits:
        try:
            return load_dataset(dataset_name, split=sp).to_pandas()
        except Exception:
            continue
    try:
        ds = load_dataset(dataset_name)
        first_split = list(ds.keys())[0]
        return ds[first_split].to_pandas()
    except Exception as e:
        print(f"⚠️ {dataset_name} yüklenemedi: {e}")
        return None

def extract_chat_or_text(df, preferred_cols=None):
    """Pandas DataFrame içindeki string veya ShareGPT/Chat dict formatlı mesajları güvenle çıkarır."""
    if df is None or len(df) == 0:
        return []
    candidates = (preferred_cols or []) + ["prompt", "text", "payload", "evaded_text", "instruction", "input", "train"]
    target_col = None
    for c in candidates:
        if c in df.columns:
            target_col = c
            break
    if target_col is None:
        target_col = df.columns[0]
    
    extracted = []
    for val in df[target_col].dropna():
        if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict) and "content" in val[0]:
            s = str(val[0]["content"]).strip()
        elif isinstance(val, dict) and "content" in val:
            s = str(val["content"]).strip()
        else:
            s = str(val).strip()
        if len(s) >= 8:
            extracted.append(s)
    return extracted

# 1. 3nesdeniz Sinsi Konuşma Kılıflı Saldırılar & Masum Günlük Sohbetler
try:
    ds_sinsi = load_hf_df_robust("3nesdeniz/turkish-conversation-prompt-injection", preferred_splits=["train"])
    if ds_sinsi is not None and "label" in ds_sinsi.columns and "text" in ds_sinsi.columns:
        s_att = safe_clean(ds_sinsi[ds_sinsi["label"].astype(str) == "1"]["text"])
        s_ben = safe_clean(ds_sinsi[ds_sinsi["label"].astype(str) == "0"]["text"])
        attacks_pool.extend(s_att)
        benign_pool.extend(s_ben)
        print(f"✅ 3nesdeniz/turkish-conversation-prompt-injection: {len(s_att):,} sinsi saldırı, {len(s_ben):,} masum eklendi.")
except Exception as e:
    print(f"⚠️ 3nesdeniz atlandı: {e}")

# 2. sadecebirisii Otorite Bypass, Role Stealing ve Geliştirici Kılıflı Saldırılar
try:
    ds_auth = load_hf_df_robust("sadecebirisii/turkish-llm-authority-bypass-safety-sft", preferred_splits=["train"])
    auth_attacks = extract_chat_or_text(ds_auth, preferred_cols=["prompt", "text", "train"])
    auth_cleaned = safe_clean(auth_attacks)
    attacks_pool.extend(auth_cleaned * 3)  # Yüksek öncelikli kılıf koruması
    print(f"✅ sadecebirisii/turkish-llm-authority-bypass-safety-sft: {len(auth_cleaned):,} yetki delme saldırısı eklendi.")
except Exception as e:
    print(f"⚠️ Authority bypass atlandı: {e}")

# 3. fevziegeyurtsevenler Türkçe Evasion ve Karakter Manipülasyonları
try:
    ds_evasion = load_hf_df_robust("fevziegeyurtsevenler/turkish-casefold-evasion", preferred_splits=["train"])
    evasion_attacks = extract_chat_or_text(ds_evasion, preferred_cols=["evaded_text", "payload", "text"])
    evasion_cleaned = safe_clean(evasion_attacks)
    attacks_pool.extend(evasion_cleaned)
    print(f"✅ fevziegeyurtsevenler/turkish-casefold-evasion: {len(evasion_cleaned):,} karakter evasion saldırısı eklendi.")
except Exception as e:
    print(f"⚠️ Evasion atlandı: {e}")

# 4. logicBombExe Türkçe Siber Güvenlik Kontrolleri ve Ağ Mimarisi (Teknik Masumlar)
try:
    ds_cyber = load_hf_df_robust("logicBombExe/turkish_cyber_security_controls_dataset", preferred_splits=["turkish", "train"])
    cyber_benigns = extract_chat_or_text(ds_cyber, preferred_cols=["text", "prompt", "train"])
    cyber_cleaned = safe_clean(cyber_benigns)
    benign_pool.extend(cyber_cleaned)
    print(f"✅ logicBombExe/turkish_cyber_security_controls_dataset: {len(cyber_cleaned):,} teknik siber masum eklendi.")
except Exception as e:
    print(f"⚠️ Cyber controls atlandı: {e}")
'''

for nb_path in ["Train_XLM_RoBERTa_v5.ipynb", "notebooks/Train_XLM_RoBERTa_v5.ipynb"]:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    c3_src = "".join(nb["cells"][3]["source"])
    
    start_str = "# ==============================================================================\n# BÖLÜM 7.5:"
    end_str = "# ==============================================================================\n# BÖLÜM 8:"
    
    if start_str in c3_src and end_str in c3_src:
        idx1 = c3_src.find(start_str)
        idx2 = c3_src.find(end_str)
        c3_src = c3_src[:idx1] + replacement_b75 + "\n\n" + c3_src[idx2:]
        nb["cells"][3]["source"] = [l + "\n" for l in c3_src.split("\n")[:-1]]
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"[+] Replaced B7.5 with robust version in {nb_path}")
    else:
        print(f"[!] Could not locate B7.5 boundary in {nb_path}")
