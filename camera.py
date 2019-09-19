import io
import random
import picamera
import os
import time

RESOLUTION = (1280, 720)
FRAMERATE = 60
BITRATE = 17000000
BUFFER_SEC = 20


class ContinuousCamera:
    def __init__(self):
        self.camera = picamera.PiCamera(framerate=FRAMERATE, resolution=RESOLUTION)
        self.camera.rotation = 180
        self.stream = picamera.PiCameraCircularIO(self.camera, seconds=BUFFER_SEC, bitrate=BITRATE)
        self.camera.start_recording(self.stream, format='h264', bitrate=BITRATE, level="4.2")

    def dump_to_file(self, filename):
        time.sleep(5)
        self.stream.copy_to(f"{filename}.h264", seconds=BUFFER_SEC)
