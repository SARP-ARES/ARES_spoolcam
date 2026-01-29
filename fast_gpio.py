from picamera2 import Picamera2
from gpiozero import Button, LED
import threading
import time
import os
import datetime
from signal import pause

# ================= Configuration =================
IMAGE_DIR = "./spoolvids"
RESOLUTION = (640, 480)
CAPTURE_FPS = 20
GPIO_TRIGGER = 17
GPIO_LED = 26
# ================================================

os.makedirs(IMAGE_DIR, exist_ok=True)

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": RESOLUTION})
picam2.configure(config)
picam2.start()

trigger = Button(GPIO_TRIGGER, pull_up=False)
led = LED(GPIO_LED)

recording = False
recording_lock = threading.Lock()
frame_thread = None
led_thread = None
stop_event = threading.Event()

def led_blink_loop():
    while not stop_event.is_set():
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)
    led.off()

def capture_loop(folder):
    frame = 0
    interval = 1.0 / CAPTURE_FPS

    while not stop_event.is_set():
        filename = os.path.join(folder, f"frame_{frame:06d}.jpg")
        picam2.capture_file(filename)
        frame += 1
        time.sleep(interval)

def start_recording():
    global recording, frame_thread, led_thread

    with recording_lock:
        if recording:
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = os.path.join(IMAGE_DIR, f"run_{timestamp}")
        os.makedirs(folder, exist_ok=True)

        stop_event.clear()

        frame_thread = threading.Thread(target=capture_loop, args=(folder,), daemon=True)
        led_thread = threading.Thread(target=led_blink_loop, daemon=True)

        frame_thread.start()
        led_thread.start()

        recording = True
        print(f"Recording started: {folder}")

def stop_recording():
    global recording

    with recording_lock:
        if not recording:
            return

        stop_event.set()
        time.sleep(0.2)  # allow threads to exit cleanly
        recording = False
        print("Recording stopped")

trigger.when_pressed = start_recording
trigger.when_released = stop_recording

print("System ready. Waiting for trigger...")
pause()
