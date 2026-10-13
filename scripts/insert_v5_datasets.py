import json
import ast

for nb_path in ["Train_XLM_RoBERTa_v5.ipynb", "notebooks/Train_XLM_RoBERTa_v5.ipynb"]:
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    c3_src = "".join(nb["cells"][3]["source"])
    
    new_v5_datasets = '''
# ==============================================================================
# BÖLÜM 7.5: v5 ÖZEL TÜRKÇE OTORİTE BYPASS, EVASION VE SİBER GÜVENLİK HAVUZLARI
# ==============================================================================
print("\\n--- v5 Özel Bilişim Masum ve Sinsi Saldırı Havuzları Enjekte Ediliyor ---")

# 1. 3nesdeniz Sinsi Konuşma Kılıflı Saldırılar & Masum Günlük Sohbetler
try:
    ds_sinsi = load_dataset("3nesdeniz/turkish-conversation-prompt-injection", split="train").to_pandas()
    if "label" in ds_sinsi.columns and "text" in ds_sinsi.columns:
        s_att = safe_clean(ds_sinsi[ds_sinsi["label"].astype(str) == "1"]["text"])
        s_ben = safe_clean(ds_sinsi[ds_sinsi["label"].astype(str) == "0"]["text"])
        attacks_pool.extend(s_att)
        benign_pool.extend(s_ben)
        print(f"✅ 3nesdeniz/turkish-conversation-prompt-injection: {len(s_att):,} sinsi saldırı, {len(s_ben):,} masum eklendi.")
except Exception as e:
    print(f"⚠️ 3nesdeniz atlandı: {e}")

# 2. sadecebirisii Otorite Bypass, Role Stealing ve Geliştirici Kılıflı Saldırılar
try:
    ds_auth = load_dataset("sadecebirisii/turkish-llm-authority-bypass-safety-sft", split="train").to_pandas()
    auth_attacks = []
    for row in ds_auth.get("train", []):
        if isinstance(row, list) and len(row) > 0 and isinstance(row[0], dict) and "content" in row[0]:
            auth_attacks.append(str(row[0]["content"]))
        elif isinstance(row, str):
            auth_attacks.append(row)
    auth_cleaned = safe_clean(auth_attacks)
    attacks_pool.extend(auth_cleaned * 3)  # Yüksek öncelikli kılıf koruması
    print(f"✅ sadecebirisii/turkish-llm-authority-bypass-safety-sft: {len(auth_cleaned):,} yetki delme saldırısı eklendi.")
except Exception as e:
    print(f"⚠️ Authority bypass atlandı: {e}")

# 3. fevziegeyurtsevenler Türkçe Evasion ve Karakter Manipülasyonları
try:
    ds_evasion = load_dataset("fevziegeyurtsevenler/turkish-casefold-evasion", split="train").to_pandas()
    e_col = "evaded_text" if "evaded_text" in ds_evasion.columns else ds_evasion.columns[0]
    evasion_attacks = safe_clean(ds_evasion[e_col])
    attacks_pool.extend(evasion_attacks)
    print(f"✅ fevziegeyurtsevenler/turkish-casefold-evasion: {len(evasion_attacks):,} karakter evasion saldırısı eklendi.")
except Exception as e:
    print(f"⚠️ Evasion atlandı: {e}")

# 4. logicBombExe Türkçe Siber Güvenlik Kontrolleri ve Ağ Mimarisi (Teknik Masumlar)
try:
    ds_cyber = load_dataset("logicBombExe/turkish_cyber_security_controls_dataset", split="turkish").to_pandas()
    cyber_benigns = []
    for row in ds_cyber.get("train", []):
        if isinstance(row, list) and len(row) > 0 and isinstance(row[0], dict) and "content" in row[0]:
            cyber_benigns.append(str(row[0]["content"]))
        elif isinstance(row, str):
            cyber_benigns.append(row)
    cyber_cleaned = safe_clean(cyber_benigns)
    benign_pool.extend(cyber_cleaned)
    print(f"✅ logicBombExe/turkish_cyber_security_controls_dataset: {len(cyber_cleaned):,} teknik siber masum eklendi.")
except Exception as e:
    print(f"⚠️ Cyber controls atlandı: {e}")

'''
    split_marker = "# BÖLÜM 8: METİN VE KARAKTER DÜZEYİ TEMİZ TEKİLLEŞTİRME VE DENGELİ ÖRNEKLEME"
    if split_marker in c3_src and "BÖLÜM 7.5:" not in c3_src:
        c3_src = c3_src.replace(split_marker, new_v5_datasets + "\n" + split_marker)
        nb["cells"][3]["source"] = [l + "\n" for l in c3_src.split("\n")[:-1]]
        with open(nb_path, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"[+] Successfully inserted BÖLÜM 7.5 into {nb_path}")
    else:
        print(f"[!] Marker check failed or already present in {nb_path}")
