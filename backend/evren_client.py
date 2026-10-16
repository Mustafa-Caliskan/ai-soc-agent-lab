"""
CyberTech Neural Shield - EVREN LLM API İstemcisi.

Bu modül, TÜBİTAK/SSYZ EVREN Platformu açık ağırlıklı model filosuna
(DeepSeek-v4.1-Flash, GLM-5.3, Qwen3-Guard-4B, Gemma-4-31B vb.)
OpenAI uyumlu REST uç noktası üzerinden erişim sağlar.

Özellikler:
  1. Kullanım şartlarını (terms) otomatik tespit ve onaylama (terms/accept).
  2. Günlük 15M ücretsiz token kotası sorgulama (/v1/quota).
  3. Düşünme (reasoning) ve içerik akışını eşzamanlı ayrıştırma.
  4. Qwen3-Guard-4B içerik güvenliği değerlendirmesi.
  5. Keep-alive SSE ve önbellek desteği.
"""
import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Generator
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = os.getenv("EVREN_BASE_URL", "https://evren-llmapi.ssyz.org.tr/v1")
DEFAULT_MODEL = os.getenv("EVREN_DEFAULT_MODEL", "deepseek-v4.1-flash")


class EvrenClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("EVREN_API_KEY", "").strip()
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.terms_accepted = False

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.startswith("evren_llm_"))

    def _headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def ensure_terms_accepted(self) -> bool:
        """Kullanım şartlarını kontrol eder ve onaylanmamışsa onaylar."""
        if not self.is_configured:
            return False
        if self.terms_accepted:
            return True

        url_status = f"{self.base_url}/terms/status"
        try:
            r = requests.get(url_status, headers=self._headers(), timeout=10)
            if r.status_code == 200:
                data = r.json()
                version = data.get("current_version", 1)
                accepted = data.get("accepted", False)
                if not accepted:
                    url_accept = f"{self.base_url}/terms/accept"
                    r_acc = requests.post(url_accept, headers=self._headers(), json={"version": version}, timeout=10)
                    if r_acc.status_code == 200:
                        logger.info("✅ EVREN kullanım şartları başarıyla onaylandı.")
                        self.terms_accepted = True
                        return True
                    else:
                        logger.warning(f"⚠️ EVREN şart onayı başarısız: HTTP {r_acc.status_code} - {r_acc.text}")
                        return False
                else:
                    self.terms_accepted = True
                    return True
            else:
                logger.warning(f"⚠️ EVREN şart durumu sorgulanamadı: HTTP {r.status_code}")
                # Fallback: version 1 kabul etmeyi dene
                requests.post(f"{self.base_url}/terms/accept", headers=self._headers(), json={"version": 1}, timeout=10)
                self.terms_accepted = True
                return True
        except Exception as e:
            logger.error(f"❌ EVREN şart kontrol hatası: {e}")
            return False

    def get_quota(self) -> Dict[str, Any]:
        """Kalan günlük kota ve sıfırlanma bilgilerini döndürür."""
        if not self.is_configured:
            return {"error": "API key ayarlanmamış"}
        try:
            r = requests.get(f"{self.base_url}/quota", headers=self._headers(), timeout=10)
            if r.status_code == 200:
                return r.json()
            return {
                "status_code": r.status_code,
                "remaining_tokens": r.headers.get("x-evren-daily-remaining-tokens", "Bilinmiyor"),
                "detail": r.text
            }
        except Exception as e:
            return {"error": str(e)}

    def list_models(self) -> List[str]:
        """Kullanılabilir model kimliklerini döndürür."""
        if not self.is_configured:
            return []
        try:
            r = requests.get(f"{self.base_url}/models", headers=self._headers(), timeout=10)
            if r.status_code == 200:
                data = r.json()
                return [m.get("id") if isinstance(m, dict) else str(m) for m in data.get("data", [])]
            return []
        except Exception as e:
            logger.error(f"❌ Model listeleme hatası: {e}")
            return []

    def generate_chat(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """Tek seferlik (non-streaming) sohbet tamamlama çağrısı."""
        self.ensure_terms_accepted()
        target_model = model or DEFAULT_MODEL

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": target_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "chat_template_kwargs": {"enable_thinking": False}
        }

        try:
            r = requests.post(f"{self.base_url}/chat/completions", headers=self._headers(), json=payload, timeout=60)
            if r.status_code == 200:
                data = r.json()
                choice = data["choices"][0]
                content = choice["message"].get("content", "")
                reasoning = choice["message"].get("reasoning", "") or choice["message"].get("reasoning_content", "")
                return {
                    "success": True,
                    "content": content,
                    "reasoning": reasoning,
                    "model": data.get("model", target_model),
                    "usage": data.get("usage", {}),
                    "remaining_daily_tokens": r.headers.get("x-evren-daily-remaining-tokens")
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {r.status_code}: {r.text}",
                    "status_code": r.status_code
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stream_chat(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.3
    ) -> Generator[Dict[str, Any], None, None]:
        """Akış (streaming SSE) sohbet tamamlama üreteci. (reasoning ve content parçacıklarını iletir)."""
        self.ensure_terms_accepted()
        target_model = model or DEFAULT_MODEL

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": target_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
            "stream_options": {"include_usage": True},
            "chat_template_kwargs": {"enable_thinking": False}
        }

        try:
            with requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
                stream=True,
                timeout=90
            ) as response:
                if response.status_code != 200:
                    yield {"type": "error", "error": f"HTTP {response.status_code}: {response.text}"}
                    return

                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    # Keep-alive sinyallerini atla (": keep-alive")
                    if line.startswith(":"):
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            choices = chunk.get("choices", [])
                            if not choices:
                                if "usage" in chunk:
                                    yield {"type": "usage", "usage": chunk["usage"]}
                                continue
                            delta = choices[0].get("delta", {})
                            reasoning = delta.get("reasoning") or delta.get("reasoning_content")
                            if reasoning:
                                yield {"type": "reasoning", "delta": reasoning}
                            content = delta.get("content")
                            if content:
                                yield {"type": "content", "delta": content}
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield {"type": "error", "error": str(e)}

    def evaluate_with_qwen_guard(self, text: str) -> Dict[str, Any]:
        """EVREN üzerindeki qwen3-guard-4b modelini kullanarak girdi güvenliğini test eder."""
        self.ensure_terms_accepted()
        payload = {
            "model": "qwen3-guard-4b",
            "messages": [
                {"role": "user", "content": text}
            ],
            "max_tokens": 512,
            "temperature": 0.0
        }
        try:
            r = requests.post(f"{self.base_url}/chat/completions", headers=self._headers(), json=payload, timeout=20)
            if r.status_code == 200:
                data = r.json()
                raw_reply = data["choices"][0]["message"].get("content", "").strip()
                is_safe = "safe" in raw_reply.lower() and "unsafe" not in raw_reply.lower()
                return {
                    "success": True,
                    "is_safe": is_safe,
                    "verdict": raw_reply,
                    "model": "qwen3-guard-4b",
                    "usage": data.get("usage", {})
                }
            return {"success": False, "error": f"HTTP {r.status_code}: {r.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
