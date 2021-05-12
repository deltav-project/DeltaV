#!/usr/bin/python3 -u

from frame import FrameResizer, BrightnessFilter
from sys import argv
import board
from neopixel import NeoPixel, GRB
import signal


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
# HSV V value in percentage to use as threshold for filter
threshold = float(argv[6])

framerate_logging = "--show-fps" in argv  # show-fps option enable framerate informations logging


class LedstripUpdater:
    """Callable object which updates given ledstrip with top pixels array from resized frame"""

    def __init__(self, ledstrip: NeoPixel):
        self.ledstrip = ledstrip
        self.next_led = 0  # Will go from 0 to ledstrip.n, then go back to 0

    def showSegment(self, pixels_array):
        """Increases next_led of given pixels array length and color these LEDs with given color codes"""

        for i in range(len(pixels_array)):
            # Colors next LED inside ledstrip
            self.ledstrip[self.next_led] = pixels_array[i]
            # Go to next LED
            self.next_led += 1

            # If all LEDs were colored, go back to the beginning of the ledstrip
            if self.next_led == self.ledstrip.n:
                self.next_led = 0

    def __call__(self, borders):
        """Take top border from given arrays to adjust ledstrip LEDs, filling with black if required"""

        left_array = borders[2]
        top_array = borders[0]
        right_array = borders[3]
        bottom_array = borders[1]

        bot_len = len(bottom_array)

        self.showSegment(bottom_array[:1])
        self.showSegment(left_array)
        self.showSegment(top_array)
        self.showSegment(right_array)
        self.showSegment(bottom_array[bot_len-1:bot_len])

        self.ledstrip.show()


def print_borders(borders):  # Prints resized frame borders
    for pixels_array in borders:
        print(pixels_array)


def do_nothing(borders):  # Don't do anything on resized frame
    pass


pin_value = getattr(board, pin)  # Get pin variable from board module depending on pin id argument

print("Connect to ledstrip...")
with NeoPixel(pin_value, leds, pixel_order=GRB, auto_write=False) as ledstrip:  # with statement ensures ledstrip is clean when program stops (SIGKILL case unhandled)
    update_ledstrip = LedstripUpdater(ledstrip)  # Generate function for ledstirp updating from callable class with __call__()
    filter_pixels = BrightnessFilter(threshold, update_ledstrip)

    resizer = FrameResizer(framerate, width, height)

    def stop(received_signal: int, _):
        print(f"Stopped by signal {received_signal}")
        resizer.stop_resize()

    signal.signal(signal.SIGTERM, stop)  # Handle SIGTERM by systemd to stop resizing operations
    resizer.start_resize(filter_pixels, framerate_logging)
