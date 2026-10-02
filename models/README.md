# Model Training Results

## YOLOv8 Pothole Detection

The YOLOv8 object detection model was trained **from scratch without using pretrained weights**.

---

## Experiment 1 — Initial Model

The initial model was trained using the first pothole dataset.

### Dataset

- Total Images: **3,381**
- Classes: **1**
- Class: `pothole`
- Training Images: **2,586**
- Validation Images: **617**
- Testing Images: **178**
- Image Size: **640 × 640**

### Training Configuration

- Model: **YOLOv8**
- Training Type: **From Scratch**
- Epochs: **100**
- Image Size: **640 × 640**
- GPU: **NVIDIA Tesla T4**
- Dataset Format: **YOLOv8**

### 100-Epoch Validation Results

| **Metric** | **Result** |
| ---------- | ---------- |
| Precision  | **78.13%** |
| Recall     | **62.22%** |
| mAP@50     | **71.66%** |
| mAP@50-95  | **42.76%** |

### Detection Analysis

The confusion matrix showed the following detection behavior:

- **1,243 pothole instances** were correctly detected.
- **602 pothole instances** were missed by the model (false negatives).
- **506 false pothole detections** were produced (false positives).

Therefore, although the model successfully detects many potholes, it still misses a significant number of potholes and sometimes detects non-pothole regions as potholes.

### Confidence Threshold Analysis

The F1-Confidence curve showed the highest F1 score of approximately **0.69 at a confidence threshold of 0.337**.

Based on this analysis, a confidence threshold of approximately **0.337** was tested during inference.

### Initial Model Status

The initial 100-epoch model provided a starting point for pothole detection. Further experiments were conducted using an updated dataset and training configuration.

---

## Experiment 2 — Updated Dataset and Improved Model

A second training experiment was conducted using an updated pothole dataset containing more images.

### Dataset

The updated dataset contains **7,871 images** with a single detection class:

- Total Images: **7,871**
- Classes: **1**
- Class: `pothole`

### Dataset Split

| Dataset Split | Images | Percentage |
|---|---:|---:|
| Training | **5,008** | **64%** |
| Validation | **1,843** | **23%** |
| Testing | **1,020** | **13%** |

### Preprocessing

- **Auto-Orient:** Applied
- **Resize:** Stretch to **512 × 512**

### Augmentations

- **No augmentations were applied**

### Training Configuration

- Model: **YOLOv8n**
- Training Type: **From Scratch**
- Maximum Epochs: **200**
- Batch Size: **16**
- Image Size: **512 × 512**
- GPU: **NVIDIA Tesla T4**
- Dataset Format: **YOLOv8**

Training was manually stopped after approximately **133 completed epochs**. The best model checkpoint was saved as `best.pt`.

### Validation Results

| **Metric** | **Result** |
| ---------- | ---------- |
| Precision  | **79.8%** |
| Recall     | **66.5%** |
| mAP@50     | **74.8%** |
| mAP@50-95  | **44.9%** |

### Test Prediction

The trained model was tested on all **1,020 test images**.

- Test Images Processed: **1,020**
- Image Size: **512 × 512**
- Confidence Threshold: **0.25**
- Average Preprocessing Time: **1.2 ms/image**
- Average Inference Time: **8.7 ms/image**
- Average Postprocessing Time: **1.3 ms/image**
- Prediction Results: **Successfully generated**
- Visual inspection: **Potholes were detected correctly**

The prediction results were saved to:

`/content/runs/detect/predict`

### Current Model Status

The updated model has completed:

- Dataset preparation
- Model training
- Validation
- Test-set prediction
- Visual verification of predictions

The trained `best.pt` model is ready to be integrated into the **Smart Pothole Detection System** application.

**Status: Model Training & Testing Completed ✅**

---

## Experiment Comparison

| Metric | Experiment 1 | Experiment 2 |
|---|---:|---:|
| Total Dataset Images | 3,381 | **7,871** |
| Training Images | 2,586 | **5,008** |
| Validation Images | 617 | **1,843** |
| Test Images | 178 | **1,020** |
| Image Size | 640 × 640 | **512 × 512** |
| Precision | 78.13% | **79.8%** |
| Recall | 62.22% | **66.5%** |
| mAP@50 | 71.66% | **74.8%** |
| mAP@50-95 | 42.76% | **44.9%** |

### Summary

The second experiment used an updated dataset with **7,871 images** compared with **3,381 images** in the initial experiment. The second experiment achieved higher validation values for **Precision, Recall, mAP@50, and mAP@50-95** than the initial experiment.

The second model was also evaluated on **1,020 test images**, and visual inspection confirmed that the model was detecting potholes correctly.

**Current Status: Model Training and Testing Completed ✅**
