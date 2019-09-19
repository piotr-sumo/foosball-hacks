import pyaudio
import aubio
import numpy
import collections

# https://makersportal.com/blog/2018/8/23/recording-audio-on-the-raspberry-pi-with-python-and-a-usb-microphone


class MicProcessor:
    def __init__(self, device_name):
        self.audio = pyaudio.PyAudio()
        self.device_indices = []
        for index in range(self.audio.get_device_count()):
            device = self.audio.get_device_info_by_index(index)
            if device.get('name') == device_name:
                self.device_indices += [index]
        self.streams = []

    def close_streams(self):
        for stream in self.streams:
            stream.stop_stream()
            stream.close()
        self.streams = []
        self.circular_buffer = collections.deque(maxlen=self.circular_buffer_maxlen)

    def default_callback(self, in_data, frame_count, time_info, status):
        samples = numpy.fromstring(in_data, dtype=aubio.float_type)
        volume = numpy.sum(samples**2) / len(samples)
        self.circular_buffer.append(volume)
        return None, pyaudio.paContinue

    def max_volume_in_circular_buffer(self):
        max_volume = 0
        circular_buffer = self.circular_buffer.copy()
        for volume in circular_buffer:
            max_volume = max(volume, max_volume)
        return max_volume

    def open_streams(self, rate=44100, channels=1, format=pyaudio.paFloat32, frames_per_buffer=4096,
                     input_host_api_specific_stream_info=None, stream_callback=None, circular_buffer_maxlen=100):
        # with defaults, circular_buffer_maxlen=100 means last 10s or 10s/number of devices
        self.circular_buffer_maxlen = circular_buffer_maxlen
        self.close_streams()
        self.pitch = aubio.pitch('default', frames_per_buffer*2, frames_per_buffer, rate)
        self.pitch.set_unit('Hz')
        self.pitch.set_silence(-40)
        for _ in self.device_indices:
             self.streams += [
                self.audio.open(
                    rate=rate,
                    channels=channels,
                    format=format,
                    frames_per_buffer=frames_per_buffer,
                    input=True,
                    start=True,
                    input_host_api_specific_stream_info=input_host_api_specific_stream_info,
                    stream_callback=stream_callback
                )
             ]
