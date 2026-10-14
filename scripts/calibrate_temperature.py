"""
CyberTech NeuralShield-v5 - Sıcaklık Kalibrasyonu (Temperature Scaling) Optimizasyon Scripti.
Referans: Guo et al., "On Calibration of Modern Neural Networks", ICML 2017.

Bu script, doğrulama veri kümesi (data/test_multilingual.csv) üzerindeki ham logit'leri çıkarır,
Negative Log-Likelihood (NLL) fonksiyonunu minimize eden optimal Sıcaklık parametresini (T*)
Scipy optimizasyonu ile hesaplar ve ECE (Expected Calibration Error) düşüşünü raporlar.
Fitted T* değeri doğrudan backend/shield_config.json dosyasına yazılır.
"""
import os
import sys
import json
import logging
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

# Proje ana dizini
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.ml_model import MLSecurityModel
from backend.shield_config import CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TempCalibration")


def compute_ece(probs: np.ndarray, labels: np.ndarray, n_bins: int = 10) -> float:
    """Guo et al. (ICML 2017) uyarınca Expected Calibration Error (ECE) hesaplar."""
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n = len(labels)

    # İkili sınıflandırmada en yüksek olasılık ve tahmin edilen sınıf
    confidences = np.maximum(probs, 1.0 - probs)
    predictions = (probs >= 0.5).astype(int)
    accuracies = (predictions == labels).astype(int)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            avg_accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += np.abs(avg_accuracy_in_bin - avg_confidence_in_bin) * prop_in_bin

    return float(ece)


def nll_objective(temperature: float, logits_diff: np.ndarray, labels: np.ndarray) -> float:
    """Negative Log-Likelihood (NLL) kaybı."""
    if temperature <= 0.01:
        return 1e9
    scaled_diff = logits_diff / temperature
    # Sigmoid olasılıkları: P(Y=1) = 1 / (1 + exp(-scaled_diff))
    # Kararlı log-sum-exp formülasyonu:
    log_p1 = -np.logaddexp(0.0, -scaled_diff)
    log_p0 = -np.logaddexp(0.0, scaled_diff)
    
    loss = -np.mean(labels * log_p1 + (1.0 - labels) * log_p0)
    return float(loss)


def extract_raw_logits(ml_model: MLSecurityModel, texts: list) -> np.ndarray:
    """ONNX modelinden her bir metin için ham [z0, z1] logit vektörünü çeker."""
    logits_list = []
    logger.info(f"Modelden {len(texts)} örnek için ham logit çıkarımı yapılıyor...")
    
    bos_id = int(ml_model.tokenizer.bos_token_id if ml_model.tokenizer.bos_token_id is not None else 0)
    eos_id = int(ml_model.tokenizer.eos_token_id if ml_model.tokenizer.eos_token_id is not None else 2)

    for idx, text in enumerate(texts):
        encoded = ml_model.tokenizer(
            str(text),
            max_length=512,
            truncation=True,
            return_tensors="np"
        )
        inputs = {
            "input_ids": encoded["input_ids"].astype(np.int64),
            "attention_mask": encoded["attention_mask"].astype(np.int64)
        }
        outputs = ml_model.session.run(None, inputs)
        raw_logits = outputs[0][0]  # shape: (2,) -> [logit_benign, logit_malicious]
        logits_list.append(raw_logits)
        
        if (idx + 1) % 50 == 0 or (idx + 1) == len(texts):
            logger.info(f"İşlendi: {idx + 1}/{len(texts)}")

    return np.array(logits_list)


def main():
    logger.info("=== NeuralShield v5 Sıcaklık Kalibrasyonu (Temperature Scaling) Başlatılıyor ===")
    
    val_csv_path = os.path.join(ROOT_DIR, "data", "test_multilingual.csv")
    if not os.path.exists(val_csv_path):
        logger.error(f"Doğrulama veri seti bulunamadı: {val_csv_path}")
        sys.exit(1)

    df = pd.read_csv(val_csv_path)
    texts = df["text"].tolist()
    labels = np.array(df["label"].tolist(), dtype=np.float64)
    logger.info(f"Doğrulama veri seti yüklendi: {len(texts)} örnek (Malicious: {int(np.sum(labels))}, Benign: {int(len(labels) - np.sum(labels))})")

    ml_model = MLSecurityModel()
    if not ml_model.is_loaded:
        logger.error("ML modeli yüklenemedi!")
        sys.exit(1)

    # 1. Ham logitleri çıkar
    logits = extract_raw_logits(ml_model, texts)
    # logits_diff: z1 - z0 (Malicious vs Benign farkı)
    logits_diff = logits[:, 1] - logits[:, 0]

    # 2. Kalibrasyon Öncesi Metrikler (T = 1.0)
    uncalibrated_nll = nll_objective(1.0, logits_diff, labels)
    uncalibrated_probs = 1.0 / (1.0 + np.exp(-logits_diff))
    uncalibrated_ece = compute_ece(uncalibrated_probs, labels)

    logger.info(f"📊 Kalibrasyon Öncesi (T = 1.0): NLL = {uncalibrated_nll:.5f}, ECE = %{uncalibrated_ece * 100:.2f}")

    # 3. Sıcaklık Optimizasyonu: Scipy minimize_scalar ile optimal T bul
    res = minimize_scalar(
        nll_objective,
        bounds=(0.05, 5.0),
        args=(logits_diff, labels),
        method="bounded"
    )
    optimal_t = float(res.x)

    # 4. Kalibrasyon Sonrası Metrikler (T = T*)
    calibrated_nll = nll_objective(optimal_t, logits_diff, labels)
    calibrated_probs = 1.0 / (1.0 + np.exp(-logits_diff / optimal_t))
    calibrated_ece = compute_ece(calibrated_probs, labels)

    logger.info(f"🎯 Kalibrasyon Sonrası (T* = {optimal_t:.4f}): NLL = {calibrated_nll:.5f}, ECE = %{calibrated_ece * 100:.2f}")
    logger.info(f"📈 ECE İyileşmesi: %{uncalibrated_ece * 100:.2f} ➔ %{calibrated_ece * 100:.2f} (Delta: %{(uncalibrated_ece - calibrated_ece) * 100:.2f})")

    # 5. shield_config.json'a fitted T*'ı yaz
    config_path = os.path.join(ROOT_DIR, "backend", "shield_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        cfg["ml_temperature"] = round(optimal_t, 4)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ backend/shield_config.json güncellendi: ml_temperature = {round(optimal_t, 4)}")

    # 6. Sonuç Raporunu Kaydet
    report = {
        "calibration_timestamp": str(pd.Timestamp.now()),
        "validation_dataset": "data/test_multilingual.csv",
        "validation_samples": len(texts),
        "uncalibrated_temperature": 1.0,
        "uncalibrated_nll": round(uncalibrated_nll, 5),
        "uncalibrated_ece_pct": round(uncalibrated_ece * 100.0, 3),
        "fitted_optimal_temperature": round(optimal_t, 4),
        "calibrated_nll": round(calibrated_nll, 5),
        "calibrated_ece_pct": round(calibrated_ece * 100.0, 3),
        "ece_reduction_pct": round((uncalibrated_ece - calibrated_ece) * 100.0, 3)
    }
    report_path = os.path.join(ROOT_DIR, "data", "temperature_calibration_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Kalibrasyon raporu kaydedildi: {report_path}")


if __name__ == "__main__":
    main()
