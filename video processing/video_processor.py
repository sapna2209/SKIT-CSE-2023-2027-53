import cv2
import os

# Input video path
video_path = r"D:\YOLOV8\sample_video.mp4"

# Output folder
output_dir = r"D:\YOLOV8\output_frames"

# Create output folder
os.makedirs(output_dir, exist_ok=True)

# Open video
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Cannot open video.")
    exit()

# Read video properties
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

if fps <= 0:
    cap.release()
    raise ValueError("Invalid video FPS")

duration = total_frames / fps

print("Video FPS:", fps)
print("Total Frames:", total_frames)
print("Video Duration:", duration, "seconds")

# Extract one frame per second
interval_seconds = 1
frame_interval = round(fps * interval_seconds)

frame_number = 0
saved_frames = 0

while True:
    success, frame = cap.read()

    if not success:
        break

    if frame_number % frame_interval == 0:
        filename = f"frame_{frame_number}.jpg"
        output_path = os.path.join(output_dir, filename)

        if cv2.imwrite(output_path, frame):
            saved_frames += 1
            print("Saved:", filename)
        else:
            print("Failed to save:", filename)

    frame_number += 1

cap.release()

print("\nFrame extraction completed!")
print("Total frames processed:", frame_number)
print("Frames saved:", saved_frames)
print("Output folder:", output_dir)