from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import pyglet
import subprocess
import mad
#from pydub import AudioSegment
#dirName = os.path.dirname(os.path.abspath(__file__))
FileLocation = "./BAC.mp3"
# read audio samples

mf = mad.MadFile(FileLocation)
track_length_in_milliseconds = mf.total_time()
subprocess.call(["mpg123", "-w", "new.wav", FileLocation])
input_data = read("new.wav")
audio = input_data[1]
# plot the first 1024 samples
plt.plot(audio[0:track_length_in_milliseconds])
# label the axes
plt.ylabel("Amplitude")
plt.xlabel("Time")
# set the title  
plt.title("Sample Wav")
# display the plot
plt.show()
print track_length_in_milliseconds
