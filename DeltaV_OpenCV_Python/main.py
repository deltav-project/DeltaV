#!/usr/bin/python3

from frame import FrameResizer
from sys import argv
import board
from neopixel import NeoPixel, GRB


# Reads /dev/video device index from first command line argument
dev_index = int(argv[1])
# Framerate is second command line argument
framerate = int(argv[2])
# Width from 3rd argument
width = int(argv[3])
# Height for 4th argument
height = int(argv[4])
# Get pin id for plugged led strip
pin = argv[5]

framerate_logging = "--show-fps" in argv  # show-fps option enable framerate informations logging


class LedstripUpdater:
    """Callable object which updates given ledstrip with top pixels array from resized frame"""

    def __init__(self, ledstrip: NeoPixel):
        self.ledstrip = ledstrip

    def updateBorder(self, border, leds_array_begin: int): int:
        """Takes given border and draw LEDS from leds_array_begin until there is no more color in border, or no more LEDs to update"""

        leds_count = self.ledstrip.n
        border_len = len(border)
        color_i = 0

        while color_i < border_len and leds_array_begin + color_i < leds_count:
            self.ledstrip[leds_array_begin + color_i] = border[color_i]
            color_i += 1

    def __call__(self, borders):
        """Take top border from given arrays to adjust ledstrip LEDs, filling with black if required"""

        (top, bottom, left, right) = borders

        self.updateBorder(0, top)
        self.updateBorder(16, right)
        self.updateBorder(25, bottom)
        self.updateBorder(41, left)


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
