# Kaggle Dataset

## Dataset Name
Potholes-Detection-YOLOv8

## Dataset Details

- Training Images: 1,581
- Validation Images: 396
- Classes: 1 (Pothole)
- Annotation Format: YOLO
- Total Training Bounding Boxes: 5,942
- Invalid Annotation Lines: 0
- Average Potholes per Training Image: 3.76
- Maximum Potholes in One Training Image: 79

## Dataset Configuration

The dataset contains one object-detection class:

- Class ID: 0
- Class Name: pothole

The `data.yaml` file specifies the training and validation image paths and the pothole class.

## Dataset Verification

The dataset was checked before selection:

- Training annotations were checked.
- 5,942 bounding boxes were found in the training set.
- All annotation lines followed the expected YOLO format.
- No invalid annotation lines were found.
- Sample training images were visually inspected.
- Sample validation images were visually inspected.
- Bounding boxes were generally aligned with the visible potholes.

## Reported Reference Results

A publicly available Kaggle notebook using this dataset reported:

- mAP@50: 78.90%
- mAP@50-95: 52.26%
- Precision: 81.21%
- Recall: 69.92%
- F1 Score: 75.14%

These results are reported results from an external Kaggle notebook and are not the final results of our project.

## Why It Was Selected

- Specifically designed for pothole detection.
- Contains YOLO-format object-detection annotations.
- Contains a pothole-only class.
- Suitable for YOLO-based object detection models.
- Dataset structure is compatible with the current project requirements.

## Status

Selected as the Kaggle candidate.

Final dataset selection will be made after comparison with the Roboflow candidate.

## Dataset Storage

The original dataset is not stored in this repository because of its large size.

The dataset was downloaded locally for verification and analysis. It will be used for model development after the final dataset is selected.
