# 🛡️ EVREN 8x NVIDIA H200 Süper Bilgisayar Canlı Benchmark Kılavuzu

Bu kılavuz, **EVREN Platformu** üzerinde rezerve edilen **8 adet NVIDIA H200 (1.1 TB VRAM)** süper bilgisayar kümesinde 4 saatlik test seansını sıfır zaman kaybıyla en yüksek akademik verimle tamamlamak için hazırlanmıştır.

---

## 📋 1. Adım: SSH ile Bağlantı ve Projenin İndirilmesi

Süper bilgisayara bağlandığınızda ilk olarak çalışma dizinini hazırlayın:

```bash
# 1. Proje dizinine geçin veya klonlayın
git clone <PROJE_REPO_URL> neuralshield_h200
cd neuralshield_h200

# 2. Kurulum betiğini çalıştırın (vLLM, PyTorch, H200 optimizasyonları)
bash scripts/h200/setup_h200_environment.sh
```

---

## 🚀 2. Adım: Öncelikli 3 Modelin 8 GPU'da Paralel Test Planı (16:00 - 20:00)

4 saatlik sürede her bir amiral modeli sırayla ayağa kaldırıp testlerini tamamlayacağız:

### 1. Model (16:00 - 17:00): Llama-3.3-70B (Küresel Baz Kontrol Modeli)
* **Stratejik Önemi:** Kurumsal RAG sistemlerinin küresel standardı. Güvenlik duvarı kapalıyken bile en dirençli baz kontrol modelidir.
```bash
# Modeli Başlat
bash scripts/h200/launch_vllm_8x_h200.sh llama70b 8000

# Benchmark'ı Koştur
python scripts/h200/run_h200_benchmark.py --base-url "http://localhost:8000/v1" --model-name "meta-llama/Llama-3.3-70B-Instruct" --output-dir "./h200_results/llama70b"
```

### 2. Model (17:00 - 18:00): DeepSeek-R1-Distill-Llama-70B (Akıl Yürütme & Ajan Beyni)
* **Stratejik Önemi:** SQL ile veritabanına bağlanan otonom ajanların beyni. Düşünme/muhakeme (Chain-of-Thought) sürecinde karmaşık jailbreak'leri nasıl işlediğini kanıtlar.
```bash
# Modeli Başlat
bash scripts/h200/launch_vllm_8x_h200.sh deepseek70b 8000

# Benchmark'ı Koştur
python scripts/h200/run_h200_benchmark.py --base-url "http://localhost:8000/v1" --model-name "deepseek-ai/DeepSeek-R1-Distill-Llama-70B" --output-dir "./h200_results/deepseek70b"
```

### 3. Model (18:00 - 19:00): Trendyol-LLM-70B-Instruct (Türkçe Yerel Egemenlik Modeli)
* **Stratejik Önemi:** Türkiye'deki bankacılık, e-ticaret ve kamu destek botlarında veri egemenliği için tercih edilen yerel model. Türkçe siber saldırı kombinasyonlarındaki zafiyetini ve NeuralShield'in kurtarıcı etkisini kanıtlar.
```bash
# Modeli Başlat
bash scripts/h200/launch_vllm_8x_h200.sh trendyol70b 8000

# Benchmark'ı Koştur
python scripts/h200/run_h200_benchmark.py --base-url "http://localhost:8000/v1" --model-name "Trendyol/Trendyol-LLM-70B-Instruct" --output-dir "./h200_results/trendyol70b"
```

### 4. Kapanış & Tünel Analizi (19:00 - 20:00)
Son saatte tüm loglar, grafikler ve CSV dosyaları kontrol edilip kendi bilgisayarınıza aktarılır.


---

## ⚡ 3. Adım: Otomatik Benchmark'ı Başlatma (Kalkan AÇIK vs. KALI)

Model ayağa kalktığında tek bir komutla hem **Kalkan KAPALI (Raw ASR)** hem de **NeuralShield-v4 AÇIK** testlerini koşturun:

```bash
# Yerel vLLM Uç Noktasını Test Et
python scripts/h200/run_h200_benchmark.py \
    --base-url "http://localhost:8000/v1" \
    --model-name "meta-llama/Llama-3.3-70B-Instruct" \
    --output-dir "./h200_results"
```

Eğer doğrudan **EVREN Platformunun Kendi API'sini** test etmek isterseniz:
```bash
python scripts/h200/run_h200_benchmark.py \
    --base-url "https://evren-llmapi.ssyz.org.tr/v1" \
    --api-key "evren_llm_BURAYA_ANAHTARINIZ" \
    --model-name "deepseek-v4.1-flash" \
    --output-dir "./h200_results_evren"
```

---

## 🌐 4. Adım: Kendi Bilgisayarınızdan Web Arayüzüyle Canlı Test (SSH Tüneli)

Kendi dizüstü/masaüstü bilgisayarınızın terminalinde şu tüneli açarsanız:

```bash
ssh -L 8000:localhost:8000 <KULLANICI_ADI>@<EVREN_H200_IP>
```

Kendi tarayıcınızdan `http://localhost:8000/red` adresine girdiğinizde, **CyberTech Red Team Konsolu** doğrudan Ankara'daki 8x H200 kümesinde çalışan 70B'lik modele bağlanır!
* Canlı saldırı preseti seçip gönderebilir,
* Kalkanı açıp/kapatıp sızıntıyı anlık CRT ekranda izleyebilirsiniz.

---

## 📊 5. Adım: Sonuçları Alma ve Makaleye Aktarma

Test tamamlandığında `./h200_results/` klasöründe iki altın çıktı oluşur:
1. **`summary_table.md`**: Makalenin "Empirical Results" bölümüne doğrudan kopyalayabileceğiniz Wilson %95 güven aralıklı Markdown tablosu.
2. **`benchmark_TIMESTAMP.json`**: Hakemlerin incelemesi için ham sızıntı logları ve gecikme metrikleri.

Bu iki dosyayı kendi bilgisayarınıza kopyalayıp çıktığınızda, 4 saatlik randevu akademik olarak **%100 başarıyla tamamlanmış olur!**
