#!/usr/bin/env python3

import pyaudio
import av


class RadioTelephoneTrack():
    def __init__(self):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 8000
        self.CHUNK = 1024

        self.p = pyaudio.PyAudio()
        self.mic_stream = self.p.open(
            format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True)

        self.codec = av.CodecContext.create('pcm_s16le', 'r')
        self.codec.sample_rate = self.RATE
        self.codec.channels = self.CHANNELS

        self.audio_samples = 0
        self.chunk_number = 0

    def recv(self):
        mic_data = self.mic_stream.read(self.CHUNK)
        packet = av.Packet(mic_data)
        frame = self.codec.decode(packet)[0]
        frame.pts = self.audio_samples
        self.audio_samples += frame.samples
        self.chunk_number = self.chunk_number + 1
        print('audio', frame)
        return frame


track = RadioTelephoneTrack()

while True:
    frame = track.recv()
    print(frame)
