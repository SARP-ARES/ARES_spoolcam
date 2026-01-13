import cv2
import glob
import os

# Target framerate
FPS = 30

for mjpeg_file in glob.glob("*.mjpeg"):
    mp4_file = os.path.splitext(mjpeg_file)[0] + ".mp4"

    # Open the MJPEG file
    cap = cv2.VideoCapture(mjpeg_file)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Setup VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 codec
    out = cv2.VideoWriter(mp4_file, fourcc, FPS, (width, height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()
    out.release()
    print(f"Converted {mjpeg_file} → {mp4_file}")
