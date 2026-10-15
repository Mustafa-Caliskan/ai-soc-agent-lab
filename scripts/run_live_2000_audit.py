"""
CyberTech NeuralShield-v5 - Tam 2.000 Örnek Canlı ve Bağımsız Denetim Koşucusu.
Her bir örneği sıfırdan Layer 0, Layer 1 ve Layer 2 ONNX INT8 modelinden geçirir.
Önceden hesaplanmış hiçbir değeri kullanmaz; tamamen canlı çıkarım yapar.
"""
import os
import sys
import json
import time
import math
from collections import defaultdict, Counter
from pathlib import Path

# UTF-8 ayarı
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from normalizer import normalize_for_analysis
from regex_rules import scan_text
from ml_model import MLSecurityModel
from shield_config import CONFIG

DATA_PATH = ROOT / "data" / "appsec_benchmark_2000.json"

def wilson_interval(k, n, z=1.95996):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(max(0.0, center - spread) * 100.0, 2), round(min(1.0, center + spread) * 100.0, 2))

def main():
    print("=" * 85)
    print("🛡️  NEURALSHIELD-v5: 2.000 ÖRNEK SIFIRDAN CANLI VE ŞEFFAF TEST KOŞUSU")
    print("=" * 85)

    if not DATA_PATH.exists():
        print(f"[-] Hata: {DATA_PATH} bulunamadı!")
        sys.exit(1)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"📂 Veri seti yüklendi: {len(dataset)} örnek")
    print(f"📦 Model yükleniyor (ONNX INT8)...")
    t_load = time.time()
    ml_model = MLSecurityModel()
    print(f"✅ Model hazır ({time.time() - t_load:.2f} saniye). Model yolu: {ml_model.model_path}")
    print(f"⚙️  Konfigürasyon: ml_block_threshold={CONFIG.get('ml_block_threshold', 70)}, regex_threshold={CONFIG.get('regex_block_score_threshold', 60)}, mode={CONFIG.get('decision_mode', 'or_gate')}")
    print("-" * 85)

    results = []
    latencies = []

    # İlerleme takibi
    total = len(dataset)
    t_start = time.time()

    for idx, item in enumerate(dataset, 1):
        text = item.get("text") or item.get("prompt", "")
        label = int(item.get("label", 0))  # 1 = Attack, 0 = Benign
        lang = item.get("language", "unknown")
        category = item.get("attack_family", "unknown")

        t0 = time.perf_counter()

        # ── Katman 0: Normalizasyon & Steganografi ──
        norm_res = normalize_for_analysis(text)
        clean_text = norm_res["clean_text"]
        analysis_text = norm_res["extended_text"]
        alerts = list(norm_res["alerts"])
        hard_stego = bool(norm_res["hard_stego_signal"])

        # ── Katman 1: Regex & Heuristics ──
        regex_hit, patterns, regex_score = scan_text(analysis_text)
        rot13_hit, r13_pats, r13_score = scan_text(norm_res.get("rot13_variant", ""))
        rev_hit, rev_pats, rev_score = scan_text(norm_res.get("reversed_variant", ""))
        leet_hit, leet_pats, leet_score = scan_text(norm_res.get("leetspeak_variant", ""))

        regex_hit = regex_hit or rot13_hit or rev_hit or leet_hit
        patterns = list(set(patterns + r13_pats + rev_pats + leet_pats))
        regex_score = max(regex_score, r13_score, rev_score, leet_score)

        # ── Katman 2: XLM-RoBERTa ONNX INT8 ML Modeli ──
        ml_res = ml_model.predict(analysis_text)
        ml_class = ml_res.get("ml_class", "Benign")
        ml_risk = ml_res.get("ml_risk_score", 0)

        # ── Karar Katmanı (OR-Gate) ──
        blocked = bool(
            hard_stego
            or regex_score >= CONFIG.get("regex_block_score_threshold", 60)
            or ml_risk >= CONFIG.get("ml_block_threshold", 70)
            or (regex_hit and ml_class == "Malicious")
        )

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(elapsed_ms)

        decision = "BLOCKED" if blocked else "ALLOWED"
        is_attack = (label == 1)

        # Doğruluk durumu
        if is_attack and blocked:
            outcome = "TP" # True Positive (Saldırı başarıyla yakalandı)
        elif is_attack and not blocked:
            outcome = "FN" # False Negative (Saldırı kaçtı)
        elif not is_attack and blocked:
            outcome = "FP" # False Positive (Masum metin yanlışlıkla engellendi)
        else:
            outcome = "TN" # True Negative (Masum metne doğru izin verildi)

        results.append({
            "id": item.get("id", f"SAMPLE_{idx:04d}"),
            "text": text,
            "label": label,
            "language": lang,
            "category": category,
            "decision": decision,
            "outcome": outcome,
            "ml_risk": ml_risk,
            "ml_class": ml_class,
            "regex_score": regex_score,
            "hard_stego": hard_stego,
            "latency_ms": round(elapsed_ms, 2)
        })

        if idx % 250 == 0 or idx == total:
            cur_time = time.time() - t_start
            cur_tp = sum(1 for r in results if r["outcome"] == "TP")
            cur_fn = sum(1 for r in results if r["outcome"] == "FN")
            cur_fp = sum(1 for r in results if r["outcome"] == "FP")
            cur_tn = sum(1 for r in results if r["outcome"] == "TN")
            cur_rec = (cur_tp / (cur_tp + cur_fn) * 100) if (cur_tp + cur_fn) else 0
            cur_fpr = (cur_fp / (cur_fp + cur_tn) * 100) if (cur_fp + cur_tn) else 0
            print(f"  [{idx:4d}/{total}] ({cur_time:.1f}s) -> Şu anki Recall: %{cur_rec:.1f} | FP Oranı: %{cur_fpr:.1f} | Ort. Gecikme: {sum(latencies)/len(latencies):.2f} ms")

    # ── Genel Metrikler ──
    tp = sum(1 for r in results if r["outcome"] == "TP")
    fn = sum(1 for r in results if r["outcome"] == "FN")
    fp = sum(1 for r in results if r["outcome"] == "FP")
    tn = sum(1 for r in results if r["outcome"] == "TN")

    total_attacks = tp + fn
    total_benign = fp + tn

    recall = (tp / total_attacks * 100.0) if total_attacks else 0.0
    fpr = (fp / total_benign * 100.0) if total_benign else 0.0
    precision = (tp / (tp + fp) * 100.0) if (tp + fp) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    accuracy = ((tp + tn) / total * 100.0) if total else 0.0

    rec_ci = wilson_interval(tp, total_attacks)
    fpr_ci = wilson_interval(fp, total_benign)

    latencies_sorted = sorted(latencies)
    p50_lat = latencies_sorted[int(len(latencies_sorted) * 0.50)]
    p95_lat = latencies_sorted[int(len(latencies_sorted) * 0.95)]
    p99_lat = latencies_sorted[int(len(latencies_sorted) * 0.99)]
    avg_lat = sum(latencies) / len(latencies)

    print("\n" + "=" * 85)
    print("🏆  GENEL TEST SONUÇLARI (N=2.000 ÖRNEK ÜZERİNDE)")
    print("=" * 85)
    print(f"  Toplam İncelenen Örnek       : {total}")
    print(f"  Toplam Saldırı (Label=1)     : {total_attacks}")
    print(f"  Toplam Masum Metin (Label=0) : {total_benign}")
    print("-" * 85)
    print(f"  Saldırı Bloklama (Recall)    : %{recall:.2f} ({tp}/{total_attacks})  [Wilson %95: %{rec_ci[0]} - %{rec_ci[1]}]")
    print(f"  Yanlış Pozitif (FP Oranı)    : %{fpr:.2f} ({fp}/{total_benign})   [Wilson %95: %{fpr_ci[0]} - %{fpr_ci[1]}]")
    print(f"  Hassasiyet (Precision)       : %{precision:.2f} ({tp}/{tp+fp})")
    print(f"  Macro F1 Skoru               : %{f1:.2f}")
    print(f"  Genel Doğruluk (Accuracy)    : %{accuracy:.2f} ({tp+tn}/{total})")
    print("-" * 85)
    print(f"  Gecikme İstatistikleri (CPU) : Ort: {avg_lat:.2f} ms | P50: {p50_lat:.2f} ms | P95: {p95_lat:.2f} ms | P99: {p99_lat:.2f} ms")
    print("=" * 85)

    # ── 12 Dil Bazında Kırılım ──
    print("\n🌍 12 DİL BAZINDA PERFORMANS KIRILIMI:")
    print("-" * 85)
    print(f"| {'Dil':<6} | {'Saldırı (TP/Total)':<20} | {'Recall':<10} | {'Masum FP (FP/Total)':<20} | {'FP Oranı':<10} |")
    print("|--------|----------------------|------------|----------------------|------------|")
    
    langs = sorted(list(set(r["language"] for r in results)))
    for l in langs:
        l_res = [r for r in results if r["language"] == l]
        l_tp = sum(1 for r in l_res if r["outcome"] == "TP")
        l_fn = sum(1 for r in l_res if r["outcome"] == "FN")
        l_fp = sum(1 for r in l_res if r["outcome"] == "FP")
        l_tn = sum(1 for r in l_res if r["outcome"] == "TN")
        l_atks = l_tp + l_fn
        l_bens = l_fp + l_tn
        l_rec = (l_tp / l_atks * 100.0) if l_atks else 0.0
        l_fpr = (l_fp / l_bens * 100.0) if l_bens else 0.0
        print(f"| {l:<6} | {l_tp:3d} / {l_atks:3d}              | %{l_rec:<8.1f} | {l_fp:3d} / {l_bens:3d}              | %{l_fpr:<8.1f} |")
    print("-" * 85)

    # ── En Dikkat Çeken 5 Kaçan Saldırı (False Negatives - Şeffaf İnceleme) ──
    print("\n🔍 ŞEFFAFLIK RAPORU: KAÇAN SALDIRILARDAN 5 ÖRNEK (False Negatives):")
    fns = [r for r in results if r["outcome"] == "FN"]
    for i, r in enumerate(fns[:5], 1):
        print(f"  {i}. [{r['language'].upper()}] (ML: {r['ml_risk']}, Regex: {r['regex_score']}) -> {repr(r['text'][:90])}")

    # ── En Dikkat Çeken 5 Yanlış Alarm (False Positives - Şeffaf İnceleme) ──
    print("\n🔍 ŞEFFAFLIK RAPORU: YANLIŞ ALARM VERİLEN 5 MASUM METİN (False Positives):")
    fps = [r for r in results if r["outcome"] == "FP"]
    for i, r in enumerate(fps[:5], 1):
        print(f"  {i}. [{r['language'].upper()}] (ML: {r['ml_risk']}, Regex: {r['regex_score']}, Stego: {r['hard_stego']}) -> {repr(r['text'][:90])}")

    # ── Sonuçları Kaydet ──
    out_file = ROOT / "data" / "live_2000_audit_results.json"
    summary_data = {
        "total": total,
        "total_attacks": total_attacks,
        "total_benign": total_benign,
        "recall_pct": round(recall, 2),
        "recall_wilson_95": rec_ci,
        "fpr_pct": round(fpr, 2),
        "fpr_wilson_95": fpr_ci,
        "precision_pct": round(precision, 2),
        "f1_score": round(f1, 2),
        "accuracy_pct": round(accuracy, 2),
        "latency_avg_ms": round(avg_lat, 2),
        "latency_p50_ms": round(p50_lat, 2),
        "latency_p95_ms": round(p95_lat, 2),
        "latency_p99_ms": round(p99_lat, 2)
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"summary": summary_data, "details": results}, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Tüm 2.000 satır detaylı çıktı kaydedildi: {out_file}")

if __name__ == "__main__":
    main()
