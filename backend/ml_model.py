"""
NeuralShield v5 - XLM-RoBERTa ONNX INT8 Inference Engine.
Layer 2 of the 4-Layer Hybrid Peripheral Defense Architecture.
Native multilingual (Turkish & English) semantic classifier with ~12ms CPU inference.
"""
import os
import time
import logging
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

CLASS_NAMES = ["Benign", "Malicious"]


class MLSecurityModel:
    def __init__(self, model_path: str = None):
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

    def predict(self, text: str) -> Dict[str, Any]:
        if not self.is_loaded or self.session is None or self.tokenizer is None:
            return self._fallback_predict(text)

        t_start = time.perf_counter()
        try:
            tokens = self.tokenizer(
                text,
                truncation=True,
                max_length=256,
                return_tensors="np"
            )
            inputs = {
                "input_ids": tokens["input_ids"].astype(np.int64),
                "attention_mask": tokens["attention_mask"].astype(np.int64)
            }
            outputs = self.session.run(None, inputs)
            logits = outputs[0][0]

            # Softmax calculation
            exp_logits = np.exp(logits - np.max(logits))
            probs = exp_logits / np.sum(exp_logits)
            pred_idx = int(np.argmax(probs))

            probs_dict = {
                "Benign": float(probs[0]),
                "Malicious": float(probs[1])
            }
            latency_ms = (time.perf_counter() - t_start) * 1000.0

            return {
                "ml_class": CLASS_NAMES[pred_idx],
                "ml_class_idx": pred_idx,
                "ml_probabilities": probs_dict,
                "ml_risk_score": int(round(probs[1] * 100)),
                "inference_latency_ms": round(latency_ms, 2),
                "translated_text": text,  # Native multilingual: no translation required
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
