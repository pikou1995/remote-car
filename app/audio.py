import asyncio
import fractions
from logging import log
import time
import pyaudio
import av

from aiortc.mediastreams import AudioStreamTrack


class RTCAudioTrack(AudioStreamTrack):
    def __init__(self):
        super().__init__()  # don't forget this!

        self.AUDIO_PTIME = 0.02
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = int(self.RATE * self.AUDIO_PTIME)

        self.p = pyaudio.PyAudio()
        self.mic_stream = self.p.open(
            format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True)

        self.codec = av.CodecContext.create('pcm_s16le', 'r')
        self.codec.sample_rate = self.RATE
        self.codec.channels = self.CHANNELS

    async def recv(self):
        mic_data = self.mic_stream.read(self.CHUNK)
        packet = av.Packet(mic_data)
        frame = self.codec.decode(packet)[0]

        if hasattr(self, "_timestamp"):
            self._timestamp += self.CHUNK
            wait = self._start + (self._timestamp /
                                  self.RATE) - time.time()
            await asyncio.sleep(wait)
        else:
            self._start = time.time()
            self._timestamp = 0

        frame.pts = self._timestamp
        frame.sample_rate = self.RATE
        frame.time_base = fractions.Fraction(1, self.RATE)
        return frame
