import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent.parent
nb_path = ROOT / "notebooks" / "CyberTech_Colab_LLM_Benchmark.ipynb"

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 🛡️ CyberTech NeuralShield — Google Colab Çok Modelli Benchmark\n",
            "\n",
            "Bu Colab çalışma alanı; **TÜBİTAK / EVREN H200** altyapısında API üzerinden test edilen modellere ek olarak,\n",
            "Hugging Face ekosistemindeki açık ağırlıklı amiral gemisi modelleri (**Llama-3.3-70B**, **Qwen-2.5-72B**, **Trendyol-LLM**, **Mistral-7B**)\n",
            "aynı kademeli saldırı havuzuyla (Tier 1 - Tier 5) GPU üzerinde test etmek için tasarlanmıştır.\n",
            "\n",
            "### 🎯 Değerlendirme Modları:\n",
            "1. **Kalkan KAPALI (Shield OFF):** Çıplak modelin kanarya sızıntı oranı (Attack Success Rate - ASR %)\n",
            "2. **Kalkan AÇIK (Shield ON):** CyberTech NeuralShield-v5 (ONNX INT8 ~12ms) devredeyken saldırının kapıda engellenmesi\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# @title 1. GPU ve Donanım Kontrolü\n",
            "!nvidia-smi\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# @title 2. Gerekli Kütüphanelerin Yüklenmesi\n",
            "!pip install -q transformers accelerate bitsandbytes onnxruntime torch python-dotenv\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# @title 3. Proje Deposunu Klonlama veya Güncelleme\n",
            "import os\n",
            "if not os.path.exists('ai-soc-agent-lab'):\n",
            "    !git clone https://github.com/Mustafa-Caliskan/ai-soc-agent-lab.git\n",
            "%cd ai-soc-agent-lab\n",
            "!git pull\n",
            "import sys\n",
            "sys.path.insert(0, os.path.abspath('backend'))\n",
            "print('✅ Çalışma dizini:', os.getcwd())\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# @title 4. Hedef Modeli Seçin ve Testi Başlatın\n",
            "# @markdown Açık ağırlıklı modeli seçin:\n",
            "TARGET_MODEL = \"Qwen/Qwen2.5-7B-Instruct\" #@param [\"Qwen/Qwen2.5-7B-Instruct\", \"meta-llama/Llama-3.3-70B-Instruct\", \"Trendyol/Trendyol-LLM-7b-chat-v1.0\", \"mistralai/Mistral-7B-Instruct-v0.3\"]\n",
            "HF_TOKEN = \"\" #@param {type:\"string\"}\n",
            "USE_4BIT = True #@param {type:\"boolean\"}\n",
            "\n",
            "cmd = f\"python scripts/colab/run_colab_benchmark.py --model {TARGET_MODEL}\"\n",
            "if USE_4BIT:\n",
            "    cmd += \" --load-in-4bit\"\n",
            "if HF_TOKEN:\n",
            "    cmd += f\" --hf-token {HF_TOKEN}\"\n",
            "\n",
            "print(f\"🚀 Benchmark Başlatılıyor: {cmd}\")\n",
            "!{cmd}\n"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# @title 5. Çıktı Grafiğini Çizdirin (Kalkan KAPALI vs AÇIK ASR %)\n",
            "import json, glob, matplotlib.pyplot as plt\n",
            "\n",
            "results_files = glob.glob('data/colab_benchmark_*.json')\n",
            "if results_files:\n",
            "    latest = max(results_files, key=os.path.getctime)\n",
            "    with open(latest, 'r', encoding='utf-8') as f:\n",
            "        data = json.load(f)\n",
            "    \n",
            "    model_name = data.get('model', 'Hedef Model')\n",
            "    raw_asr = data.get('raw_asr_pct', 0)\n",
            "    shield_asr = data.get('shield_asr_pct', 0)\n",
            "    block_rate = data.get('block_rate_pct', 0)\n",
            "    \n",
            "    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)\n",
            "    bars = ax.bar(['Kalkan KAPALI (Raw LLM)', 'Kalkan AÇIK (NeuralShield)'], [raw_asr, shield_asr], color=['#e74c3c', '#2ecc71'], width=0.5)\n",
            "    ax.set_ylabel('Saldırı Başarı Oranı (ASR %)', fontsize=12)\n",
            "    ax.set_title(f'{model_name} - Hacklenme Riski Karşılaştırması', fontsize=14, fontweight='bold')\n",
            "    ax.set_ylim(0, 100)\n",
            "    for bar in bars:\n",
            "        yval = bar.get_height()\n",
            "        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f'%{yval:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')\n",
            "    plt.grid(axis='y', linestyle='--', alpha=0.5)\n",
            "    plt.tight_layout()\n",
            "    plt.savefig('colab_benchmark_comparison.png')\n",
            "    plt.show()\n",
            "    print('✅ Grafik kaydedildi: colab_benchmark_comparison.png')\n",
            "else:\n",
            "    print('⚠️ Henüz tamamlanmış benchmark verisi bulunamadı.')\n"
        ]
    }
]

notebook = {
    "cells": cells,
    "metadata": {
        "accelerator": "GPU",
        "colab": {
            "name": "CyberTech_Colab_LLM_Benchmark.ipynb",
            "provenance": []
        },
        "kernelspec": {
            "display_name": "Python 3",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print(f"✅ Colab Notebook oluşturuldu: {nb_path}")
