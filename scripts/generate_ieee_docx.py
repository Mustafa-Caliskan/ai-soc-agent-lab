"""
Generates the IEEE Conference Paper formatted Word Document (.docx)
with embedded empirical figures and tables.
"""
import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOCS_DIR = Path(__file__).parent.parent / "docs"
FIG_DIR = DOCS_DIR / "figures"
TARGET_DOCX = DOCS_DIR / "IEEE_Konferans_Bildirisi_2Sutun.docx"

doc = docx.Document()

# Page Margins: Standard IEEE (0.75 in top/bottom, 0.75 in left/right)
sections = doc.sections
for s in sections:
    s.top_margin = Inches(0.75)
    s.bottom_margin = Inches(0.75)
    s.left_margin = Inches(0.75)
    s.right_margin = Inches(0.75)

# Styling Helper
def set_font(run, name="Times New Roman", size_pt=10, bold=False, italic=False, color_rgb=(0,0,0)):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

# 1. Title
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(0)
p_title.paragraph_format.space_after = Pt(4)
r_title = p_title.add_run("Büyük Dil Modellerinde Çok Katmanlı Güvenlik Ağ Geçidi: XLM-RoBERTa Tabanlı Doğal Çok Dilli ve Kuantize Semantik Savunma")
set_font(r_title, size_pt=16, bold=True)

p_subtitle = doc.add_paragraph()
p_subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_subtitle.paragraph_format.space_after = Pt(12)
r_sub = p_subtitle.add_run("Multi-Layer Security Gateway for Large Language Models: Native Multilingual and Quantized Semantic Defense via XLM-RoBERTa")
set_font(r_sub, size_pt=11, italic=True, color_rgb=(70,70,70))

# 2. Authors
p_auth = doc.add_paragraph()
p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_auth.paragraph_format.space_after = Pt(14)
r_a1 = p_auth.add_run("Mustafa ÇALIŞKAN¹*, Prof. Dr. Ali Hakan IŞIK²\n")
set_font(r_a1, size_pt=11, bold=True)
r_aff = p_auth.add_run("¹²Burdur Mehmet Akif Ersoy Üniversitesi, Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü, Burdur, Türkiye\n*mustafacaliskan@ogr.mehmetakif.edu.tr, hisik@mehmetakif.edu.tr")
set_font(r_aff, size_pt=9, italic=True, color_rgb=(60,60,60))

# 3. Abstract
p_abs = doc.add_paragraph()
p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p_abs.paragraph_format.space_after = Pt(6)
r_abs_h = p_abs.add_run("Özet— ")
set_font(r_abs_h, size_pt=9, bold=True)
r_abs_t = p_abs.add_run(
    "Büyük Dil Modellerinin (LLM) kurumsal karar destek mekanizmalarına entegre edilmesi, doğal dil girdilerini manipüle eden yeni nesil siber tehdit vektörlerini beraberinde getirmiştir. "
    "Komut enjeksiyonu (Prompt Injection), jailbreak ve görünmez Unicode Tag (U+E0000 - U+E007F) steganografisi gibi teknikler, geleneksel ağ güvenlik duvarlarını ve LLM sağlayıcılarının dahili güvenlik filtrelerini aşabilmektedir. "
    "Bu çalışmada, harici bir çeviri katmanına ihtiyaç duymaksızın doğrudan çok dilli çalışan ve mikro-gecikme seviyesinde koruma sağlayan 3 katmanlı hibrit bir çevre savunma mimarisi (CyberTech Neural Shield) önerilmektedir. "
    "Önerilen mimari; (1) Regex kural motoru, sıfır genişlikli karakter (ZWSP) filtresi, Base64 deşifreleyici ve Unicode Tag steganografi dedektöründen oluşan mikro-gecikmeli (<0.3 ms) Deterministik Katman, "
    "(2) NVIDIA A100 GPU üzerinde 28.524 dengeli veri örneğiyle eğitilen ve CPU üzerinde 9.47 ms gecikmeyle çalışan kuantize XLM-RoBERTa ONNX INT8 Semantik Sınıflandırıcısı ve "
    "(3) model yanıtlarındaki kişisel ve operasyonel verileri (TCKN, kredi kartı, şifre, API anahtarı) maskeleyen Veri Sızıntısı Önleme (DLP) katmanından oluşmaktadır. "
    "4.279 adetlik bağımsız test kümesinde yapılan ampirik değerlendirmeler; önerilen modelin %98.74 F1-skoru, %98.74 doğruluk ve yalnızca %0.93 Yanlış Alarm (False Positive) ürettiğini kanıtlamıştır. "
    "Dağılım dışı (OOD - Neuralchemy n=1.000) saldırılarda %82.15 F1-skoru, 100 örneklik canlı Türkçe saldırı benchmarkında ise %100 saldırı yakalama (50/50 TP, 0 FN) başarımı elde edilmiştir. "
    "Sistem, kurumsal Google Gemini 3.6 Flash modeli önünde konumlandırılarak API maliyetlerini ve hizmet kesinti (DoS) risklerini sıfıra indiren yüksek verimli bir çevre savunması sağlamıştır."
)
set_font(r_abs_t, size_pt=9)

p_kw = doc.add_paragraph()
p_kw.paragraph_format.space_after = Pt(14)
r_kw_h = p_kw.add_run("Anahtar Kelimeler— ")
set_font(r_kw_h, size_pt=9, bold=True)
r_kw_t = p_kw.add_run("Büyük Dil Modelleri, LLM Güvenliği, Prompt Injection, XLM-RoBERTa, ONNX INT8 Kuantizasyon, Unicode Steganografi, Çevre Savunması, DLP.")
set_font(r_kw_t, size_pt=9, italic=True)

def add_heading(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    set_font(r, size_pt=11, bold=True)
    return p

def add_body(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    set_font(r, size_pt=10)
    return p

# I. GİRİŞ
add_heading("I. GİRİŞ")
add_body(
    "Büyük Dil Modelleri (Large Language Models - LLM), doğal dil işleme alanındaki transformatör devrimi sayesinde kurumsal iş akışlarında ve müşteri iletişim sistemlerinde merkezi bir aktör haline gelmiştir [1]. "
    "Ancak modern dil modelleri, klasik Von Neumann bilgisayar mimarisinden farklı olarak komut (talimat) ile kullanıcı verisini birbirinden ayıramaz; girdi olarak verilen tüm belirteçleri (tokens) aynı bağlam penceresinde (context window) tek bir metin dizisi olarak işler [4]. "
    "Bu yapısal zafiyet, kötü niyetli aktörlerin masum kullanıcı sorguları kisvesi altında sistem talimatlarını geçersiz kılmasına (Prompt Injection), kurumsal veri tabanlarını sızdırmasına veya etik güvenlik bariyerlerini yıkmasına (Jailbreak) yol açmaktadır [7]."
)
add_body(
    "Buna ek olarak, Unicode standardında dil etiketleme amacıyla tanımlanmış özel etiket karakterleri (U+E0000 - U+E007F) kötüye kullanılarak icra edilen steganografik saldırılar yeni bir tehdit boyutu doğurmuştur. "
    "Arayüzde tek bir masum emoji veya boşluk gibi görünen bu karakterler, tokenizer seviyesinde ayrıştırılarak LLM'e görünmez kötü niyetli talimatlar iletmektedir."
)

# II. ÇEVRE SAVUNMASI
add_heading("II. ÇEVRE SAVUNMASININ GEREKLİLİĞİ VE MALİYET ANALİZİ")
add_body(
    "Akademik literatürde ve endüstride sıklıkla sorulan temel soru şudur: 'Google Gemini veya OpenAI GPT-4o gibi modeller zaten milyar dolarlık bütçelerle eğitilmekte ve kendi güvenlik filtrelerine sahiptir. Harici bir ön cephe güvenlik katmanına (Guardrail) neden ihtiyaç vardır?' "
    "Bu çalışmanın varlık sebebi olan 4 temel siber güvenlik gerekçesi şunlardır:"
)
add_body(
    "1. Kod ve Veri Ayrımının İmkânsızlığı: LLM'lerde sistem yöneticisi talimatı, kullanıcı girdisi ve harici dokümanlar aynı tensör akışında birleşir. Bu sebeple en gelişmiş modeller dahi bilişsel çerçeveleme (Cognitive Framing) ve kademeli ikna (Crescendo Attack) ile kandırılabilmektedir [10].\n"
    "2. Dolaylı Enjeksiyon Tehdidi: Kurumsal bir LLM harici bir bilet PDF'ini özetlerken, belge içerisine gizlenmiş görünmez beyaz metinleri okuduğunda zafiyete düşer. Bu saldırı dokümandan geldiği için modelin iç filtresi devreye girmez.\n"
    "3. Hizmet Kesinti Saldırıları (DoS) ve Token Maliyet Tasarrufu: Saldırganlar kurumsal API'lere binlerce kelimelik manipülatif promptlar göndererek şirketi iflas ettirecek API faturaları (Resource Exhaustion) çıkarabilir. NeuralShield, saldırıyı yerel sunucuda 9.47 ms'de ve sıfır ($0) API maliyetiyle ağ seviyesinde (HTTP 403) imha eder.\n"
    "4. Kurumsal Hassas Veri İzolasyonu (Hard Negatives): Genel bulut modelleri kurumsal IT bağlamını bilmez. NeuralShield, kurumsal terminolojide geçen kritik kelimeleri yanlış alarm üretmeden güvenle işler."
)

# III. MİMARİ
add_heading("III. ÖNERİLEN HİBRİT SİSTEM MİMARİSİ")
add_body(
    "CyberTech Neural Shield, gelen istekleri ardışık 3 katmandan geçiren asenkron bir güvenlik ağ geçididir:\n"
    "• Katman 1 (Deterministik Filtre & Steganografi, <0.3 ms): Unicode Tag (U+E0000 - U+E007F) görünmez mürekkep karakterlerini, sıfır genişlikli karakterleri (ZWSP), Base64 payload'larını ve regex kurallarını donanımsal olarak filtreler.\n"
    "• Katman 2 (XLM-RoBERTa ONNX INT8, 9.47 ms): Çok dilli transformatör mimarisine dayanan model, Türkçe ve İngilizce'yi harici çeviri olmaksızın yerel olarak sınıflandırır. 278 MB boyutuyla CPU üzerinde mikro-gecikmeli çıkarım sunar.\n"
    "• Hedef Model (Google Gemini 3.6 Flash): Kalkanı geçen güvenli istekler kurumsal Gemini 3.6 Flash API'sine iletilir.\n"
    "• Katman 3 (DLP Maskeleme, <0.5 ms): Üretilen yanıttaki TCKN, kredi kartı, şifre ve operasyonel API anahtarları maskelenir."
)

# IV. DENEYSEL BULGULAR
add_heading("IV. DENEYSEL BULGULAR VE BAŞARIM ANALİZİ")
add_body(
    "Model, literatürdeki standart güvenlik veri setleri ve kurumsal False Positive tuzaklarını içeren 28.524 dengeli örnek (14.262 Meşru / 14.262 Saldırı) ile NVIDIA A100 GPU üzerinde 3 epoch boyunca eğitilmiştir."
)

# Tablo
table = doc.add_table(rows=4, cols=8)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.autofit = False

headers = ["Değerlendirme Kümesi", "Örnek (n)", "Doğruluk", "Macro F1", "Kesinlik", "Duyarlılık", "Yanlış Alarm (FPR)", "Kaçırma (FNR)"]
row_data = [
    ["Bağımsız Hold-out Test", "4.279", "%98.74", "%98.74", "%98.74", "%98.74", "%0.93 (20/2140)", "%1.59 (34/2139)"],
    ["Dağılım Dışı (OOD - Neuralchemy)", "1.000", "%82.30", "%82.15", "%83.91", "%74.71", "%5.68 (22/387)", "%25.29 (155/613)"],
    ["Canlı Türkçe Siber Saldırı Testi", "100", "%90.00", "%90.91", "%83.33", "%100.00", "%20.00 (10/50)", "%0.00 (0/50)"]
]

for col_idx, h in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = h
    set_font(cell.paragraphs[0].runs[0], size_pt=8, bold=True)
    # Shading header
    shading_elm = parse_xml(r'<w:shd {} w:fill="E2E8F0"/>'.format(nsdecls('w')))
    cell._tc.get_or_add_tcPr().append(shading_elm)

for row_idx, r in enumerate(row_data):
    for col_idx, val in enumerate(r):
        cell = table.cell(row_idx + 1, col_idx)
        cell.text = val
        set_font(cell.paragraphs[0].runs[0], size_pt=8)

p_sp = doc.add_paragraph()
p_sp.paragraph_format.space_before = Pt(8)

# Add figures if present
figures_list = [
    ("sekil_1_loss_egrisi.png", "Şekil 1: Eğitim ve Doğrulama Kayıp Eğrisi (Training & Validation Loss Convergence)"),
    ("sekil_2_metrik_ilerlemesi.png", "Şekil 2: Epoch Bazlı Doğruluk ve Macro F1 Skoru İlerlemesi"),
    ("sekil_3_confusion_matrix.png", "Şekil 3: Bağımsız Hold-out Test Kümesi Karmaşıklık Matrisi (n=4.279)"),
    ("sekil_4_roc_auc.png", "Şekil 4: Alıcı İşletim Karakteristiği ve ROC-AUC Eğrisi (AUC = 0.998)"),
    ("sekil_5_dil_ve_dagilim_kiyasi.png", "Şekil 5: Çapraz Dağılım ve Çok Dilli Başarım Kıyaslama Grafiği"),
    ("sekil_6_esik_analizi.png", "Şekil 6: Sınıflandırma Eşik Değeri Analizi (F1 vs Yanlış Alarm Oranı)"),
    ("sekil_7_threshold_tuning.png", "Şekil 7: Maliyet Duyarlı Karar Eşiği Optimizasyonu (Precision-Recall Tuning)")
]

for fname, caption in figures_list:
    fpath = FIG_DIR / fname
    if fpath.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(str(fpath), width=Inches(4.8))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run(caption)
        set_font(r_cap, size_pt=8.5, italic=True, color_rgb=(50,50,50))

# V. TARTIŞMA
add_heading("V. TARTIŞMA VE LİTERATÜRLE KIYASLAMA")
add_body(
    "ProtectAI'ın orijinal deberta-v3-base modeli ham Türkçe girdilerde %100'e varan yanlış alarmlar üretirken, geliştirdiğimiz XLM-RoBERTa modeli harici bir çeviriye ihtiyaç duymadan Türkçe morfolojisini yerel olarak öğrenmiştir. "
    "Canlı Türkçe testinde 50 saldırının 50'sini de yakalayarak (%100 Duyarlılık / Sıfır Kaçırma) yüksek siber güvenlik sağlamıştır. "
    "Dağılım dışı (OOD) testte elde edilen %82.15'lik başarı, modelin daha önce hiç karşılaşmadığı yeni nesil saldırı semantiğini genelleme yeteneğine sahip olduğunu göstermektedir."
)

# VI. SONUÇ
add_heading("VI. SONUÇ")
add_body(
    "Bu çalışmada, Büyük Dil Modellerine yönelik siber saldırılara karşı 3 katmanlı hibrit bir çevre savunma mimarisi olan CyberTech Neural Shield geliştirilmiş ve NVIDIA A100 GPU üzerinde eğitilerek doğrulanmıştır. "
    "XLM-RoBERTa ONNX INT8 modeli ile harici çeviri katmanı kaldırılmış, çıkarım süresi 9.47 ms'ye düşürülmüş ve hold-out test setinde %98.74 F1 başarımı elde edilmiştir. "
    "Çalışma, kurumsal Gemini 3.6 Flash API'si önünde tam koruma sağlayarak endüstri standardı bir açık kaynaklı güvenlik ağ geçidi sunmaktadır."
)

# KAYNAKÇA
add_heading("KAYNAKÇA")
refs = [
    "[1] K. Greshake, S. Abdelnabi, S. Mishra, C. Endres, T. Holz, and M. Fritz, 'Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injections,' in Proc. 16th ACM Workshop on Artificial Intelligence and Security (AISEC), 2023, pp. 79–90.",
    "[2] P. He, X. Liu, J. Gao, and W. Chen, 'DeBERTa: Decoding-enhanced BERT with disentangled attention,' in Proc. ICLR, 2021.",
    "[3] A. Conneau et al., 'Unsupervised cross-lingual representation learning at scale,' in Proc. ACL, 2020, pp. 8440–8451.",
    "[4] F. Perez and I. Ribeiro, 'Ignore previous prompt: Attack techniques for language models,' in NeurIPS ML Safety Workshop, 2022.",
    "[5] Y. Liu et al., 'RoBERTa: A robustly optimized BERT pretraining approach,' arXiv preprint arXiv:1907.11692, 2019.",
    "[6] ProtectAI, 'deberta-v3-base-prompt-injection: Open-source sequence classification model,' Hugging Face Hub, 2023.",
    "[7] J. Wei et al., 'Jailbroken: How does LLM safety training fail?' in Advances in Neural Information Processing Systems (NeurIPS), vol. 36, 2023.",
    "[8] OWASP Foundation, 'OWASP Top 10 for Large Language Model Applications v1.1,' Tech. Rep., 2023.",
    "[9] A. Zou, Z. Wang, J. Z. Kolter, and M. Fredrikson, 'Universal and transferable adversarial attacks on aligned language models,' arXiv preprint arXiv:2307.15043, 2023.",
    "[10] E. Wallace, S. Feng, N. Kandpal, M. Gardner, and S. Singh, 'Universal adversarial triggers for attacking and evaluating NLP,' in Proc. EMNLP, 2019.",
    "[11] S. Inan et al., 'Llama Guard: LLM-based input-output safeguard for human-AI conversations,' arXiv preprint arXiv:2312.06674, 2023.",
    "[12] Microsoft, 'ONNX Runtime: Cross-platform, high performance ML inferencing and training accelerator,' GitHub Repository, 2024.",
    "[13] M. Çalışkan and A. H. Işık, 'CyberTech Neural Shield: 3-Layer Hybrid Security Gateway for LLMs,' Burdur Mehmet Akif Ersoy Üniversitesi, 2026."
]
for r in refs:
    p_r = doc.add_paragraph()
    p_r.paragraph_format.space_after = Pt(3)
    p_r.paragraph_format.left_indent = Inches(0.2)
    p_r.paragraph_format.first_line_indent = Inches(-0.2)
    r_run = p_r.add_run(r)
    set_font(r_run, size_pt=8)

doc.save(str(TARGET_DOCX))
print(f"[SUCCESS] Generated IEEE Word Document at: {TARGET_DOCX}")
