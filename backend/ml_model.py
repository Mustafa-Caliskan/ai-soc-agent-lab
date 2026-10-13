"""
NeuralShield v5 - XLM-RoBERTa ONNX INT8 Inference Engine.
Layer 2 of the 4-Layer Hybrid Peripheral Defense Architecture.
Native multilingual (Turkish & English) semantic classifier with ~12ms CPU inference.
"""
import os
import time
import logging
from typing import Dict, Any, Optional
import numpy as np

try:
    from backend.shield_config import CONFIG
except ImportError:
    try:
        from shield_config import CONFIG
    except ImportError:
        CONFIG = {}

logger = logging.getLogger(__name__)

CLASS_NAMES = ["Benign", "Malicious"]


class MLSecurityModel:
    def __init__(
        self,
        model_path: str = None,
        window_size: Optional[int] = None,
        stride: Optional[int] = None,
        temperature: Optional[float] = None,
        sliding_window_enabled: Optional[bool] = None,
    ):
        if model_path is None:
            # Priority: v5 (if available) -> v4 -> v3 -> fallback v2
            v5_local = os.path.join(os.path.dirname(__file__), "models", "neuralshield_v5")
            v4_local = os.path.join(os.path.dirname(__file__), "models", "neuralshield_v4")
            v3_local = os.path.join(os.path.dirname(__file__), "models", "neuralshield_v3")
            if os.path.exists(v5_local):
                self.model_path = v5_local
            elif os.path.exists(v4_local):
                self.model_path = v4_local
            elif os.path.exists(v3_local):
                self.model_path = v3_local
            else:
                self.model_path = os.path.join(os.path.dirname(__file__), "models", "neuralshield_v2")
        else:
            self.model_path = model_path

        self.window_size = window_size or CONFIG.get("ml_window_size", 256)
        self.stride = stride or CONFIG.get("ml_stride", 128)
        self.temperature = temperature if temperature is not None else CONFIG.get("ml_temperature", 1.0)
        self.sliding_window_enabled = (
            sliding_window_enabled if sliding_window_enabled is not None
            else CONFIG.get("ml_sliding_window_enabled", True)
        )

        self.session = None
        self.tokenizer = None
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        try:
            import onnxruntime as ort
            from transformers import AutoTokenizer

            # Check if path exists or resolve relative to current file
            target_path = self.model_path
            if not os.path.exists(target_path):
                # Try relative to this file's directory
                alt_path_v5 = os.path.join(os.path.dirname(__file__), "models", "neuralshield_v5")
                alt_path_v4 = os.path.join(os.path.dirname(__file__), "models", "neuralshield_v4")
                alt_path_v3 = os.path.join(os.path.dirname(__file__), "models", "neuralshield_v3")
                alt_path_v2 = os.path.join(os.path.dirname(__file__), "models", "neuralshield_v2")
                if os.path.exists(alt_path_v5):
                    target_path = alt_path_v5
                elif os.path.exists(alt_path_v4):
                    target_path = alt_path_v4
                elif os.path.exists(alt_path_v3):
                    target_path = alt_path_v3
                elif os.path.exists(alt_path_v2):
                    target_path = alt_path_v2
                else:
                    alt_root_v5 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "neuralshield_v5_academic_bundle"))
                    if os.path.exists(alt_root_v5):
                        target_path = alt_root_v5
                    else:
                        alt_root_v3 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "neuralshield_v3_academic_bundle"))
                        if os.path.exists(alt_root_v3):
                            target_path = alt_root_v3

            onnx_file = os.path.join(target_path, "model_quantized_int8.onnx")
            if not os.path.exists(onnx_file):
                # Fallback to model.onnx if quantized not found
                alt_onnx = os.path.join(target_path, "model.onnx")
                if os.path.exists(alt_onnx):
                    onnx_file = alt_onnx
                else:
                    logger.error(f"❌ ONNX model file not found in '{target_path}'.")
                    self.is_loaded = False
                    return

            logger.info(f"Loading XLM-RoBERTa Tokenizer from: {target_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(target_path)

            logger.info(f"Loading ONNX INT8 Engine from: {onnx_file}")
            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 4
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            self.session = ort.InferenceSession(
                onnx_file, 
                sess_options, 
                providers=["CPUExecutionProvider"]
            )

            # Warmup inference to eliminate initial cold-start latency
            dummy_tok = self.tokenizer("warmup test payload", return_tensors="np")
            dummy_inputs = {
                "input_ids": dummy_tok["input_ids"].astype(np.int64),
                "attention_mask": dummy_tok["attention_mask"].astype(np.int64)
            }
            self.session.run(None, dummy_inputs)

            self.is_loaded = True
            logger.info("✅ NeuralShield v5 XLM-RoBERTa ONNX INT8 Engine successfully initialized & warmed up.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ONNX model: {e}")
            self.is_loaded = False

    def predict(
        self,
        text: str,
        temperature: Optional[float] = None,
        sliding_window: Optional[bool] = None
    ) -> Dict[str, Any]:
        if not self.is_loaded or self.session is None or self.tokenizer is None:
            return self._fallback_predict(text)

        temp = temperature if temperature is not None else self.temperature
        sw_enabled = sliding_window if sliding_window is not None else self.sliding_window_enabled

        t_start = time.perf_counter()
        try:
            # 1. Uzun dokümanları kontrol etmek için 4096 tokene kadar tara
            tokens_full = self.tokenizer(
                text,
                truncation=True,
                max_length=4096,
                return_tensors="np"
            )
            input_ids = tokens_full["input_ids"][0]
            attention_mask = tokens_full["attention_mask"][0]
            total_tokens = int(len(input_ids))

            # 2. Standart metin boyutu (<= window_size) veya kayan pencere kapalıysa tek geçiş
            if total_tokens <= self.window_size or not sw_enabled:
                if total_tokens > self.window_size:
                    input_ids = input_ids[:self.window_size]
                    attention_mask = attention_mask[:self.window_size]

                inputs = {
                    "input_ids": np.expand_dims(input_ids, axis=0).astype(np.int64),
                    "attention_mask": np.expand_dims(attention_mask, axis=0).astype(np.int64)
                }
                outputs = self.session.run(None, inputs)
                logits = outputs[0][0]

                # Sıcaklık kalibrasyonu (Platt scaling)
                if temp > 0 and temp != 1.0:
                    logits = logits / temp

                exp_logits = np.exp(logits - np.max(logits))
                probs = exp_logits / np.sum(exp_logits)
                pred_idx = int(np.argmax(probs))
                latency_ms = (time.perf_counter() - t_start) * 1000.0

                return {
                    "ml_class": CLASS_NAMES[pred_idx],
                    "ml_class_idx": pred_idx,
                    "ml_probabilities": {
                        "Benign": float(probs[0]),
                        "Malicious": float(probs[1])
                    },
                    "ml_risk_score": int(round(probs[1] * 100)),
                    "inference_latency_ms": round(latency_ms, 2),
                    "translated_text": text,
                    "chunks_analyzed": 1,
                    "total_tokens": total_tokens,
                }

            # 3. Kayan Pencere (Sliding Window Chunking) — 512+ RAG/PDF Doküman Analizi
            bos_id = int(self.tokenizer.bos_token_id if self.tokenizer.bos_token_id is not None else 0)
            eos_id = int(self.tokenizer.eos_token_id if self.tokenizer.eos_token_id is not None else 2)
            content_ids = [int(t) for t in input_ids if t not in (bos_id, eos_id)]
            content_window = max(self.window_size - 2, 64)

            chunks = []
            start = 0
            while start < len(content_ids):
                end = min(start + content_window, len(content_ids))
                sub = content_ids[start:end]
                # RoBERTa sınıflandırma kafası için <s> ve </s> ile çerçeveleme şarttır
                chunk = [bos_id] + sub + [eos_id]
                chunks.append(np.array(chunk, dtype=np.int64))
                if end == len(content_ids):
                    break
                start += self.stride

            max_mal_prob = 0.0
            for chunk_ids in chunks:
                chunk_inputs = {
                    "input_ids": np.expand_dims(chunk_ids, axis=0),
                    "attention_mask": np.ones((1, len(chunk_ids)), dtype=np.int64)
                }
                outputs = self.session.run(None, chunk_inputs)
                logits = outputs[0][0]
                if temp > 0 and temp != 1.0:
                    logits = logits / temp
                exp_logits = np.exp(logits - np.max(logits))
                probs = exp_logits / np.sum(exp_logits)
                mal_prob = float(probs[1])
                if mal_prob > max_mal_prob:
                    max_mal_prob = mal_prob

            benign_prob = float(1.0 - max_mal_prob)
            pred_idx = 1 if max_mal_prob >= 0.50 else 0
            latency_ms = (time.perf_counter() - t_start) * 1000.0

            return {
                "ml_class": CLASS_NAMES[pred_idx],
                "ml_class_idx": pred_idx,
                "ml_probabilities": {
                    "Benign": benign_prob,
                    "Malicious": max_mal_prob
                },
                "ml_risk_score": int(round(max_mal_prob * 100)),
                "inference_latency_ms": round(latency_ms, 2),
                "translated_text": text,
                "chunks_analyzed": len(chunks),
                "total_tokens": total_tokens,
            }
        except Exception as e:
            logger.error(f"Inference execution error: {e}")
            return self._fallback_predict(text)

    def _fallback_predict(self, text: str) -> Dict[str, Any]:
        """Emergency fallback heuristic if model fails to execute."""
        t = text.lower()
        inj_keywords = [
            "ignore all rules", "override system", "jailbreak mode", 
            "dan mode", "forget instructions", "developer mode",
            "tüm kuralları unut", "sistem şifresi", "yetkileri geçersiz kıl"
        ]
        is_attack = any(kw in t for kw in inj_keywords)
        benign_prob = 0.05 if is_attack else 0.95
        mal_prob = 1.0 - benign_prob

        return {
            "ml_class": "Malicious" if is_attack else "Benign",
            "ml_class_idx": 1 if is_attack else 0,
            "ml_probabilities": {"Benign": benign_prob, "Malicious": mal_prob},
            "ml_risk_score": 95 if is_attack else 5,
            "inference_latency_ms": 0.5,
            "translated_text": text,
        }
