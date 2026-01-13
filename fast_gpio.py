from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from signal import pause
import datetime
import threading
import os
import time

# ================= Configuration =================
VIDEO_DIR = "./spoolvids"          # Directory to save MJPEGs
RESOLUTION = (320, 240)            # Low res for max FPS
CHUNK_DURATION = 10 * 60           # seconds per MJPEG file (10 min)
SOFTWARE_TEST_MODE = False          # True = simulate GPIO triggers
TRIGGER_DURATION = 5                # seconds per simulated trigger
WAIT_BETWEEN = 3                    # seconds between simulated triggers
GPIO_PIN = 17                       # GPIO pin for real trigger
# ================================================

# Ensure save directory exists
os.makedirs(VIDEO_DIR, exist_ok=True)

# Initialize camera
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": RESOLUTION}, buffer_count=4)
picam2.configure(video_config)
picam2.start()  # Start camera before recording

# Recording state
recording_lock = threading.Lock()
recording = False
encoder = None
current_file_start_time = None

# ================== Recording Functions ==================
def get_new_filename():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{VIDEO_DIR}/video_{timestamp}.mjpeg"

def start_recording():
    """Start recording a new MJPEG video."""
    global recording, encoder, current_file_start_time
    with recording_lock:
        if recording:
            return
        filename = get_new_filename()
        encoder = MJPEGEncoder()  # NEW encoder per recording
        try:
            picam2.start_recording(encoder, filename)
        except Exception as e:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Failed to start recording: {e}")
            return  # exit without setting recording = True
        current_file_start_time = time.time()
        recording = True
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Recording started: {filename}")
        time.sleep(0.05)  # ensure first frame captured

def stop_recording():
    global recording
    with recording_lock:
        if not recording:
            return
        picam2.stop_recording()
        recording = False
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Recording stopped")

def check_chunk_duration():
    """If recording exceeds CHUNK_DURATION, stop and start new file."""
    global recording
    while True:
        time.sleep(1)
        with recording_lock:
            if recording and current_file_start_time is not None:
                elapsed = time.time() - current_file_start_time
                if elapsed >= CHUNK_DURATION:
                    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Chunk duration reached. Splitting file...")
                    stop_recording()
                    start_recording()

# ================== Main ==================
if SOFTWARE_TEST_MODE:
    print("SOFTWARE TEST MODE: Simulating trigger...")
    try:
        # Start chunk checker thread
        threading.Thread(target=check_chunk_duration, daemon=True).start()
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
    trigger = Button(GPIO_PIN, pull_up=False, bounce_time=0.05)
    trigger.when_pressed = start_recording
    trigger.when_released = stop_recording
    # Start chunk checker thread
    threading.Thread(target=check_chunk_duration, daemon=True).start()
    print(f"GPIO trigger mode enabled on pin {GPIO_PIN}. Waiting for triggers...")
    pause()

