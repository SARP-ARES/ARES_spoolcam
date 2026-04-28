import os
import RPi.GPIO as GPIO
import time
import threading

################################
SPOOL_VIDS_PATH = '../spoolvids'
TRIGGER_PIN = 0 #needs change
################################

def main():
    
    os.makedirs(SPOOL_VIDS_PATH, exist_ok=True)

    # GPIO SETUP
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIGGER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # Threading overhead
    recording = threading.Event()
    started_vid = False

    def poll_GPIO():

        while(True):

            if GPIO.input(TRIGGER_PIN):
                recording.set()
            else:
                recording.clear()
            
            time.sleep(0.5) # Sleep for half second
    
    # Threading overhead
    updater = threading.Thread(target=poll_GPIO)
    updater.start()

    # main loop
    while(True):

        if recording.is_set():
            if started_vid:
                #implement video running logic
                pass
            else: 
                #implement start video logic
                pass
        else:
            started_vid = False

    updater.join()

if __name__ == "__main__":
    main()
