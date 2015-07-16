import subprocess
import matplotlib.pyplot as plt
import numpy as np
import wave
import sys
FileLocation = "./BAC.mp3"
# read audio samples

#mf = mad.MadFile(FileLocation)
#track_length_in_milliseconds = mf.total_time()
subprocess.call(["mpg123", "-w", "new.wav", FileLocation])


spf = wave.open('new.wav','r')

#Extract Raw Audio from Wav File
signal = spf.readframes(-1)
signal = np.fromstring(signal, 'Int16')


#If Stereo
if spf.getnchannels() == 2:
    print 'Just mono files'
    sys.exit(0)

plt.figure(1)
plt.title('Signal Wave...')
lines = plt.plot(signal)
plt.setp(lines, color='black', backgroundcolor='gray', linewidth=2.0)
plt.show()
