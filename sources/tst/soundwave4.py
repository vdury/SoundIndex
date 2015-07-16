import matplotlib.pyplot as plt
import numpy as np
import wave
import sys
import subprocess

FileLocation = "./BAC.mp3"

subprocess.call(["mpg123", "-w", "new.wav", FileLocation])

spf = wave.open('new.wav','r')

#Extract Raw Audio from Wav File
signal = spf.readframes(-1)
signal = np.fromstring(signal, 'Int16')
fs = spf.getframerate()

#If Stereo
if spf.getnchannels() == 2:
    print 'Just mono files'
    sys.exit(0)


Time=np.linspace(0, len(signal)/fs, num=len(signal))

plt.figure(1)
plt.title('Signal Wave...')
plt.plot(Time,signal)
plt.show()
#plt.savefig('empty.png', format='png')

