#!/usr/bin/python

import ffmpeg
from sys import argv


dev_index = int(argv[1])
framerate = argv[2]

ffmpeg \
    .input(":0.0", f="x11grab", s="1920x1080", r=framerate) \
    .output(f"/dev/video{dev_index}", f="v4l2").run()
