
Spoolcam is configured to run its python script (spoolcam.py) on startup. 

**Script Logic**
-

 - Poll trigger pin if high, enter recording, if low exit recording

 - If camera is in recording state

	- If video is not started
		Start the video 
		Turn on recording LED

	- If the video is started
		pass

 - If camera is not in recording state
	
	- If video was running
		End the Video
		Turn off recording LED

	- If video was not running 
		pass

**User Guide**
-

Plug in the device. Provide a 3.3V supply to GPIO 4 to start recording. The external LED
will light up when the recording has started. To end the recording, lower power to that GPIO pin
and the recording will stop, the external LED will turn off to verify this behavior. 

Videos will be marked with a timestamp of when they started. To retrieve all videos from the pi run this command
(assuming you are connected to the pi through gadget mode). 

scp -r ares@ares.local:~/spoolvids/ <insert-target-directory>

This will prompt the password for the device, which is ares
All spoolcam videos will then be moved to the target directory. 

If the spoolcam begins to run out of storage. Collect all videos with the above command, and then run 

ssh ares@ares.local "cd ~; rm -rf ./spoolvids/"

This will ssh on to the board and clear all existing videos.

**GPIO MAP**
-
Purpose | Pin Num
Trigger | 23
LED 	| 25 
