#!/usr/bin/python

import numpy as np
import cv2 as cv
from sys import argv


# Reads /dev/video device index from first command line argument
dev_index = int(argv[1])
# Framerate is 1000ms / (second command line argument)
framerate = 1000 // int(argv[2])
# Width from 3rd argument
width = int(argv[3])
# Height for 4th argument
height = int(argv[4])

# First try to open video capture from v4l2 device /dev/video{device}
video = cv.VideoCapture(dev_index)

# As ffmpeg is background process, it might not be running at this point, so
# v4l2 device may not be open.
while not video.isOpened():  # While v4l2 device haven't been opened by ffmpeg
    video.open(dev_index)  # Tries again to get video capture from device

while True:
    received, frame = video.read()  # Reads and waits for next captured frame
    squared = cv.resize(frame, (width, height))

    if not received:  # No longer signal received from device, stops
        print("No signal from video stream.")
        break

    print(squared)
