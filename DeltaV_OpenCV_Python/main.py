#!/usr/bin/python

import numpy as np
import cv2 as cv
from sys import argv
import ffmpeg


# Reads /dev/video device index from first command line argument
dev_index = int(argv[1])
# Framerate is 1000ms / (second command line argument)
framerate = 1000 // int(argv[2])

# Starts ffmpeg background process
# Streaming from ":0.0" (for currently running X11 display server) with x11grab
# To "/dev/video{device_index}" with v4l2
streaming = ffmpeg \
    .input(":0.0", f="x11grab", s="1920x1080", r=framerate) \
    .output(f"/dev/video{dev_index}", f="v4l2").run_async()


# First try to open video capture from v4l2 device /dev/video{device}
video = cv.VideoCapture(dev_index)

# As ffmpeg is background process, it might not be running at this point, so
# v4l2 device may not be open.
while not video.isOpened():  # While v4l2 device haven't been opened by ffmpeg
    video.open(dev_index)  # Tries again to get video capture from device

while True:
    received, frame = video.read()  # Reads and waits for next captured frame
    # squared = cv.resize(received, (320, 180)) Doesn't work for now

    if not received:  # No longer signal received from device, stops
        print("No signal from video stream.")
        break

    # Shows current captured frame to screen
    cv.imshow("Screen capture", received)

    if cv.waitKey(framerate) == ord("q"):  # Leaves program when "q" is pressed
        break

cv.destroyAllWindows()  # OpenCV windows gone, end of program
streaming.terminate()  # Stops ffmpeg background process (sending SIGTERM)
