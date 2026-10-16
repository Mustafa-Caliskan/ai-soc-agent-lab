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
            "# 🛡️ CyberTech NeuralShield — Google Colab Çok Modelli Benchmark (v2.0)\n",
            "\n",
            "Bu Colab çalışma alanı; **TÜBİTAK / EVREN H200** altyapısında API üzerinden test edilen modellere ek olarak,\n",
            "Hugging Face ekosistemindeki açık ağırlıklı modelleri (**Trendyol-LLM-7B**, **Qwen-2.5-7B/72B**, **Llama-3.3-70B**, **DeepSeek-R1-Distill**, **Abliterated**)\n",
            "iki kanallı sızıntı protokolüyle (**True Egress ASR** ve **CoT Reasoning Leakage**) GPU üzerinde test etmek için tasarlanmıştır.\n",
            "\n",
            "### 🎯 Ölçülen Metrikler ve Özellikler:\n",
            "1. **Kalkan KAPALI — True Egress ASR (`content`):** Kullanıcı yanıtında kanarya sızıntı oranı (% + Wilson %95 GA)\n",
            "2. **Kalkan KAPALI — CoT Sızıntısı (`<think>`):** İçsel düşünme izinde kanarya sızıntı oranı (% + Wilson %95 GA)\n",
            "3. **Kalkan AÇIK — NeuralShield-v5:** Saldırının kapıda engellenme oranı ve sızıntının %0'a indirilmesi\n",
            "4. **Kesintiye Dayanıklı Kayıt (`Auto-Resume`):** Her örnek sonunda `data/colab_results/` altına kayıt alınır; oturum kopsa bile kaldığı yerden devam eder.\n"
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
            "# @title 3. Proje Deposunu Klonlama ve (İsteğe Bağlı) Google Drive Yedeklemesi\n",
            "import os\n",
            "MOUNT_GOOGLE_DRIVE = False #@param {type:\"boolean\"}\n",
            "if MOUNT_GOOGLE_DRIVE:\n",
            "    from google.colab import drive\n",
            "    drive.mount('/content/drive')\n",
            "\n",
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
            "# @title 4. Hedef Modeli Seçin ve Testi Başlatın (Colab A100 / T4 Uyumlu)\n",
            "# @markdown **Siklet 1 (Küçük 2B-3B)** | **Siklet 2 (Orta 7B-32B & Türkçe)** | **Sansürsüz (Abliterated)** | **Siklet 3 (Büyük 70B):**\n",
            "TARGET_MODEL = \"Trendyol/Trendyol-LLM-7b-chat-v1.0\" #@param [\"Trendyol/Trendyol-LLM-7b-chat-v1.0\", \"Qwen/Qwen2.5-7B-Instruct\", \"Qwen/Qwen2.5-3B-Instruct\", \"meta-llama/Llama-3.2-3B-Instruct\", \"google/gemma-2-2b-it\", \"microsoft/Phi-3.5-mini-instruct\", \"mistralai/Mistral-Nemo-Instruct-2407\", \"Qwen/Qwen2.5-14B-Instruct\", \"Qwen/Qwen2.5-32B-Instruct\", \"google/gemma-2-27b-it\", \"huihui-ai/Qwen2.5-14B-Instruct-abliterated\", \"failspy/Meta-Llama-3-8B-Instruct-abliterated-v3\", \"meta-llama/Llama-3.3-70B-Instruct\", \"Qwen/Qwen2.5-72B-Instruct\", \"deepseek-ai/DeepSeek-R1-Distill-Llama-70B\", \"deepseek-ai/DeepSeek-R1-Distill-Qwen-7B\"]\n",
            "DATASET_PATH = \"data/colab_e2e_suite_stratified.json\" #@param [\"data/colab_e2e_suite_stratified.json\", \"data/evren_unified_benchmark_25.json\", \"data/evren_benchmark_30_independent.json\"]\n",
            "HF_TOKEN = \"\" #@param {type:\"string\"}\n",
            "USE_4BIT = True #@param {type:\"boolean\"}\n",
            "\n",
            "cmd = f\"python scripts/colab/run_colab_benchmark.py --model {TARGET_MODEL} --dataset {DATASET_PATH}\"\n",
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
            "# @title 5. Sonuç Tablosunu Görüntüleyin, Grafiği Çizdirin ve JSON İndirin\n",
            "import os, json, glob, zipfile, matplotlib.pyplot as plt\n",
            "\n",
            "results_files = sorted(glob.glob('data/colab_results/colab_benchmark_*.json'), key=os.path.getmtime)\n",
            "if results_files:\n",
            "    latest = results_files[-1]\n",
            "    with open(latest, 'r', encoding='utf-8') as f:\n",
            "        data = json.load(f)\n",
            "\n",
            "    model_name = data.get('model', 'Hedef Model')\n",
            "    raw_asr = data.get('raw_asr_pct', 0.0)\n",
            "    cot_asr = data.get('raw_cot_leak_rate_pct', 0.0)\n",
            "    shield_asr = data.get('shield_asr_pct', 0.0)\n",
            "\n",
            "    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)\n",
            "    labels = ['Kalkan KAPALI\\n(True Egress ASR)', 'Kalkan KAPALI\\n(CoT Sızıntısı)', 'Kalkan AÇIK\\n(NeuralShield-v5)']\n",
            "    vals = [raw_asr, cot_asr, shield_asr]\n",
            "    colors = ['#e67e22', '#e74c3c', '#2ecc71']\n",
            "    bars = ax.bar(labels, vals, color=colors, width=0.48)\n",
            "    ax.set_ylabel('Sızıntı / Başarı Oranı (%)', fontsize=12)\n",
            "    ax.set_title(f'{model_name} — İki Kanallı Sızıntı ve Savunma Analizi', fontsize=13, fontweight='bold')\n",
            "    ax.set_ylim(0, 105)\n",
            "    for bar in bars:\n",
            "        yval = bar.get_height()\n",
            "        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f'%{yval:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')\n",
            "    plt.grid(axis='y', linestyle='--', alpha=0.5)\n",
            "    plt.tight_layout()\n",
            "    plt.savefig('data/colab_results/colab_benchmark_comparison.png')\n",
            "    plt.show()\n",
            "\n",
            "    # Tüm koşulan modelleri tek bir ZIP paketi olarak hazırla\n",
            "    zip_path = 'colab_all_results_bundle.zip'\n",
            "    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:\n",
            "        for rf in glob.glob('data/colab_results/*'):\n",
            "            zf.write(rf)\n",
            "    print(f'✅ Tüm sonuçlar paketlendi: {zip_path}')\n",
            "    try:\n",
            "        from google.colab import files\n",
            "        files.download(zip_path)\n",
            "    except Exception:\n",
            "        pass\n",
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
