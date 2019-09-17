import io
import random
import picamera
import os
import time

RESOLUTION = (1280, 720)
FRAMERATE = 60
BITRATE = 17000000
BUFFER_SEC = 20

class ContinousCamera:
    def __init__(self):
        self.camera = picamera.PiCamera(framerate=FRAMERATE, resolution=RESOLUTION)
        self.stream = picamera.PiCameraCircularIO(self.camera, seconds=BUFFER_SEC, bitrate=BITRATE)
        self.camera.start_recording(self.stream, format='h264', bitrate=BITRATE)
    
    def dump_to_file(self, filename):
        self.stream.copy_to(f"{filename}.h264", seconds=BUFFER_SEC)

