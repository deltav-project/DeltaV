import numpy as np
import cv2 as cv
from time import time, sleep


class FrameResizer:
    """Open a VideoCapture stream, then read and resize each frame, calls given handler for each received frame"""

    def __init__(self, device_index: int, framerate: int, resized_w: int, resized_h: int):
        """Makes VideoCapture stream from given /dev/ index, framerate is FPS, resized ints are pixels"""

        self.device_index = device_index  # Might be reused if first try to open video capture stream failed

        # Open video stream
        print("Opening video capture stream...")
        self.stream = cv.VideoCapture(device_index)

        # Save video config
        self.framerate = framerate
        self.resized_frame_dims = (resized_w, resized_h)

        if self.framerate == 0:  # 0 FPS means unlimited framerate
            self.limited_framerate = False
            self.frame_delay_s = 0  # No delay between frames if framerate isn't limited
        else:
            self.limited_framerate = True
            self.frame_delay_s = 1 / self.framerate  # Calculate exact expected delay between each frame

    def await_stream(self) -> None:
        """Blocks until video capture stream has been successfully open"""

        tries = 1  # Number of stream.open() calls tried

        while not self.stream.isOpened():
            tries += 1
            print(f"Opening video capture stream... Try {tries}")

            self.stream.open(self.device_index)

        print("Video capture stream open.")

    def get_borders(self, resized_frame):
        """Retrieves top, bottom, left and right borders for given resized frame"""

        width, height = self.resized_frame_dims  # Get resized frame configuration dimensions, first value is w, second value is width

        if height > 1:  # we make sure that we can find left and right pixels
            array_top_pixels = resized_frame[0]  # top pixels are the first row of the frame
            array_left_pixels = np.zeros((height-2, 3), dtype=np.uint8)  # initialization of left pixels array with zeros and the right shape
            array_right_pixels = np.zeros((height-2, 3), dtype=np.uint8)  # same for right pixels array

            for i in range(1, height-1, 1):
                # left pixels are the first pixels of each row in the frame (except the first and last row)
                array_left_pixels[i-1] = resized_frame[i][0]
                # same but they are the last
                array_right_pixels[i-1] = resized_frame[i][width-1]

            array_bottom_pixels = resized_frame[height-1]  # bottom pixels are the last row of the frame
        else:  # otherwise everything in the same as the top pixels (the first row in the frame)
            array_top_pixels = resized_frame[0]
            array_left_pixels, array_right_pixels, array_bottom_pixels = array_top_pixels, array_top_pixels, array_top_pixels

        return array_top_pixels, array_bottom_pixels, array_left_pixels, array_right_pixels

    def start_resize(self, on_frame: "function", framerate_logging: bool = False):
        """Resizes each received frame from video capture stream.
        For each frame, calls given function taking 4 arrays parameter : top pixels, bottom pixels, left pixels and right pixels"""

        last_frame_handling = time()  # First previous frame handling will have null duration

        while True:
            frame_handling_begin = time()

            if framerate_logging:
                duration_s = frame_handling_begin - last_frame_handling  # Save difference in seconds between two frame resize operations

                if duration_s != 0:  # Don't care about null duration resize
                    print(f"Estimate framerate: {1 / duration_s}fps /// Last frame duration: {duration_s}s")

                last_frame_handling = frame_handling_begin  # Only keep last frame resize timestamp to compare with next frame if framerate is logged

            valid, frame = self.stream.read()  # Read next frame, if successfully read
            if not valid:  # Signal stopped, useless to continue reading next frames
                print("No signal from video stream, stop resizing operations.")
                break

            resized_frame = cv.resize(frame, self.resized_frame_dims)  # Do resizing operation
            resized_frame_borders = self.get_borders(resized_frame)  # Get borders algorithm

            on_frame(resized_frame_borders)

            frame_handling_duration = time() - frame_handling_begin  # Time took in seconds to handle current frame
            remaining_before_next = self.frame_delay_s - frame_handling_duration  # Calculate remaing seconds before next frame

            if self.limited_framerate and remaining_before_next > 0:  # Don't sleep if late for next frame
                sleep(remaining_before_next)
