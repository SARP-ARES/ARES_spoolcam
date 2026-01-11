# spoolcam

Python code, setup instructions, and MJPEG to MP4 code for spoolcam setup in case of necessary re-imaging/re-flashing.

fast_gpio.py is the Python code for the spool cam recording saved in test mode. Turn test mode off for the GPIO-enabled trigger

convert_mjpeg_to_mp4.py is the Python code to convert MJPEG files to MP4 (on laptop)

spoolcam_start_on_power_on.me has the setup instructions to enable fast_gpio.py to start when the Raspberry Pi is powered on.

on power up, immediately run (in bash): sudo systemctl stop spoolcam.service
Or else it'll keep recording on 10-second clips and take up a bunch of the memory

Also to check the recording status, run (in bash): sudo systemctl status spoolcam.service
Make sure it is inactive before doing anything else with the rspberry pi

