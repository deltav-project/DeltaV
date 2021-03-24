#!/usr/bin/python3

import numpy as np
import cv2 as cv
from sys import argv
import time

# Reads /dev/video device index from first command line argument
dev_index = int(argv[1])
# Framerate is second command line argument
framerate = int(argv[2])
# Width from 3rd argument
width = int(argv[3])
# Height for 4th argument
height = int(argv[4])

framerate_logging = "--show-fps" in argv  # show-fps option enable framerate informations logging

unlimited_framerate = framerate == 0  # 0fps enable unlimited fps mode
if not unlimited_framerate:  # Avoid ArithmeticError with div by 0
    framerate_delay_s = 1 / framerate  # Delay expected between each frames (main loop iteration)
else:
    framerate_delay_s = -1  # Time remaining before next frame checks for positive delay, set to negative

# First try to open video capture from camera device /dev/video{device}
print("Creating video capture...")
video = cv.VideoCapture(dev_index)
print("Created video capture:", video)

while not video.isOpened():  # While camera is device is not opened
    print("Opening capture...")
    video.open(dev_index)  # Tries again to get video capture from device

print("Opened.")

last_frame = time.time()  # First frame will have null duration

while True:
    image_handling_begin = time.time()  # Save image handling begin timestamp

    if framerate_logging:  # show-fps option enable frame informations
        duration = image_handling_begin - last_frame

        if duration != 0:  # Don't care about first frame (null duration)
            print(f"Estimate framerate: {1 / duration}fps /// Last frame duration: {duration}s")

        last_frame = image_handling_begin

    received, frame = video.read()  # Reads and waits for next captured frame
    if not received:  # No longer signal received from device, stops
        print("No signal from video stream.")
        break

    frame_resized = cv.resize(frame, (width, height))
    if height > 1:  # we make sure that we can find left and right pixels
        array_top_pixels = frame_resized[0]  # top pixels are the first row of the frame
        array_left_pixels = np.zeros((height-2, 3), dtype=np.uint8)  # initialization of left pixels array with zeros and the right shape
        array_right_pixels = np.zeros((height-2, 3), dtype=np.uint8)  # same for right pixels array
        for i in range(1, height-1, 1):
            array_left_pixels[i-1] = frame_resized[i][0]  # left pixels are the first pixels of each row in the frame (except the first and last row)
            array_right_pixels[i-1] = frame_resized[i][width-1]  # same but they are the last
        array_bottom_pixels = frame_resized[height-1]  # bottom pixels are the last row of the frame
    else:  # otherwise  everything in the same as the top pixels (the first row in the frame)
        array_top_pixels = frame_resized[0]
        array_left_pixels, array_right_pixels, array_bottom_pixels = array_top_pixels, array_top_pixels, array_top_pixels

    image_handling_duration = time.time() - image_handling_begin  # Save image handling duration
    remaining_frame_delay_s = framerate_delay_s - image_handling_duration  # Remaining time to wait is expected time minus time spent to handle image

    if not unlimited_framerate and remaining_frame_delay_s > 0:  # Wait if and only if framerate should be limited
        time.sleep(remaining_frame_delay_s)  # Wait time remaining before next frame should be handled
