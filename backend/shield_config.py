"""
CyberTech Neural Shield - Merkezi Konfigürasyon Yükleyici.

Eşik değerleri, bileşik risk formülü ağırlıkları ve DLP/ban-politikası
parametreleri artık kod içine gömülü değil, `shield_config.json`
dosyasından okunur. Ortam değişkenleri (env var) dosya değerlerini
override edebilir (örn. CI/CD veya farklı dağıtım ortamlarında).

Kullanım:
    from shield_config import CONFIG
    threshold = CONFIG["block_threshold"]

Not: `reload_config()` test ortamlarında config'i yeniden okumak için kullanılır.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict

_CONFIG_PATH = Path(__file__).parent / "shield_config.json"

_DEFAULTS: Dict[str, Any] = {
    "block_threshold": 60,
    "suspect_threshold": 40,
    "weight_ml": 0.70,
    "weight_regex": 0.20,
    "weight_stego": 0.10,
    "hard_block_stego_score": 85,
    "hard_block_regex_and_ml_score": 90,
    "regex_only_floor_score": 65,
    "mask_generic_emails": False,
    "mask_generic_phones": False,
    "ban_window_seconds": 120,
    "ban_penalty_per_violation": 20,
    "ban_max_penalty": 40,
    "ban_min_effective_threshold": 20,
}

# Ortam değişkeni ön eki: SHIELD_BLOCK_THRESHOLD=55 gibi.
_ENV_PREFIX = "SHIELD_"


def _coerce(raw: str, reference: Any) -> Any:
    """Env var string değerini referans tipe (bool/int/float) çevirir."""
    if isinstance(reference, bool):
        return raw.strip().lower() in ("1", "true", "yes", "on")
    if isinstance(reference, int):
        try:
            return int(raw)
        except ValueError:
            return reference
    if isinstance(reference, float):
        try:
            return float(raw)
        except ValueError:
            return reference
    return raw


def _load() -> Dict[str, Any]:
    cfg = dict(_DEFAULTS)
    if _CONFIG_PATH.exists():
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                file_cfg = json.load(f)
            for k, v in file_cfg.items():
                if k in cfg:
                    cfg[k] = v
        except Exception:
            # Bozuk config dosyası durumunda güvenli varsayılanlara düş.
            pass

    for key in cfg:
        env_key = _ENV_PREFIX + key.upper()
        if env_key in os.environ:
            cfg[key] = _coerce(os.environ[env_key], cfg[key])

    return cfg


CONFIG: Dict[str, Any] = _load()


def reload_config() -> Dict[str, Any]:
    """Config'i diskten/ortamdan yeniden okur (testler ve admin panel için)."""
    global CONFIG
    CONFIG = _load()
    return CONFIG
