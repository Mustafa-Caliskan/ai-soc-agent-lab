"""
Generate CyberTech_IMRAD_Raporu_Revize.docx with formatted tables and embedded figures.
"""
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"
FIGURES_DIR = DOCS_DIR / "figures"
TARGET_DOCX = DOCS_DIR / "CyberTech_IMRAD_Raporu_Revize.docx"

doc = docx.Document()

for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

def set_font(run, name="Times New Roman", size_pt=11, bold=False, italic=False, color_rgb=(0,0,0)):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

def add_heading_1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_font(run, size_pt=14, bold=True, color_rgb=(20, 45, 90))
    return p

def add_heading_2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_font(run, size_pt=12, bold=True, color_rgb=(30, 60, 110))
    return p

def add_body(text, bold_prefix=None, space_after=6, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_font(r_pre, size_pt=11, bold=True)
    run = p.add_run(text)
    set_font(run, size_pt=11, italic=italic)
    return p

def add_figure(img_name, caption):
    img_path = FIGURES_DIR / img_name
    if img_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(str(img_path), width=Inches(5.5))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run(caption)
        set_font(r_cap, size_pt=9.5, italic=True, color_rgb=(60, 60, 60))

# ── Title & Authors ──────────────────────────────────────────────────────────
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(18)
p_title.paragraph_format.space_after = Pt(4)
r_t = p_title.add_run("CyberTech Neural Shield: Büyük Dil Modelleri İçin Çok Katmanlı Hibrit Güvenlik Mimarisi")
set_font(r_t, size_pt=16, bold=True, color_rgb=(10, 30, 70))

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(12)
r_sub = p_sub.add_run("Doğrudan Çok Dilli (XLM-RoBERTa) Semantik Tehdit Sınıflandırması, Unicode Steganografi Tespiti ve DLP Entegrasyonu")
set_font(r_sub, size_pt=12, italic=True, color_rgb=(50, 50, 50))

p_auth = doc.add_paragraph()
p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_auth.paragraph_format.space_after = Pt(16)
r_a1 = p_auth.add_run("Mustafa ÇALIŞKAN¹, Prof. Dr. Ali Hakan IŞIK²\n")
set_font(r_a1, size_pt=11, bold=True)
r_a2 = p_auth.add_run("¹Mühendislik Fakültesi, Bilgisayar Mühendisliği Bölümü, Burdur Mehmet Akif Ersoy Üniversitesi\n²Bilgisayar Mühendisliği Bölümü (Akademik Danışman), Burdur Mehmet Akif Ersoy Üniversitesi\nİletişim: mustafacaliskan@ogr.mehmetakif.edu.tr, hisik@mehmetakif.edu.tr")
set_font(r_a2, size_pt=9.5, italic=True, color_rgb=(80, 80, 80))

# ── Abstract ─────────────────────────────────────────────────────────────────
add_heading_1("Özet")
add_body(
    "Büyük Dil Modellerinin (LLM) kurumsal iş akışlarına ve kamu altyapılarına entegre edilmesi, doğal dil arayüzlerini hedef alan yeni nesil siber tehdit vektörlerini beraberinde getirmiştir. Komut enjeksiyonu (Prompt Injection), jailbreaking (etik ve güvenlik sınırlarını aşma), sistem komutu sızıntısı ve Unicode Tag (U+E0000 - U+E007F aralığındaki 'Görünmez Mürekkep') steganografisi gibi teknikler, geleneksel ağ güvenlik duvarlarının ve statik filtrelerin etrafından kolaylıkla dolaşabilmektedir. Bu çalışmada, söz konusu tehditlere karşı uçtan uca savunma sağlayan ve çevre birim (peripheral gateway) düzeyinde konumlanan 3 katmanlı hibrit bir güvenlik mimarisi (CyberTech Neural Shield) önerilmektedir. Katman 1 regex ve steganografi dedektöründen (<0.3 ms), Katman 2 NVIDIA A100 GPU üzerinde eğitilip INT8 ONNX motoruyla optimize edilen çok dilli XLM-RoBERTa sınıflandırıcısından (9.47 ms), Katman 3 ise gidiş-dönüş veri sızıntılarını önleyen DLP motorundan oluşmaktadır. Sistem, korunan ana model olarak Google Gemini 3.6 Flash (gemini-3.6-flash) API'sini barındırmaktadır. 4.279 test örneğinde %98.74 F1-skoru ve %0.93 yanlış alarm oranı (FPR) elde edilmiş, çıkarım gecikmesi 126 ms'den 9.47 ms'ye (12.3 kat hızlanma) düşürülmüştür."
)
add_body("LLM Güvenliği, Prompt Injection Savunması, XLM-RoBERTa, INT8 Kuantizasyonu, ONNX Runtime, Unicode Steganografi, Veri Sızıntısı Önleme (DLP), Google Gemini 3.6 Flash.", bold_prefix="Anahtar Kelimeler: ")

# ── 1. Giriş ─────────────────────────────────────────────────────────────────
add_heading_1("1. Giriş")
add_body(
    "Büyük Dil Modelleri (LLM), kurumsal karar destek mekanizmalarında, havalimanı ve bankacılık operasyonlarında ve müşteri iletişim sistemlerinde merkezi bir rol üstlenmiştir. Google Gemini, OpenAI GPT ve Meta LLaMA gibi milyarlarca parametreli temel modeller, olağanüstü üretim kabiliyetleri sunmaktadır. Ne var ki, sistem mimarilerinin komutlar ile kullanıcı girdilerini aynı bağlam penceresi içerisinde işlemesi, geleneksel yazılım güvenliğinde görülmeyen yapısal bir zafiyet doğurmuştur."
)
add_body(
    "Komut enjeksiyonu (Prompt Injection) ve jailbreaking saldırılarında, saldırgan sistem talimatlarını manipüle ederek yetkisiz eylemler icra edebilmektedir. Buna ek olarak, Unicode Tag karakterleri (U+E0000 - U+E007F) kullanılarak icra edilen 'Invisible Ink' (Görünmez Mürekkep) steganografik saldırıları, kullanıcı ekranında tek bir masum emoji veya boşluk olarak görünürken dil modeline gizli ve yıkıcı direktifler iletebilmektedir."
)
add_body(
    "Kurumsal ortamda LLM güvenliğini sağlama noktasında üç temel darboğaz bulunmaktadır: (1) Yüksek çıkarım gecikmesi (LlamaGuard vb. 1-2 saniye), (2) Çok dilli tokenizasyon kırılması ve harici çeviri modellerinin 100+ ms ek gecikme yaratması, (3) Aşırı yanlış alarm (False Positive) ile meşru kurumsal sorguların engellenmesi. Bu çalışmada tüm bu darboğazları aşan 3 katmanlı hibrit bir güvenlik mimarisi geliştirilmiştir."
)

# ── 2. Yöntem ve Sistem Mimarisi ─────────────────────────────────────────────
add_heading_1("2. Yöntem ve Sistem Mimarisi")
add_body(
    "CyberTech Neural Shield, kullanıcı girdisi kurumsal modele ulaşmadan önce ve model çıktısı kullanıcıya dönmeden önce denetim sağlayan 3 bağımsız katmandan oluşmaktadır."
)
add_figure("sekil_1_mimari.png", "Şekil 1: CyberTech Neural Shield 3 Katmanlı Hibrit Güvenlik Mimarisi ve Çevre Birim (Peripheral) Savunma Akışı.")

add_heading_2("2.1. Katman 1: Regex ve Unicode Steganografi Filtresi")
add_body(
    "Ham metinler ilk olarak sıfırıncı dereceden mikro-filtreleme katmanına iletilir. Bilinen saldırı şablonları düzenli ifadelerle taranırken, Unicode Tag (0xE0000 - 0xE007F) aralığındaki gizli baytlar 0.28 ms'de yakalanarak bloke edilir. Bu sayede gereksiz model çıkarım maliyeti önlenir."
)

add_heading_2("2.2. Katman 2: XLM-RoBERTa ONNX INT8 Semantik Sınıflandırıcısı")
add_body(
    "Katman 1'i geçen girdiler derin niyet analizi yapılmak üzere Katman 2'ye aktarılır. Önceki çeviri tabanlı tek dilli modellerin handikaplarını aşmak üzere xlm-roberta-base mimarisi NVIDIA A100-SXM4-40GB GPU üzerinde dengeli çok dilli veri setleriyle eğitilmiştir. Model INT8 kuantizasyonu ile 278 MB boyutuna ve ONNX Runtime motoruyla CPU üzerinde 9.47 ms çıkarım süresine optimize edilmiştir."
)
add_figure("sekil_7_threshold_tuning.png", "Şekil 2: F1-Skoru ve FPR Dengesi İçin Eşik Değeri (Threshold) Optimizasyon Analizi (Optimal tau = 0.50).")

add_heading_2("2.3. Katman 3: DLP (Veri Sızıntısı Önleme) Çıktı Filtresi")
add_body(
    "Korunan ana dil modelinin (Google Gemini 3.6 Flash) ürettiği yanıtlar kullanıcıya iletilmeden önce Katman 3 tarafından taranır. TCKN (Luhn doğrulamalı), Kredi Kartı (PAN Luhn doğrulamalı), IBAN ve gizli API anahtarları <0.5 ms'de tespit edilerek maskelenir."
)

# ── 3. Deneysel Bulgular ve Başarım Analizi ─────────────────────────────────
add_heading_1("3. Deneysel Bulgular ve Başarım Analizi")
add_body(
    "Sistemin başarımı; 4.279 örnekli hold-out test kümesi, 1.000 örnekli dağılım dışı (OOD) Neuralchemy kümesi ve 100 örnekli canlı Türkçe benchmark kümesi üzerinde test edilmiştir."
)

# Table 1
t = doc.add_table(rows=6, cols=7)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ["Test Kümesi / Model", "Örnek ($n$)", "Doğruluk", "F1-Skoru", "Kesinlik", "Duyarlılık", "FPR"]
data = [
    ["XLM-RoBERTa (Hold-out Test)", "4.279", "%98.74", "0.9874", "%99.07", "%98.41", "%0.93"],
    ["XLM-RoBERTa (OOD Neuralchemy)", "1.000", "%81.90", "0.8215", "%80.60", "%83.75", "%19.96"],
    ["XLM-RoBERTa (Canlı Türkçe)", "100", "%90.00", "0.9091", "%83.33", "%100.00", "%20.00"],
    ["Eski DeBERTa-v3 + Çeviri", "80", "%86.25", "0.8791", "%78.43", "%100.00", "%27.50"],
    ["Katman 1 (Tek Başına Regex)", "80", "%68.75", "0.5455", "%100.00", "%37.50", "%0.00"]
]
for col_idx, h in enumerate(headers):
    cell = t.cell(0, col_idx)
    p = cell.paragraphs[0]
    r = p.add_run(h)
    set_font(r, size_pt=9.5, bold=True)
for row_idx, row_data in enumerate(data):
    for col_idx, val in enumerate(row_data):
        cell = t.cell(row_idx + 1, col_idx)
        p = cell.paragraphs[0]
        r = p.add_run(val)
        is_bold = "XLM-RoBERTa" in row_data[0] and col_idx in [2, 3, 6]
        set_font(r, size_pt=9, bold=is_bold)

p_tcap = doc.add_paragraph()
p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_tcap.paragraph_format.space_before = Pt(4)
p_tcap.paragraph_format.space_after = Pt(8)
r_tc = p_tcap.add_run("Tablo 1: Güvenlik Modelleri ve Test Kümeleri Başarım Metrikleri.")
set_font(r_tc, size_pt=9.5, italic=True)

add_figure("sekil_2_confusion_matrices.png", "Şekil 3: XLM-RoBERTa Modelinin Hold-out, OOD ve Canlı Türkçe Testlerindeki Hata Matrisleri (Confusion Matrices).")
add_figure("sekil_3_roc_pr_curves.png", "Şekil 4: Modelin ROC (EAA = 0.9984) ve Precision-Recall (EAA = 0.9987) Başarım Eğrileri.")
add_figure("sekil_4_latency_comparison.png", "Şekil 5: Çıkarım Gecikmesi Kıyaslaması (Helsinki Çeviri + DeBERTa: 126.10 ms vs. XLM-RoBERTa ONNX INT8: 9.47 ms - 12.3 Kat Hızlanma).")
add_figure("sekil_5_error_analysis.png", "Şekil 6: Dağılım Dışı Test Kümesinde Hata Analizi ve Güven Skoru Histogramı.")
add_figure("sekil_6_multilingual_ood.png", "Şekil 7: Çok Dilli ve Dağılım Dışı Dayanıklılık Analizi.")

# ── 4. Tartışma ve Sonuç ─────────────────────────────────────────────────────
add_heading_1("4. Tartışma ve Sonuç")
add_body(
    "Deneysel bulgular; LLM güvenliğinin model içsel kurallarıyla veya sahte prompt manipülasyonlarıyla değil, bağımsız ve yerel bir güvenlik ağ geçidi (peripheral gateway) mimarisiyle sağlanmasının hem hız hem de güvenlik açısından üstün olduğunu kanıtlamıştır."
)
add_body(
    "XLM-RoBERTa mimarisinin sağladığı doğrudan çok dillilik, harici çeviri modellerinin yarattığı semantik bilgi kaybını ve yüksek gecikmeyi ortadan kaldırmıştır. ONNX INT8 kuantizasyonu sayesinde model, standart kurumsal sunucu CPU'larında 9.47 ms gecikmeyle üretim ortamında hizmet verebilmektedir. Korunan kurumsal model olarak entegre edilen Google Gemini 3.6 Flash (gemini-3.6-flash), filtrelenen güvenli isteklere yaklaşık 350-500 ms aralığında milisaniyelik gecikmeyle yanıt vermektedir."
)

# ── Kaynaklar ────────────────────────────────────────────────────────────────
add_heading_1("Kaynaklar")
refs = [
    "[1] K. Greshake et al., 'Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injections,' in Proc. 16th ACM Workshop on Artificial Intelligence and Security (AISEC), 2023, pp. 79–90.",
    "[2] A. Conneau et al., 'Unsupervised cross-lingual representation learning at scale,' in Proc. 58th Annual Meeting of the Association for Computational Linguistics (ACL), 2020, pp. 8440–8451.",
    "[3] F. Perez and I. Ribeiro, 'Ignore previous prompt: Attack techniques for language models,' in NeurIPS ML Safety Workshop, 2022.",
    "[4] OWASP Foundation, 'OWASP Top 10 for Large Language Model Applications v1.1,' Tech. Rep., 2023.",
    "[5] S. Inan et al., 'Llama Guard: LLM-based input-output safeguard for human-AI conversations,' arXiv preprint arXiv:2312.06674, 2023.",
    "[6] Google DeepMind, 'Gemini 3.6 Flash Model Documentation and Interactions API Reference,' Google AI Cloud Docs, 2024.",
    "[7] M. Çalışkan and A. H. Işık, 'CyberTech Neural Shield: 3-Layer Peripheral Defense Architecture for LLMs,' Burdur Mehmet Akif Ersoy University Research Repository, 2026."
]
for r in refs:
    p_r = doc.add_paragraph()
    p_r.paragraph_format.space_after = Pt(3)
    p_r.paragraph_format.left_indent = Inches(0.25)
    p_r.paragraph_format.first_line_indent = Inches(-0.25)
    r_run = p_r.add_run(r)
    set_font(r_run, size_pt=9.5)

doc.save(str(TARGET_DOCX))
print(f"[SUCCESS] Generated CyberTech_IMRAD_Raporu_Revize.docx at: {TARGET_DOCX}")
