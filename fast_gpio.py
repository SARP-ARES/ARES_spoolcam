from picamera2 import Picamera2
from signal import pause
import datetime
import threading
import os
import time

# ================= Configuration =================
BASE_DIR = "./spoolvids"
RESOLUTION = (320, 240)
CAPTURE_INTERVAL = 1 / 25      # 25 FPS
CHUNK_DURATION = 10 * 60       # 10 minutes per folder
SOFTWARE_TEST_MODE = False
GPIO_PIN = 17
# ================================================

os.makedirs(BASE_DIR, exist_ok=True)

picam2 = Picamera2()
config = picam2.create_still_configuration(
    main={"size": RESOLUTION},
    buffer_count=4
)
picam2.configure(config)
picam2.start()

recording = False
recording_lock = threading.Lock()
current_chunk_start = None
current_chunk_dir = None

def new_chunk_dir():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(BASE_DIR, f"chunk_{ts}")
    os.makedirs(path, exist_ok=True)
    return path

def start_recording():
    global recording, current_chunk_start, current_chunk_dir
    with recording_lock:
        if recording:
            return
        current_chunk_dir = new_chunk_dir()
        current_chunk_start = time.time()
        recording = True
        print(f"Recording started ? {current_chunk_dir}")

def stop_recording():
    global recording
    with recording_lock:
        if not recording:
            return
        recording = False
        print("Recording stopped")

def capture_loop():
    frame = 0
    while True:
        time.sleep(CAPTURE_INTERVAL)
        with recording_lock:
            if not recording:
                continue

            elapsed = time.time() - current_chunk_start
            if elapsed >= CHUNK_DURATION:
                print("Chunk duration reached ? rotating folder")
                start_recording()

            filename = os.path.join(
                current_chunk_dir,
                f"frame_{frame:06d}.jpg"
            )
            picam2.capture_file(filename)
            frame += 1

def software_test():
    try:
        while True:
            start_recording()
            time.sleep(5)
            stop_recording()
            time.sleep(3)
    except KeyboardInterrupt:
        pass

threading.Thread(target=capture_loop, daemon=True).start()

if SOFTWARE_TEST_MODE:
    software_test()
else:
    from gpiozero import Button
    trigger = Button(GPIO_PIN, pull_up=False, bounce_time=0.05)
    trigger.when_pressed = start_recording
    trigger.when_released = stop_recording
    pause()
