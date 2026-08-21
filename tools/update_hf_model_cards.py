from huggingface_hub import HfApi
import os

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_USER = os.getenv("HF_USER", "Mustafa5645344")

api = HfApi(token=HF_TOKEN)

# 1. Detailed ViT Model Card
vit_card = f"""---
language:
- en
- tr
tags:
- vision-transformer
- vit
- image-classification
- insect-detection
- biology
- agriculture
- fine-tuned
license: mit
pipeline_tag: image-classification
metrics:
- accuracy
- f1
model-index:
- name: {HF_USER}/insect-detection-vit
  results:
  - task:
      type: image-classification
      name: Insect Species Classification
    dataset:
      type: specifly-insect-dataset
      name: Specifly 50K Insect Dataset
    metrics:
    - type: accuracy
      value: 0.9851
      name: Accuracy
    - type: f1
      value: 0.9858
      name: F1-Score
---

# Insect Classification: Vision Transformer (ViT) Model

This model is a high-accuracy fine-tuned **Vision Transformer (ViT)** (`google/vit-base-patch16-224-in21k` backbone) trained to classify **21 distinct agricultural insect pest and beneficial species**.

## Training Hardware & Specs
- **Compute:** NVIDIA A100 Tensor Core GPU (SXM4 40GB)
- **Total Training Steps:** 16,600 iterations (20 full epochs)
- **Training Time:** 31 minutes 25 seconds
- **Base Architecture:** Vision Transformer Base (`vit-base-patch16-224`)
- **Image Resolution:** 224 x 224 px

---

## Evaluation Benchmark & Training History

| Epoch | Training Loss | Validation Loss | Accuracy | F1-Score |
| :---: | :---: | :---: | :---: | :---: |
| 1 | 0.3389 | 0.3206 | 97.41% | 97.57% |
| 2 | 0.1076 | 0.1481 | 97.77% | 97.91% |
| 3 | 0.0486 | 0.1073 | 97.83% | 97.95% |
| 4 | 0.0252 | 0.0999 | 98.13% | 98.18% |
| 5 | 0.0167 | 0.0784 | 98.45% | 98.51% |
| 10 | 0.0065 | 0.1190 | 98.03% | 98.12% |
| 15 | 0.0003 | 0.1093 | 98.42% | 98.50% |
| 19 | 0.0001 | 0.1151 | **98.51%** | **98.59%** |
| **20 (Final)** | **0.0001** | **0.1153** | **98.51%** | **98.58%** |

### Top Metrics Achieved:
- **Final Top-1 Accuracy:** **98.51%**
- **Macro F1-Score:** **98.58%**
- **Minimal Training Loss:** **0.000100**

---

## Supported Taxa / Classes (21 Classes)

`ant`, `aphid`, `bees`, `butterfly`, `caterpillar`, `cicada`, `dragonfly`, `grasshopper`, `green_lacewing`, `ladybug`, `leafhopper`, `mantis`, `mole_cricket`, `planthopper`, `rhino_beetle`, `rice_bug`, `spider`, `stem_borer`, `stink_bug`, `undefined`, `weevil`

---

## Quick Inference Usage

```python
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch

model_id = "{HF_USER}/insect-detection-vit"

# Load image processor & model
processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = AutoModelForImageClassification.from_pretrained(model_id)

image = Image.open("insect_sample.jpg")
inputs = processor(images=image, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=-1)
    predicted_idx = outputs.logits.argmax(-1).item()

predicted_label = model.config.id2label[str(predicted_idx)]
confidence = probs[0][predicted_idx].item()

print(f"Species: {{predicted_label}} (Confidence: {{confidence*100:.2f}}%)")
```
"""

# 2. Detailed YOLOv8 Model Card
yolo_card = f"""---
tags:
- yolo
- yolov8
- yolov8m
- ultralytics
- object-detection
- insect-detection
- agriculture
- pest-management
license: mit
pipeline_tag: object-detection
---

# Insect Detection: YOLOv8m Object Detection Model

This repository provides production-ready **YOLOv8m (Medium)** weights fine-tuned on **50,000 augmented agricultural images** (`specifly-3-rwm7i`) for real-time localization and detection of insect pests in fields and greenhouses.

---

## Performance Highlights & Overall Metrics

- **mAP@50:** **85.72%** (0.8572 peak, 0.8540 validation)
- **mAP@50-95:** **51.87%**
- **Precision:** **83.46%**
- **Recall:** **85.86%**
- **F1-Score:** **82.40%**
- **Inference Speed:** **1.5 ms** per image (~400+ FPS on NVIDIA A100)
- **Model Parameters:** 23.23M | **GFLOPs:** 67.9

---

## Detailed Per-Class Validation Breakdown (mAP@50)

| Insect Class | Images | Instances | Precision (P) | Recall (R) | mAP@50 | mAP@50-95 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **All Classes** | **2,987** | **3,097** | **0.835** | **0.816** | **0.854** | **0.519** |
| `stem_borer` | 206 | 223 | 0.957 | 0.978 | **0.992** | 0.794 |
| `leafhopper` | 208 | 216 | 0.942 | 0.949 | **0.976** | 0.681 |
| `ladybug` | 174 | 177 | 0.954 | 0.977 | **0.976** | 0.622 |
| `dragonfly` | 18 | 18 | 0.903 | 0.944 | **0.959** | 0.662 |
| `butterfly` | 186 | 222 | 0.915 | 0.918 | **0.950** | 0.629 |
| `weevil` | 58 | 61 | 0.889 | 0.934 | **0.946** | 0.521 |
| `rice_bug` | 190 | 237 | 0.931 | 0.916 | **0.937** | 0.595 |
| `bees` | 211 | 236 | 0.887 | 0.915 | **0.920** | 0.551 |
| `mole_cricket` | 39 | 41 | 0.882 | 0.854 | **0.890** | 0.471 |
| `grasshopper` | 298 | 317 | 0.882 | 0.852 | **0.885** | 0.510 |
| `planthopper` | 116 | 429 | 0.815 | 0.855 | **0.872** | 0.471 |
| `spider` | 72 | 78 | 0.767 | 0.821 | **0.858** | 0.572 |
| `ant` | 71 | 173 | 0.733 | 0.761 | **0.813** | 0.373 |
| `cicada` | 55 | 78 | 0.808 | 0.744 | **0.797** | 0.423 |
| `caterpillar` | 173 | 208 | 0.853 | 0.716 | **0.791** | 0.400 |
| `stink_bug` | 123 | 123 | 0.727 | 0.724 | **0.777** | 0.535 |
| `aphid` | 36 | 163 | 0.686 | 0.632 | **0.669** | 0.332 |
| `mantis` | 96 | 97 | 0.493 | 0.206 | **0.361** | 0.202 |

---

## Training Setup
- **Framework:** Ultralytics YOLOv8 (v8.3.0)
- **Hardware:** NVIDIA A100-SXM4-40GB
- **Epochs:** 50
- **Batch Size:** 56 | **Image Size:** 640 x 640
- **Optimizer:** AdamW (lr0 = 0.0008, lrf = 0.00008 with Cosine Annealing)
- **Dataset Source:** Roboflow `specifly-3-rwm7i` (Augmented Version)

---

## Quick Usage

```python
from ultralytics import YOLO
from huggingface_hub import hf_hub_download

# Download best weights
weights_path = hf_hub_download(
    repo_id="{HF_USER}/insect-detection-yolov8",
    filename="best.pt"
)

# Run Inference
model = YOLO(weights_path)
results = model.predict(source="field_sample.jpg", conf=0.35, save=True)

for r in results:
    for box in r.boxes:
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        print(f"Found: {{model.names[cls_id]}} with {{conf*100:.1f}}% confidence")
```
"""

# Upload ViT Card
with open("temp_vit_readme.md", "w", encoding="utf-8") as f:
    f.write(vit_card)
api.upload_file(
    path_or_fileobj="temp_vit_readme.md",
    path_in_repo="README.md",
    repo_id=f"{HF_USER}/insect-detection-vit",
    repo_type="model"
)
os.remove("temp_vit_readme.md")
print("[+] Updated ViT Model Card on Hugging Face!")

# Upload YOLOv8 Card
with open("temp_yolo_readme.md", "w", encoding="utf-8") as f:
    f.write(yolo_card)
api.upload_file(
    path_or_fileobj="temp_yolo_readme.md",
    path_in_repo="README.md",
    repo_id=f"{HF_USER}/insect-detection-yolov8",
    repo_type="model"
)
os.remove("temp_yolo_readme.md")
print("[+] Updated YOLOv8 Model Card on Hugging Face!")
