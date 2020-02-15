# -*- coding:utf-8 -*-
import pyaudio
import numpy as np
import wave

RATE=44100
CHUNK = 22050
p=pyaudio.PyAudio()

f_list=['a','i','si','te','ru','u','wa','n','sa','n']

stream=p.open(format = pyaudio.paInt16,
        channels = 1,
        rate = int(48000),
        frames_per_buffer = CHUNK,
        input = True,
        output = True) # inputとoutputを同時にTrueにする

for i in f_list:
    wavfile = './wav/'+i+'.wav'
    print(wavfile)
    wr = wave.open(wavfile, "rb")
    input = wr.readframes(wr.getnframes())
    output = stream.write(input)