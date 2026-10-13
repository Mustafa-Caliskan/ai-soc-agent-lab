import json

with open("notebooks/Train_XLM_RoBERTa_v4.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Update Cell 0 Title
nb["cells"][0]["source"] = [
    "# 🛡️ NeuralShield-v5: Üretim Düzeyi Çok Dilli (XLM-RoBERTa) Prompt Injection & Jailbreak Savunma Kalkanı\n",
    "### Siber Güvenlik Odaklı Odak Kaybı (CyberFocalLoss), Sinsi Kurgulama (Framing) Savunması ve Aşırı Öğrenme Karşıtı Üretim Eğitimi\n",
    "\n",
    "**Sürüm:** `NeuralShield-v5-CyberFocal` | **Tarih:** 2026 | **Mimari:** XLM-RoBERTa-base + CyberFocalLoss (γ=2.0)\n"
]

# Update Cell 3: Framing and Hard-Negative multiplier
c3_src = "".join(nb["cells"][3]["source"])
c3_src = c3_src.replace("benign_pool.extend(curated_custom_hard_negatives * 20)", "benign_pool.extend(curated_custom_hard_negatives * 50)")
c3_src = c3_src.replace("attacks_pool.extend(curated_adversarial_framing_attacks * 30)", "attacks_pool.extend(curated_adversarial_framing_attacks * 80)")
nb["cells"][3]["source"] = [line + "\n" for line in c3_src.split("\n")[:-1]]

# Update Cell 4: Add CyberFocalLossTrainer definition
c4_src = "".join(nb["cells"][4]["source"])
focal_code = """
# ── CyberFocalLossTrainer: Sinsi ve Sınırda Kalan Saldırılara Odaklanan Kayıp Fonksiyonu ──
class CyberFocalLossTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        
        loss_fct = nn.CrossEntropyLoss(reduction="none")
        base_loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        
        probs = torch.softmax(logits, dim=-1)
        labels_onehot = nn.functional.one_hot(labels, num_classes=self.model.config.num_labels)
        gathered_probs = torch.sum(probs * labels_onehot, dim=-1)
        
        gamma = 2.0
        focal_weight = (1.0 - gathered_probs) ** gamma
        loss = torch.mean(base_loss * focal_weight)
        
        return (loss, outputs) if return_outputs else loss
"""
c4_src += "\n" + focal_code
nb["cells"][4]["source"] = [line + "\n" for line in c4_src.split("\n")[:-1]]

# Update Cell 5: TrainingArguments & Trainer instantiation
c5_src = "".join(nb["cells"][5]["source"])
c5_src = c5_src.replace('output_dir="./checkpoints_xlm_roberta_v4"', 'output_dir="./checkpoints_xlm_roberta_v5"')
c5_src = c5_src.replace('num_train_epochs=3', 'num_train_epochs=2')
c5_src = c5_src.replace('learning_rate=2e-5', 'learning_rate=1.5e-5')
c5_src = c5_src.replace('weight_decay=0.01', 'weight_decay=0.05')
c5_src = c5_src.replace('metric_for_best_model="f1_macro"', 'metric_for_best_model="eval_loss"')
c5_src = c5_src.replace('greater_is_better=True', 'greater_is_better=False')
c5_src = c5_src.replace('trainer = Trainer(', 'trainer = CyberFocalLossTrainer(')
nb["cells"][5]["source"] = [line + "\n" for line in c5_src.split("\n")[:-1]]

# Update Cell 12: Bundle name
c12_src = "".join(nb["cells"][12]["source"])
c12_src = c12_src.replace('archive_name = "neuralshield_v4_academic_bundle"', 'archive_name = "neuralshield_v5_academic_bundle"')
c12_src = c12_src.replace('output_dir = "./neuralshield_v4_saved"', 'output_dir = "./neuralshield_v5_saved"')
nb["cells"][12]["source"] = [line + "\n" for line in c12_src.split("\n")[:-1]]

with open("notebooks/Train_XLM_RoBERTa_v5.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("[+] Successfully generated notebooks/Train_XLM_RoBERTa_v5.ipynb")
