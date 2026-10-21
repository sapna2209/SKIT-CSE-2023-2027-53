import os
import sys
import cv2
from ultralytics import YOLO

# --------------------------------------------------
# 1. Paths and configuration
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

MODEL_PATH = os.path.join(PROJECT_ROOT, "best.pt")
VIDEO_PATH = os.path.join(PROJECT_ROOT, "sample_video.mp4")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "pothole_detected_video.mp4")

DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")

sys.path.insert(0, DATABASE_DIR)
from db_manager import DatabaseManager

def main():

    # --------------------------------------------------
    # 2. Validate input files
    # --------------------------------------------------

    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found: {MODEL_PATH}")
        return

    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Input video not found: {VIDEO_PATH}")
        return

    # --------------------------------------------------
    # 3. Load YOLO model
    # --------------------------------------------------

    print("Loading YOLO model...")
    model = YOLO(MODEL_PATH)

    print("Model classes:", model.names)

    # --------------------------------------------------
    # 4. Open input video
    # --------------------------------------------------

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        print("Error: Could not open input video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if fps <= 0:
        fps = 25.0
        print("Warning: Could not read FPS. Using 25 FPS.")

    duration = total_frames / fps if total_frames > 0 else 0

    print("\nInput video information:")
    print("FPS:", fps)
    print("Total frames:", total_frames)
    print("Duration:", round(duration, 2), "seconds")
    print("Resolution:", width, "x", height)

    # --------------------------------------------------
    # 5. Initialize database
    # --------------------------------------------------

    db = DatabaseManager()

    video_id = db.insert_video(
        filename=os.path.basename(VIDEO_PATH),
        fps=fps,
        total_frames=total_frames,
        duration_sec=duration
    )

    print("\nVideo metadata saved in database.")
    print("Video ID:", video_id)

    # --------------------------------------------------
    # 6. Create output video writer
    # --------------------------------------------------

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    out = cv2.VideoWriter(
        OUTPUT_PATH,
        fourcc,
        fps,
        (width, height)
    )

    if not out.isOpened():
        cap.release()
        print("Error: Could not create output video.")
        return

    # --------------------------------------------------
    # 7. Detect potholes and save detections
    # --------------------------------------------------

    frame_number = 0
    total_detections_saved = 0

    print("\nStarting video processing...\n")

    try:
        while True:

            ret, frame = cap.read()

            if not ret:
                break

            # Run YOLO on the current frame
            results = model.predict(
                source=frame,
                conf=CONFIDENCE_THRESHOLD,
                verbose=False
            )

            result = results[0]

            # Save detected bounding boxes and confidence
            # scores in the existing SQLite database.
            saved_count = db.insert_from_yolo_result(
                video_id=video_id,
                frame_number=frame_number,
                fps=fps,
                result=result,
                frame_image_path=None,
                min_conf=CONFIDENCE_THRESHOLD
            )

            total_detections_saved += saved_count

            # Draw YOLO bounding boxes on the frame
            annotated_frame = result.plot()

            # Write the annotated frame to output video
            out.write(annotated_frame)

            frame_number += 1

            if frame_number % 50 == 0:
                print(
                    f"Processed {frame_number}/{total_frames} frames | "
                    f"Detections saved: {total_detections_saved}"
                )

    finally:
        # Release video resources even if an error occurs
        cap.release()
        out.release()

    # --------------------------------------------------
    # 8. Display final summary
    # --------------------------------------------------

    print("\n------------------------------------")
    print("VIDEO PROCESSING COMPLETED")
    print("------------------------------------")

    print("Input video:", VIDEO_PATH)
    print("Output video:", OUTPUT_PATH)
    print("Frames processed:", frame_number)
    print("Detections saved:", total_detections_saved)
    print("Database video ID:", video_id)

    print("\nCheck your database here:")
    print(os.path.join(DATABASE_DIR, "potholes.db"))

    print("\nOpen the output video to see the detected potholes.")


if __name__ == "__main__":
    main()
