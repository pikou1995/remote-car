import asyncio
import fractions
import time
import pyaudio
import av
from aiortc.mediastreams import AudioStreamTrack, MediaStreamError


class RTCAudioTrack(AudioStreamTrack):
    def __init__(self):
        super().__init__()  # don't forget this!
        self.sample_rate = 8000
        self.AUDIO_PTIME = 0.02
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.samples = int(self.sample_rate * self.AUDIO_PTIME)

        self.p = pyaudio.PyAudio()
        self.mic_stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.samples
        )
        self.mic_stream.start_stream()

        self.codec = av.CodecContext.create('pcm_s16le', 'r')
        self.codec.sample_rate = self.sample_rate
        self.codec.channels = self.CHANNELS

    async def recv(self):
        if self.readyState != "live":
            raise MediaStreamError

        mic_data = self.mic_stream.read(self.samples, False)
        packet = av.Packet(mic_data)
        frame = self.codec.decode(packet)[0]

        if hasattr(self, "_timestamp"):
            self._timestamp += self.samples
            wait = self._start + (self._timestamp /
                                  self.sample_rate) - time.time()
            await asyncio.sleep(wait)
        else:
            self._start = time.time()
            self._timestamp = 0

        frame.pts = self._timestamp
        frame.sample_rate = self.sample_rate
        frame.time_base = fractions.Fraction(1, self.sample_rate)
        return frame
