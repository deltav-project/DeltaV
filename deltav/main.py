#!/usr/bin/python3

from frame import FrameResizer
from sys import argv
import board
from neopixel import NeoPixel, GRB


# Framerate is second command line argument
framerate = int(argv[1])
# Width from 3rd argument
width = int(argv[2])
# Height for 4th argument
height = int(argv[3])
# Number of leds on plugged led strip
leds = int(argv[4])
# Get pin id for plugged led strip
pin = argv[5]

framerate_logging = "--show-fps" in argv  # show-fps option enable framerate informations logging


class LedstripUpdater:
    """Callable object which updates given ledstrip with top pixels array from resized frame"""

    def __init__(self, ledstrip: NeoPixel):
        self.ledstrip = ledstrip

    def __call__(self, borders):
        """Take top border from given arrays to adjust ledstrip LEDs, filling with black if required"""

        top_array = borders[0]
        leds_to_color = min(len(top_array), self.ledstrip.n)  # Color LED while there is still LEDs and there is still pixel to show

        for i in range(leds_to_color):
            self.ledstrip[i] = top_array[i]

        for i in range(leds_to_color, self.ledstrip.n):  # Color remaining LEDS (if any) in black
            self.ledstrip[i] = (0, 0, 0)


def print_borders(borders):  # Prints resized frame borders
    for pixels_array in borders:
        print(pixels_array)


def do_nothing(borders):  # Don't do anything on resized frame
    pass


pin_value = getattr(board, pin)  # Get pin variable from board module depending on pin id argument

with NeoPixel(pin_value, leds, pixel_order=GRB) as ledstrip:  # with statement ensures ledstrip is clean when program stops (SIGKILL case unhandled)
    update_ledstrip = LedstripUpdater(ledstrip)  # Generate function for ledstirp updating from callable class with __call__()

    resizer = FrameResizer(dev_index, framerate, width, height)
    resizer.start_resize(update_ledstrip, framerate_logging)
