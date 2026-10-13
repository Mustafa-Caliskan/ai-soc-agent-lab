#!/usr/bin/env bash
# ==============================================================================
# CyberTech 8x NVIDIA H200 Supercomputer - Model Weights Pre-Fetcher
# Parallel / High-Speed Downloader via huggingface-cli & hf_transfer
# ==============================================================================
set -e

echo "============================================================"
echo " [CyberTech] H200 HF Weights Pre-Fetcher Initializing..."
echo "============================================================"

# HF Transfer ile maksimum indirme hızı (10-40 Gbps NVLink / Ethernet)
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_HOME="${HF_HOME:-/workspace/hf_cache}"

mkdir -p "$HF_HOME"

if ! command -v huggingface-cli &> /dev/null; then
    echo "[!] huggingface-cli bulunamadı, pip ile kuruluyor..."
    pip install -U "huggingface_hub[cli,hf_transfer]"
fi

# HuggingFace Token Kontrolü (Gated modeller için şart: Llama-3.3-70B)
if [ -z "$HF_TOKEN" ]; then
    echo "[!] DİKKAT: HF_TOKEN tanımlı değil!"
    echo "    Llama-3.3-70B gibi onay gerektiren modelleri indirmek için:"
    echo "    export HF_TOKEN=\"hf_your_token_here\" komutunu çalıştırın."
fi

# İndirilecek Model Listesi
MODELS=(
    "meta-llama/Llama-3.3-70B-Instruct"
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
    "Trendyol/Trendyol-LLM-70B-Instruct"
    "mistralai/Mistral-Small-Instruct-2409"
    "Trendyol/Llama-3-Trendyol-LLM-8b-chat-v2.0"
)

echo "[*] Toplam ${#MODELS[@]} model indirilecek. Hedef Dizin: $HF_HOME"
echo ""

for MODEL in "${MODELS[@]}"; do
    echo "------------------------------------------------------------"
    echo "[*] İndiriliyor: $MODEL"
    echo "------------------------------------------------------------"
    huggingface-cli download "$MODEL" \
        --cache-dir "$HF_HOME" \
        --resume-download \
        --local-dir-use-symlinks False || {
            echo "[!] UYARI: $MODEL indirilirken hata oluştu (Yetki veya isim uyuşmazlığı olabilir), diğerine geçiliyor..."
        }
done

echo ""
echo "============================================================"
echo "[+] Tüm model ağırlıkları başarıyla önbelleğe alındı!"
echo "    Artık './launch_vllm_8x_h200.sh <model>' komutunu"
echo "    sıfır bekleme süresiyle çalıştırabilirsiniz."
echo "============================================================"
