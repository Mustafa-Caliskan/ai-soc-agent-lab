import os
import zipfile
import shutil
from huggingface_hub import HfApi

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_USER = os.getenv("HF_USER", "Mustafa5645344")

api = HfApi(token=HF_TOKEN)

def upload_vit_model():
    print("\n--- 1. UPLOADING ViT MODEL ---")
    vit_zip = "VIT_BOCEK_AUG_FINAL.zip"
    extract_dir = "scratch_vit_upload"
    os.makedirs(extract_dir, exist_ok=True)
    
    with zipfile.ZipFile(vit_zip, 'r') as z:
        z.extractall(extract_dir)
        
    readme_content = f"""---
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
license: mit
pipeline_tag: image-classification
---

# Insect Classification: Vision Transformer (ViT) Model

This repository contains a fine-tuned **Vision Transformer (ViT)** model (`ViTForImageClassification`) trained to classify **21 distinct insect species** with high precision for agricultural monitoring and biological biodiversity analysis.

## Supported Insect Classes (21 Classes)
- `ant` (0), `aphid` (1), `bees` (2), `butterfly` (3), `caterpillar` (4), `cicada` (5), `dragonfly` (6), `grasshopper` (7), `green_lacewing` (8), `ladybug` (9), `leafhopper` (10), `mantis` (11), `mole_cricket` (12), `planthopper` (13), `rhino_beetle` (14), `rice_bug` (15), `spider` (16), `stem_borer` (17), `stink_bug` (18), `undefined` (19), `weevil` (20)

## Quick Usage

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
    logits = outputs.logits
    predicted_class_idx = logits.argmax(-1).item()

print("Predicted Insect:", model.config.id2label[str(predicted_class_idx)])
```
"""
    with open(os.path.join(extract_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    repo_id = f"{HF_USER}/insect-detection-vit"
    print(f"[+] Creating/Verifying repo: https://huggingface.co/{repo_id}")
    api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, private=False)
    
    print("[+] Uploading ViT model files to Hugging Face...")
    api.upload_folder(
        folder_path=extract_dir,
        repo_id=repo_id,
        repo_type="model"
    )
    print(f"[SUCCESS] ViT Model uploaded: https://huggingface.co/{repo_id}")
    
    # Cleanup temporary extraction folder
    shutil.rmtree(extract_dir, ignore_errors=True)

def upload_yolo_model():
    print("\n--- 2. UPLOADING YOLOv8 MODEL ---")
    yolo_file = "best (10).pt"
    yolo_dir = "scratch_yolo_upload"
    os.makedirs(yolo_dir, exist_ok=True)
    
    shutil.copy(yolo_file, os.path.join(yolo_dir, "best.pt"))
    
    readme_content = f"""---
tags:
- yolo
- yolov8
- object-detection
- insect-detection
- agriculture
license: mit
pipeline_tag: object-detection
---

# Insect Detection: YOLOv8 Object Detection Model

This repository provides pre-trained **YOLOv8** weights for detecting and localizing insect pests in real-time RGB imagery across agricultural fields.

## Model Details
- **Architecture:** YOLOv8 (Ultralytics)
- **Task:** Real-time Bounding Box Object Detection
- **Model Weight File:** `best.pt`

## Quick Usage

```python
from ultralytics import YOLO
from huggingface_hub import hf_hub_download

# 1. Download weights from Hugging Face Hub
weights_path = hf_hub_download(
    repo_id="{HF_USER}/insect-detection-yolov8",
    filename="best.pt"
)

# 2. Load and perform inference
model = YOLO(weights_path)
results = model.predict(source="insect_sample.jpg", conf=0.25, save=True)

# 3. View detections
for result in results:
    boxes = result.boxes
    print("Detected boxes:", boxes.xyxy)
```
"""
    with open(os.path.join(yolo_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)

    repo_id = f"{HF_USER}/insect-detection-yolov8"
    print(f"[+] Creating/Verifying repo: https://huggingface.co/{repo_id}")
    api.create_repo(repo_id=repo_id, repo_type="model", exist_ok=True, private=False)
    
    print("[+] Uploading YOLOv8 model files to Hugging Face...")
    api.upload_folder(
        folder_path=yolo_dir,
        repo_id=repo_id,
        repo_type="model"
    )
    print(f"[SUCCESS] YOLOv8 Model uploaded: https://huggingface.co/{repo_id}")
    
    # Cleanup temporary folder
    shutil.rmtree(yolo_dir, ignore_errors=True)

if __name__ == "__main__":
    upload_vit_model()
    upload_yolo_model()
