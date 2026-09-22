## Model Training Results

### YOLOv8 Pothole Detection

The YOLOv8 object detection model was trained **from scratch without using pretrained weights**.

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

| Metric | Result |
|---|---:|
| Precision | **78.13%** |
| Recall | **62.22%** |
| mAP@50 | **71.66%** |
| mAP@50-95 | **42.76%** |

### Detection Analysis

The confusion matrix showed the following detection behavior:

- **1,243 pothole instances** were correctly detected.
- **602 pothole instances** were missed by the model (false negatives).
- **506 false pothole detections** were produced (false positives).

Therefore, although the model successfully detects many potholes, it still misses a significant number of potholes and sometimes detects non-pothole regions as potholes.

### Confidence Threshold Analysis

The F1-Confidence curve showed the highest F1 score of approximately **0.69 at a confidence threshold of 0.337**.

Based on this analysis, a confidence threshold of approximately **0.337** was tested during inference.

### Current Status

The initial 100-epoch model provides a strong starting point for pothole detection, but the recall indicates that some potholes are still being missed, particularly potholes that are less visible or have weak visual features.

The model is currently **under improvement**. Further experiments are being conducted with training parameters and model configuration to improve:

- Pothole detection recall
- Detection of small and shallow potholes
- Reduction of false detections
- Bounding-box accuracy
- Overall mAP performance

**Status: Work in Progress 🚧**
