"""
RoBERTa-large inference module – Layer 2 of the hybrid security system.
Loads model once at startup, then runs inference per request.
Falls back to heuristic demo mode if model files are missing.
"""
import os
import logging
import numpy as np
from typing import Dict

logger = logging.getLogger(__name__)

CLASS_NAMES = ["Benign", "Malicious"]


class MLSecurityModel:
    def __init__(self, model_path: str = "./saved_great_shield_v15"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.translator = None
        self.device = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM

            try:
                logger.info("Loading Translation Model (TR -> EN) on cpu...")
                self.tr_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-tr-en")
                self.tr_model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-tr-en")
                logger.info("✅ Translation Model loaded.")
            except Exception as e:
                logger.error(f"Failed to load translation model: {e}")
                self.tr_tokenizer = None
                self.tr_model = None

            if not os.path.exists(self.model_path):
                logger.warning(f"Model path '{self.model_path}' not found → DEMO mode active.")
                return

            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Loading RoBERTa model on {self.device}…")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_path, 
                num_labels=len(CLASS_NAMES)
            )
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            logger.info("✅ RoBERTa model loaded successfully.")
        except Exception as e:
            logger.error(f"Model load failed: {e} → DEMO mode active.")

    def predict(self, text: str) -> Dict:
        if not self.is_loaded:
            return self._demo_predict(text)
        try:
            import torch
            
            eval_text = text
            if self.tr_model and self.tr_tokenizer:
                try:
                    toks = self.tr_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
                    res = self.tr_model.generate(**toks)
                    translated = self.tr_tokenizer.decode(res[0], skip_special_tokens=True)
                    logger.info(f"[Translator] '{text}' -> '{translated}'")
                    eval_text = translated
                except Exception as e:
                    logger.error(f"Translation failed: {e}")
                    # Acil Durum Sözlüğü (Helsinki Modeli çalışmazsa devreye girer)
                    sozluk = {
                        "selam": "hello", "merhaba": "hello", "nasılsın": "how are you",
                        "şifre": "password", "veritabanı": "database", "kredi kartı": "credit card",
                        "liste": "list", "tümünü": "all", "yok say": "ignore", "kuralları": "rules"
                    }
                    eval_text = text.lower()
                    for tr, en in sozluk.items():
                        eval_text = eval_text.replace(tr, en)
                    logger.info(f"[Sözlük Çevirisi] '{text}' -> '{eval_text}'")

            inputs = self.tokenizer(
                eval_text, return_tensors="pt", truncation=True, max_length=512, padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.model(**inputs).logits
                probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()

            idx = int(np.argmax(probs))
            probs_dict = {n: float(p) for n, p in zip(CLASS_NAMES, probs)}
            return {
                "ml_class": CLASS_NAMES[idx],
                "ml_class_idx": idx,
                "ml_probabilities": probs_dict,
                "ml_risk_score": int((1.0 - probs_dict["Benign"]) * 100),
                "translated_text": eval_text,
            }
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return self._demo_predict(text)

    def _demo_predict(self, text: str) -> Dict:
        """Simple keyword heuristic used when the model is not loaded."""
        t = text.lower()
        inj  = sum(0.25 for kw in ["ignore all rules", "override system", "jailbreak mode", "dan mode", "forget instructions"] if kw in t)

        total = inj
        benign = max(0.05, 1.0 - min(total * 0.4, 0.95))
        rem = 1.0 - benign
        probs = {
            "Benign":    benign,
            "Malicious": rem,
        }
        # renormalize
        total_p = sum(probs.values())
        probs = {k: v / total_p for k, v in probs.items()}
        idx = int(np.argmax(list(probs.values())))
        return {
            "ml_class": CLASS_NAMES[idx],
            "ml_class_idx": idx,
            "ml_probabilities": probs,
            "ml_risk_score": int((1.0 - probs["Benign"]) * 100),
            "translated_text": text,
        }
