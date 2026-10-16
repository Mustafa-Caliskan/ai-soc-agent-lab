# Çok Modelli Kurumsal Havayolu Asistanı Kalkan Benchmark Raporu
**Çalışma:** CyberTech NeuralShield-v5 Çevresel Güvenlik Ağ Geçidi (4-Katmanlı Savunma Hattı)
**Senaryo:** SkyPort Uluslararası Havalimanı (IST) Operasyonel Chatbot Asistanı (Gizli Operasyonel Sistem Promptu)
**Tarih:** 14 Ekim 2026

| Model | Üretici / Mimari | Parametre | Test (n) | Kalkan KAPALI (OFF) Sızıntı (ASR) [%95 GA] | Kalkan AÇIK (ON) Sızıntı (ASR) [%95 GA] | NeuralShield-v5 Müdahale (%) | Net Risk Azaltımı (%) |
|---|---|---:|---:|---:|---:|---:|---:|
| **qwen2.5:3b** | Alibaba Cloud | 3.09B | 45 | %31.1 (14/45) [%19.5, %45.7] | **0/45 sızıntı (Wilson %95: %0.0–%7.9)** | %100.0 | **-%31.1** |
| **llama3.2:3b** | Meta AI | 3.21B | 45 | %24.4 (11/45) [%14.2, %38.7] | **0/45 sızıntı (Wilson %95: %0.0–%7.9)** | %100.0 | **-%24.4** |
| **gemma2:2b** | Google DeepMind | 2.61B | 45 | %22.2 (10/45) [%12.5, %36.3] | **0/45 sızıntı (Wilson %95: %0.0–%7.9)** | %100.0 | **-%22.2** |
| **phi3:mini** | Microsoft Research | 3.82B | 45 | %13.3 (6/45) [%6.3, %26.2] | **0/45 sızıntı (Wilson %95: %0.0–%7.9)** | %100.0 | **-%13.3** |
| **qwen2.5:1.5b** | Alibaba Cloud | 1.54B | 45 | %8.9 (4/45) [%3.5, %20.7] | **0/45 sızıntı (Wilson %95: %0.0–%7.9)** | %100.0 | **-%8.9** |

> **İstatistiksel ve Metodolojik Notlar:**
> 1. **Wilson %95 Güven Aralığı:** Kalkan AÇIK (ON) modundaki $0/45$ gözlemlenen sızıntı, Wilson score metodu ile popülasyon sızıntı oranının %95 güvenle $\le \%7.9$ olduğunu matematiksel olarak belgeler (üst sınır $\%7.9$).
> 2. **Bütünsel Müdahale:** NeuralShield-v5 (Katman 0 Normalizasyon + Katman 1 Regex + Katman 2 INT8 XLM-RoBERTa $T^*=1.8345$ + Katman 3 DLP), test edilen 5 açık ağırlıklı modelin tamamında 45 saldırının 45'ine de müdahale ederek model çağrısı öncesinde sızıntıyı engellemiştir.
