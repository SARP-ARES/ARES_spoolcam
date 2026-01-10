from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from signal import pause
import datetime
import threading
import os
import time

# ================= Configuration =================
VIDEO_DIR = "./spoolvids"        # Saves in current folder; no permission issues
RESOLUTION = (320, 240)       # Low resolution for max FPS
SOFTWARE_TEST_MODE = True      # True = simulate GPIO trigger, False = use real GPIO
TRIGGER_DURATION = 5           # seconds recording in software test mode
WAIT_BETWEEN = 3               # seconds between simulated triggers
# ================================================

# Ensure save directory exists
os.makedirs(VIDEO_DIR, exist_ok=True)

# Initialize camera
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": RESOLUTION}, buffer_count=4)
picam2.configure(video_config)

# Recording state
recording_lock = threading.Lock()
recording = False
encoder = MJPEGEncoder()  # MJPEG for high FPS

def start_recording():
    global recording
    with recording_lock:
        if recording:
            return
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{VIDEO_DIR}/video_{timestamp}.mjpeg"
        picam2.start_recording(encoder, filename)
        recording = True
        print(f"Recording started: {filename}")

def stop_recording():
    global recording
    with recording_lock:
        if not recording:
            return
        picam2.stop_recording()
        recording = False
        print("Recording stopped")

# ================== Main ==================
if SOFTWARE_TEST_MODE:
    print("SOFTWARE TEST MODE: Simulating trigger...")
    try:
        while True:
            print("Simulating trigger HIGH")
            start_recording()
            time.sleep(TRIGGER_DURATION)
            print("Simulating trigger LOW")
            stop_recording()
            time.sleep(WAIT_BETWEEN)
    except KeyboardInterrupt:
        print("Test stopped by user")

else:
    # Real GPIO trigger mode
    from gpiozero import Button
    GPIO_PIN = 17
    trigger = Button(GPIO_PIN, pull_up=False)
    trigger.when_pressed = start_recording
    trigger.when_released = stop_recording
    pause()
