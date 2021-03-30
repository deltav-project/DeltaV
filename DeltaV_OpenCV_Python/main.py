#!/usr/bin/python3

from frame import FrameResizer
from sys import argv


def print_borders(borders):  # Prints resized frame borders
    for pixels_array in borders:
        print(pixels_array)


def do_nothing(borders):  # Don't do anything on resized frame
    pass


# Reads /dev/video device index from first command line argument
dev_index = int(argv[1])
# Framerate is second command line argument
framerate = int(argv[2])
# Width from 3rd argument
width = int(argv[3])
# Height for 4th argument
height = int(argv[4])

framerate_logging = "--show-fps" in argv  # show-fps option enable framerate informations logging

resizer = FrameResizer(dev_index, framerate, width, height)
resizer.start_resize(do_nothing, framerate_logging)
