Yes. We should **keep Experiment 1 and the old Experiment 2 information exactly as you wrote it**, and add the **final 200-epoch results as the updated/final result of Experiment 2**.

One important correction: your current final test set is **1,019 images**, because we removed the one incorrectly formatted annotation. So I would not write 1,020 as the final evaluated count.

Here is the updated version you can directly replace your current section with:

---

# Model Training Results

## YOLOv8 Pothole Detection

The YOLOv8 object detection model was trained **from scratch without using pretrained weights**.

---

## Experiment 1 — Initial Model

The initial model was trained using the first pothole dataset.

### Dataset

* Total Images: **3,381**
* Classes: **1**
* Class: `pothole`
* Training Images: **2,586**
* Validation Images: **617**
* Testing Images: **178**
* Image Size: **640 × 640**

### Training Configuration

* Model: **YOLOv8**
* Training Type: **From Scratch**
* Epochs: **100**
* Image Size: **640 × 640**
* GPU: **NVIDIA Tesla T4**
* Dataset Format: **YOLOv8**

### 100-Epoch Validation Results

| **Metric** | **Result** |
| ---------- | ---------- |
| Precision  | **78.13%** |
| Recall     | **62.22%** |
| mAP@50     | **71.66%** |
| mAP@50-95  | **42.76%** |

### Detection Analysis

The confusion matrix showed the following detection behavior:

* **1,243 pothole instances** were correctly detected.
* **602 pothole instances** were missed by the model (false negatives).
* **506 false pothole detections** were produced (false positives).

Therefore, although the model successfully detects many potholes, it still misses a significant number of potholes and sometimes detects non-pothole regions as potholes.

### Confidence Threshold Analysis

The F1-Confidence curve showed the highest F1 score of approximately **0.69 at a confidence threshold of 0.337**.

Based on this analysis, a confidence threshold of approximately **0.337** was tested during inference.

### Initial Model Status

The initial 100-epoch model provided a starting point for pothole detection. Further experiments were conducted using an updated dataset and training configuration.

---

# Experiment 2 — Updated Dataset and Improved Model

A second training experiment was conducted using an updated pothole dataset containing more images.

### Dataset

The updated dataset contains **7,871 images** with a single detection class:

* Total Images: **7,871**
* Classes: **1**
* Class: `pothole`

### Dataset Split

| **Dataset Split** | **Images** | **Percentage** |
| ----------------- | ---------- | -------------- |
| Training          | **5,008**  | **64%**        |
| Validation        | **1,843**  | **23%**        |
| Testing           | **1,020**  | **13%**        |

### Preprocessing

* **Auto-Orient:** Applied
* **Resize:** Stretch to **512 × 512**

### Augmentations

* **No augmentations were applied**

### Initial Training Configuration

* Model: **YOLOv8n**
* Training Type: **From Scratch**
* Maximum Epochs: **200**
* Batch Size: **16**
* Image Size: **512 × 512**
* GPU: **NVIDIA Tesla T4**
* Dataset Format: **YOLOv8**

### Initial Training Result — Approximately 133 Epochs

Training was initially stopped after approximately **133 completed epochs**. The best model checkpoint was saved as `best.pt`.

### Validation Results — Initial Training

| **Metric** | **Result** |
| ---------- | ---------- |
| Precision  | **79.8%**  |
| Recall     | **66.5%**  |
| mAP@50     | **74.8%**  |
| mAP@50-95  | **44.9%**  |

### Test Prediction — Initial Training

The trained model was tested on the test dataset.

* Test Images Processed: **1,020**
* Image Size: **512 × 512**
* Confidence Threshold: **0.25**
* Average Preprocessing Time: **1.2 ms/image**
* Average Inference Time: **8.7 ms/image**
* Average Postprocessing Time: **1.3 ms/image**
* Prediction Results: **Successfully generated**
* Visual inspection: **Potholes were detected correctly**

The prediction results were saved to:

`/content/runs/detect/predict`

---

# Final Training — 200 Epochs

After the initial training experiment, the model training was continued using the saved training checkpoint to complete the planned **200 epochs**.

The final model was evaluated using the updated validation and test datasets.

### Final Training Configuration

* Model: **YOLOv8n**
* Training Type: **From Scratch**
* Total Epochs: **200**
* Batch Size: **16**
* Image Size: **512 × 512**
* GPU: **NVIDIA Tesla T4**
* Dataset Format: **YOLOv8**
* Pretrained Weights: **Not used**

### Final Validation Results

| **Metric** | **Final Result** |
| ---------- | ---------------: |
| Precision  |       **81.49%** |
| Recall     |       **68.12%** |
| mAP@50     |       **75.91%** |
| mAP@50-95  |       **46.81%** |

Validation was performed on **1,843 images** containing **4,932 pothole instances**.

### Final Test Results

After cleaning one incorrectly formatted test annotation, the final evaluation was performed on **1,019 valid test images** containing **2,588 pothole instances**.

| **Metric** | **Final Test Result** |
| ---------- | --------------------: |
| Precision  |            **79.74%** |
| Recall     |            **71.02%** |
| mAP@50     |            **77.24%** |
| mAP@50-95  |            **48.07%** |

### Final Model Status

The final 200-epoch YOLOv8n model achieved improved performance compared with the earlier training results.

The final model achieved:

* **79.74% Precision**
* **71.02% Recall**
* **77.24% mAP@50**
* **48.07% mAP@50-95**

The trained model files were saved as:

```text
best.pt
last.pt
```

The `best.pt` model is intended for final pothole detection and application integration, while `last.pt` is retained as the final training checkpoint.

**Status: Final Model Training, Validation and Testing Completed ✅**

---

# Experiment Comparison

| **Metric**           | **Experiment 1** | **Experiment 2 — ~133 Epochs** | **Final — 200 Epochs** |
| -------------------- | ---------------: | -----------------------------: | ---------------------: |
| Total Dataset Images |            3,381 |                      **7,871** |              **7,871** |
| Training Images      |            2,586 |                      **5,008** |              **5,008** |
| Validation Images    |              617 |                      **1,843** |              **1,843** |
| Test Images          |              178 |                      **1,020** |        **1,019 valid** |
| Image Size           |        640 × 640 |                  **512 × 512** |          **512 × 512** |
| Precision            |           78.13% |                          79.8% |        **79.74% test** |
| Recall               |           62.22% |                          66.5% |        **71.02% test** |
| mAP@50               |           71.66% |                          74.8% |        **77.24% test** |
| mAP@50-95            |           42.76% |                          44.9% |        **48.07% test** |

### Final Summary

The initial experiment used **3,381 images**, while the updated experiment used a significantly larger dataset containing **7,871 images**.

The updated YOLOv8n model was trained **from scratch** and eventually completed the planned **200 epochs**. Compared with the earlier approximately 133-epoch training result, the final model achieved stronger validation performance:

* Precision: **79.8% → 81.49%**
* Recall: **66.5% → 68.12%**
* mAP@50: **74.8% → 75.91%**
* mAP@50-95: **44.9% → 46.81%**

The final test evaluation achieved **79.74% Precision, 71.02% Recall, 77.24% mAP@50, and 48.07% mAP@50-95**.

Therefore, the **200-epoch YOLOv8n model is currently the best-performing model in these experiments** and is ready for integration into the **Smart Pothole Detection System**.

**Current Status: Model Training and Testing Completed ✅**
