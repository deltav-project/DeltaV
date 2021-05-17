import numpy as np
import cv2 as cv
from time import time, sleep


def to_rgb(pixels_array):
    """Copies given OpenCV BGR pixels array to RGB pixels array"""

    # Creates RGB pixel arrays with same size than original given array
    rgb_pixels_array = np.zeros((len(pixels_array), 3), dtype=np.uint8)

    # For each pixel in original array
    for i in range(len(pixels_array)):
        (blue, green, red) = pixels_array[i]  # Retrieves colors provided by OpenCV using BGR order

        rgb_pixels_array[i] = np.array([red, green, blue])  # Copies to new array using RGB order

    return rgb_pixels_array


class FrameResizer:
    """Open a VideoCapture stream, then read and resize each frame, calls given handler for each received frame"""

    def __init__(self, framerate: int, resized_w: int, resized_h: int):
        """Makes VideoCapture stream from /dev/capture-card, framerate is FPS, resized ints are pixels"""

        self.device_path = "/dev/video0"  # Might be reused if first try to open video capture stream failed
        self.running = False  # Wait for start_resize() call

        # Open video stream
        print("Opening video capture stream...")
        self.stream = cv.VideoCapture(self.device_path)

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

            self.stream.open(self.device_path)

        print("Video capture stream open.")

    def get_borders(self, resized_frame):
        """Retrieves top, bottom, left and right borders for given resized frame, using RGB order"""

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

        # Converts each border pixels array to RGB
        return to_rgb(array_top_pixels), to_rgb(array_bottom_pixels), to_rgb(array_left_pixels), to_rgb(array_right_pixels)

    def start_resize(self, on_frame: "function", framerate_logging: bool = False):
        """Resizes each received frame from video capture stream.
        For each frame, calls given function taking 4 arrays parameter : top pixels, bottom pixels, left pixels and right pixels"""

        last_frame_handling = time()  # First previous frame handling will have null duration

        with open("/home/deltav/logging.log", "a") as logging:
            self.running = True
            while self.running:
                frame_handling_begin = time()

                if framerate_logging:
                    duration_s = frame_handling_begin - last_frame_handling  # Save difference in seconds between two frame resize operations

                    if duration_s != 0:  # Don't care about null duration resize
                        message = f"Estimate framerate: {1 / duration_s}fps /// Last frame duration: {duration_s}s"
                        print(message)
                        logging.write(message + "\n")

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

    def stop_resize(self):
        """Stop resizing operation started with start_resize(), can be called even if no resizing is running"""

        self.running = False


class ColorsFilter:
    """Callable object setting to black pixels which haven't a sufficiently high value inside
    HSV format depending on pixel's hue, and setting a minimal saturation of 50 %"""

    greenMinH = 75 // 2
    greenMaxH = 135 // 2

    @staticmethod
    def is_green(pixel) -> bool:
        h = pixel[0]

        return ColorsFilter.greenMinH <= h <= ColorsFilter.greenMaxH

    def __init__(self, threshold: float, on_frame: "function"):
        """threshold is the minimal Value (V) for a color to be kept, each convertion will result
        into a new borders array passed as argument to on_frame callback (functional paradigm)
        Note: threshold argument is expected to be a percentage."""

        self.threshold = (threshold / 100) * 255  # V is a % but OpenCV stores it as a byte (0-255)
        self.on_frame = on_frame

    def filter(self, border):
        """Image handling for a single pixels array"""

        length = len(border)  # Number of pixels in current screen border

        # Requires to have a 2D OpenCV image to make a cvtColor() call, creates a pixels line with
        # 2D image which has border_length * 1 dimensions
        border_image = np.zeros((1, length, 3), dtype=np.uint8)
        for i in range(length):
            border_image[0][i] = border[i]

        # Converts from HSV to get pixel brightness with Value (V)
        converted_image = cv.cvtColor(border_image, cv.COLOR_RGB2HSV)

        # 2D images is converted back into a simple pixels array
        new_border = np.zeros((length, 3), dtype=np.uint8)
        for i in range(length):
            pixel = converted_image[0][i]

            current_threshold = self.threshold
            # Brightness requirements is less high for green colors, forest are dark
            if ColorsFilter.is_green(pixel):
                current_threshold /= 2

            # If pixel color is too dark, it will be transformed to black (0, 0, 0), else the same
            # color is copied from original pixels array
            if pixel[2] < current_threshold:
                new_border[i] = np.zeros(3, dtype=np.uint8)
            else:
                pixel_image = np.zeros((1, 1, 3), dtype=np.uint8)

                # Filtering each H, S and V values for displayed pixel
                pixel_image[0][0][0] = pixel[0]
                pixel_image[0][0][1] = max(50, pixel[1])  # Minimal saturation is 50 % to avoid having too much white LEDs
                pixel_image[0][0][2] = pixel[2]

                new_border[i] = cv.cvtColor(pixel_image, cv.COLOR_HSV2RGB)[0][0]

        return new_border

    def __call__(self, borders):
        """Suppresses dark pixels by settings them to black, then call on_frame callback with new
        borders"""

        (top, bottom, left, right) = borders

        # Converts each border and use next image handling callback with them (functional paradigm)
        self.on_frame((self.filter(top), self.filter(bottom), self.filter(left), self.filter(right)))
