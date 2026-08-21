import os
from huggingface_hub import HfApi

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_USER = os.getenv("HF_USER", "Mustafa5645344")
repo_id = f"{HF_USER}/specifly-insect-dataset"

api = HfApi(token=HF_TOKEN)
api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True, private=False)

dataset_card = """---
license: mit
task_categories:
- object-detection
- image-classification
tags:
- insect-detection
- roboflow
- agriculture
- pest-monitoring
- biology
size_categories:
- 10K<n<100K
---

# Specifly: 50K Augmented Agricultural Insect Dataset

This dataset contains **49,680 augmented RGB images** of agricultural pests and beneficial insects across 21 biological taxa, generated and annotated via **Roboflow**.

## Dataset Overview
- **Total Images:** 49,680
- **Primary Task:** Multi-class Insect Detection (YOLOv8 bounding boxes) & Fine-Grained Classification
- **Domain:** Agricultural crop protection, entomology, and autonomous farm robotics

## Species / Classes Covered (21 Taxa)
1. `ant`
2. `aphid`
3. `bees`
4. `butterfly`
5. `caterpillar`
6. `cicada`
7. `dragonfly`
8. `grasshopper`
9. `green_lacewing`
10. `ladybug`
11. `leafhopper`
12. `mantis`
13. `mole_cricket`
14. `planthopper`
15. `rhino_beetle`
16. `rice_bug`
17. `spider`
18. `stem_borer`
19. `stink_bug`
20. `undefined`
21. `weevil`

## How to Access & Download Dataset

### Option 1: Direct Roboflow SDK Integration
```python
from roboflow import Roboflow

rf = Roboflow(api_key="YOUR_ROBOFLOW_KEY")
project = rf.workspace("specifly").project("specifly-3-rwm7i")
version = project.version(1)
dataset = version.download("yolov8")
```

### Option 2: Pre-trained Models
You can utilize the models trained on this dataset directly from Hugging Face Hub:
- **Vision Transformer (ViT) Classifier:** [`Mustafa5645344/insect-detection-vit`](https://huggingface.co/Mustafa5645344/insect-detection-vit)
- **YOLOv8 Detector:** [`Mustafa5645344/insect-detection-yolov8`](https://huggingface.co/Mustafa5645344/insect-detection-yolov8)
"""

temp_file = "temp_dataset_readme.md"
with open(temp_file, "w", encoding="utf-8") as f:
    f.write(dataset_card)

api.upload_file(
    path_or_fileobj=temp_file,
    path_in_repo="README.md",
    repo_id=repo_id,
    repo_type="dataset"
)

if os.path.exists(temp_file):
    os.remove(temp_file)

print(f"[SUCCESS] Dataset Card uploaded to Hugging Face: https://huggingface.co/datasets/{repo_id}")
