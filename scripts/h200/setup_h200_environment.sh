#!/bin/bash
# ==============================================================================
# CyberTech NeuralShield - EVREN 8x H200 Supercomputer Setup Script
# ==============================================================================
set -e

echo "=============================================================================="
echo "🛡️  EVREN 8x NVIDIA H200 GPU SÜPER BİLGİSAYAR KÜMESİ HAZIRLANIYOR"
echo "=============================================================================="

# 1. GPU ve Sürücü Doğrulaması
echo "🔍 1. Donanım ve GPU Durumu Kontrol Ediliyor..."
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader
TOTAL_GPUS=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
echo "✅ Tespit Edilen GPU Sayısı: $TOTAL_GPUS adet H200"

if [ "$TOTAL_GPUS" -lt 8 ]; then
    echo "⚠️  Uyarı: 8'den az GPU tespit edildi ($TOTAL_GPUS adet). Tensor parallelism ayarlanacak."
fi

# 2. Python & PIP Güncellemesi
echo "📦 2. Python Bağımlılıkları ve vLLM Motoru Kuruluyor..."
python3 -m pip install --upgrade pip

# vLLM (H100/H200 FP8 ve PagedAttention için endüstri standardı yüksek verimli çıkarım motoru)
pip install -q \
    "vllm>=0.6.0" \
    "transformers>=4.45.0" \
    "accelerate>=0.34.0" \
    "onnxruntime>=1.18.0" \
    "fastapi>=0.110.0" \
    "uvicorn>=0.28.0" \
    "requests" \
    "pandas" \
    "numpy" \
    "scikit-learn" \
    "matplotlib" \
    "seaborn"

# 3. Ortam Değişkenleri ve Bellek Optimizasyonları
echo "⚡ 3. Süper Bilgisayar Ortam Değişkenleri Yapılandırılıyor..."
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export HF_HUB_ENABLE_HF_TRANSFER=1
export TOKENIZERS_PARALLELISM=false

# Hızlı NVMe disk alanı varsa HF önbelleğini oraya yönlendir
if [ -d "/scratch" ]; then
    export HF_HOME=/scratch/hf_cache
    mkdir -p /scratch/hf_cache
elif [ -d "/local" ]; then
    export HF_HOME=/local/hf_cache
    mkdir -p /local/hf_cache
fi

echo "=============================================================================="
echo "✅ EVREN 8x H200 ORTAMI BAŞARIYLA KURULDU VE KULLANIMA HAZIR!"
echo "👉 Sıradaki adım: bash launch_vllm_8x_h200.sh <model_adi>"
echo "=============================================================================="
