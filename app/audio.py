from av import AudioFrame
from cv2 import log
from pydub import AudioSegment
import pyaudio
import av
import fractions

from aiortc.mediastreams import MediaStreamTrack


class RadioTelephoneTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()  # don't forget this!

        self.AUDIO_PTIME = 0.020  # 20ms audio packetization

        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 48000
        self.CHUNK = int(self.RATE * 0.020)

        self.p = pyaudio.PyAudio()
        self.mic_stream = self.p.open(
            format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)

        self.codec = av.CodecContext.create('pcm_s16le', 'r')
        self.codec.sample_rate = self.RATE
        self.codec.channels = self.CHANNELS

        self.audio_samples = 0
        self.chunk_number = 0

    async def recv(self):
        mic_data = self.mic_stream.read(self.CHUNK)
        packet = av.Packet(mic_data)
        frame = self.codec.decode(packet)[0]
        frame.pts = self.audio_samples
        self.audio_samples += frame.samples
        self.chunk_number = self.chunk_number + 1
        print('audio', frame)
        return frame
