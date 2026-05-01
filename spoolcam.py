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
TRIGGER_PIN = 23
LED_PIN = 25
RESOLUTION = (640, 480)
################################

def main():

    def getVidTitle() -> str: return f"{SPOOL_VIDS_PATH}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mkv"
    
    os.makedirs(SPOOL_VIDS_PATH, exist_ok=True)

    # Camera setup
    cam = Picamera2()
    config = cam.create_video_configuration(main={'size': RESOLUTION, 
                                                  'format' :'YUV420'})
    cam.configure(config)

    # GPIO SETUP
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIGGER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(LED_PIN, GPIO.OUT)
            
    try:
        # main loop
        while(True):
            
            # if its high, start 
            if GPIO.input(TRIGGER_PIN):
                
                # Start the video if needed
                if not started_vid:
                    output = PyavOutput(getVidTitle(), format='matroska') # Reset vid title
                    encoder = H264Encoder(bitrate=10000000)
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

            time.sleep(0.1) # Avoid Hammering 
    finally:

        if started_vid:
            cam.stop_recording()
        
        cam.close()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
