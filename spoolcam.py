import os
import RPi.GPIO as GPIO
import time
import threading
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import PyavOutput
from datetime import datetime

################################
SPOOL_VIDS_PATH = '../spoolvids'
TRIGGER_PIN = 4
LED_PIN = 26
RESOLUTION = (640, 480)
################################

def main():

    def getVidTitle() -> str: return f'{SPOOL_VIDS_PATH}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4'
    
    os.makedirs(SPOOL_VIDS_PATH, exist_ok=True)

    # Camera setup
    cam = Picamera2()
    config = cam.create_video_configuration(main={'size': RESOLUTION, 
                                                  'format' :'YUV420'})
    cam.configure(config)
    encoder = H264Encoder(bitrate=10000000)

    # GPIO SETUP
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIGGER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(LED_PIN, GPIO.OUT)
        
    # Polls the trigger pin to verify if the trigger pin is still high
    # sets teh recording event if high, clears if low 
    def poll_GPIO():
        while(True):
            
            # Start video if video pin is high
            if GPIO.input(TRIGGER_PIN):
                recording.set()
            else:
                recording.clear()    

            time.sleep(0.5) # Sleep for half second
    
    # Threading overhead
    recording = threading.Event()
    started_vid = False
    updater = threading.Thread(target=poll_GPIO)
    updater.start()

    # main loop
    while(True):

        if recording.is_set():
            
            # Start the video if needed
            if not started_vid:
                output = PyavOutput(getVidTitle()) # Reset vid title
                cam.start_recording(encoder, output)
                started_vid = True

                # Turn the video LED on
                GPIO.output(LED_PIN, GPIO.HIGH)

            # Pass if otherwise

        else:

            # end video if video pin is now low
            if started_vid:
                cam.stop_recording()
                
                # Turn off the video LED
                GPIO.output(LED_PIN, GPIO.LOW)

            started_vid = False
    
    # This is never reached, which is ok, break logic is fragile for usecase
    updater.join()

if __name__ == "__main__":
    main()
