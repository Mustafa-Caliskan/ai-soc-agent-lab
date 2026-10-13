#!/bin/bash
# ==============================================================================
# CyberTech NeuralShield - vLLM 8-Way Tensor Parallel Launch Script
# Runs high-throughput bare-metal models on 8x NVIDIA H200 (1.1TB VRAM)
# ==============================================================================
set -e

MODEL_CHOICE=${1:-"llama70b"}
PORT=${2:-8000}

# Model Takma Adları ve Hugging Face Yolları
case $MODEL_CHOICE in
    llama70b)
        HF_MODEL="meta-llama/Llama-3.3-70B-Instruct"
        TP_SIZE=8
        MAX_LEN=8192
        ;;
    qwen72b)
        HF_MODEL="Qwen/Qwen2.5-72B-Instruct"
        TP_SIZE=8
        MAX_LEN=8192
        ;;
    deepseek70b)
        HF_MODEL="deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
        TP_SIZE=8
        MAX_LEN=8192
        ;;
    trendyol70b)
        HF_MODEL="Trendyol/Trendyol-LLM-70B-Instruct"
        TP_SIZE=8
        MAX_LEN=8192
        ;;
    turkish8b)
        HF_MODEL="Trendyol/Llama-3-Trendyol-LLM-8b-chat-v2.0"
        TP_SIZE=1
        MAX_LEN=4096
        ;;
    qwen7b)
        HF_MODEL="Qwen/Qwen2.5-7B-Instruct"
        TP_SIZE=1
        MAX_LEN=8192
        ;;
    *)
        HF_MODEL="$MODEL_CHOICE"
        TP_SIZE=8
        MAX_LEN=8192
        ;;
esac

echo "=============================================================================="
echo "🚀 vLLM MOTORU 8x H200 ÜZERİNDE BAŞLATILIYOR"
echo "  - Model             : $HF_MODEL"
echo "  - Tensor Parallelism: $TP_SIZE GPU"
echo "  - Port              : $PORT"
echo "  - Maksimum Bağlam   : $MAX_LEN token"
echo "  - Hassasiyet        : bfloat16 (Yerel H200 HBM3e)"
echo "=============================================================================="

# Arka planda vLLM OpenAI-Uyumlu Sunucusunu Başlat
python3 -m vllm.entrypoints.openai.api_server \
    --model "$HF_MODEL" \
    --tensor-parallel-size "$TP_SIZE" \
    --port "$PORT" \
    --host "0.0.0.0" \
    --max-model-len "$MAX_LEN" \
    --gpu-memory-utilization 0.92 \
    --dtype bfloat16 \
    --disable-log-requests &

SERVER_PID=$!
echo "Sunucu PID: $SERVER_PID. Model ağırlıkları 8x H200 GPU'ya dağıtılıyor..."

# Sağlık Kontrolü (Sunucunun hazır olmasını bekle)
echo "⏳ Sunucunun ayağa kalkması bekleniyor (yaklaşık 30-60 saniye)..."
READY=0
for i in {1..120}; do
    if curl -s "http://localhost:$PORT/v1/models" | grep -q "data"; then
        READY=1
        break
    fi
    sleep 2
    echo -n "."
done

echo ""
if [ $READY -eq 1 ]; then
    echo "=============================================================================="
    echo "✅ MODEL BAŞARIYLA AYAĞA KALKTI VE YANIT VERMEYE HAZIR!"
    echo "  - Uç Nokta: http://localhost:$PORT/v1/chat/completions"
    echo "👉 Testi başlatmak için: python run_h200_benchmark.py --model-name '$HF_MODEL' --port $PORT"
    echo "=============================================================================="
else
    echo "❌ Hata: Model belirtilen sürede yanıt vermedi. Logları kontrol edin."
    kill $SERVER_PID || true
    exit 1
fi
