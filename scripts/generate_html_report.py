import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
md_path = ROOT / "docs" / "EVREN_EMPIRICAL_BENCHMARK_REPORT.md"
html_path = ROOT / "docs" / "EVREN_EMPIRICAL_BENCHMARK_REPORT.html"

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

html = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EVREN Çok Modelli Ampirik Benchmark Raporu</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 1050px; margin: 40px auto; padding: 0 24px; color: #1f2937; background-color: #f9fafb; }
.card { background: white; border-radius: 8px; border: 1px solid #e5e7eb; box-shadow: 0 2px 8px rgba(0,0,0,0.04); padding: 28px; margin-bottom: 24px; }
h1 { color: #111827; border-bottom: 2px solid #e5e7eb; padding-bottom: 12px; margin-top: 0; }
h2 { color: #1f2937; border-bottom: 1px solid #f3f4f6; padding-bottom: 8px; margin-top: 28px; }
h3 { color: #374151; margin-top: 20px; }
table { border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 13.5px; background: white; }
th, td { border: 1px solid #e5e7eb; padding: 10px 12px; text-align: left; }
th { background-color: #f9fafb; font-weight: 600; color: #4b5563; }
tr:nth-child(even) { background-color: #f9fafb; }
img { max-width: 100%; height: auto; border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); margin: 20px 0; }
.badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 11.5px; }
.blocked { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
.leaked { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
.allowed { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
.alert { background: #eff6ff; border-left: 4px solid #2563eb; padding: 16px; border-radius: 4px; margin-bottom: 24px; font-size: 14.5px; }
code { background-color: #f3f4f6; padding: 2px 5px; border-radius: 4px; font-family: Consolas, monospace; font-size: 0.9em; }
</style>
</head>
<body>
<div class="card">
<div class="alert">
  <strong>🎯 TÜBİTAK / SSYZ EVREN Ampirik Test Çıktısı:</strong> Bu rapor; Qwen-3.8-Flash-Next ve Google-Gemma-4-31B modellerinin çıplak zafiyetleri ile CyberTech NeuralShield-v5 savunma katmanının ampirik önleme başarısını belgelemektedir.
</div>
"""

lines = md_content.split("\n")
in_table = False

for line in lines:
    line_s = line.strip()
    if line_s.startswith("# "):
        html += f"<h1>{line_s[2:]}</h1>\n"
    elif line_s.startswith("## "):
        html += f"<h2>{line_s[3:]}</h2>\n"
    elif line_s.startswith("### "):
        html += f"<h3>{line_s[4:]}</h3>\n"
    elif line_s.startswith("![Figure 8"):
        html += '<div style="text-align:center;"><img src="figures/figure8_evren_multimodel_asr.png" alt="Figure 8"><br><em style="color:#6b7280; font-size:13px;">Şekil 8: EVREN Süper Bilgisayarı Üzerinde Modellerin Çıplak ve Kalkanlı ASR Oranları (Wilson %95 GA)</em></div>\n'
    elif line_s.startswith("|"):
        if not in_table:
            html += "<table>\n"
            in_table = True
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if all(set(c).issubset({"-", ":", " "}) for c in cells):
            continue
        is_header = "Metrik" in line or "Örnek ID" in line
        tag = "th" if is_header else "td"
        row_html = "<tr>"
        for cell in cells:
            cell_fmt = cell.replace("🚨 **SIZDIRDI**", '<span class="badge leaked">🚨 SIZDIRDI</span>')
            cell_fmt = cell_fmt.replace("🛡️ Direndi", '<span class="badge allowed">🛡️ Direndi</span>')
            cell_fmt = cell_fmt.replace("**BLOCKED**", '<span class="badge blocked">BLOCKED</span>')
            cell_fmt = cell_fmt.replace("**ALLOWED**", '<span class="badge allowed">ALLOWED</span>')
            cell_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", cell_fmt)
            row_html += f"<{tag}>{cell_fmt}</{tag}>"
        row_html += "</tr>\n"
        html += row_html
    else:
        if in_table:
            html += "</table>\n"
            in_table = False
        if line_s.startswith("---"):
            html += "<hr style='border: 0; border-top: 1px solid #e5e7eb; margin: 24px 0;'>\n"
        elif line_s:
            p_text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
            p_text = re.sub(r"`(.*?)`", r"<code>\1</code>", p_text)
            html += f"<p>{p_text}</p>\n"

if in_table:
    html += "</table>\n"

html += """
</div>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ HTML Rapor oluşturuldu:", html_path)
