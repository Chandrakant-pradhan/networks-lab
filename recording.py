from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from scipy.signal import stft
import numpy as np
import pyaudio
import wave

#functions
def strToDec(s):
     ans = 0
     s = s[::-1]
     for i in range(5):
         if(s[i] == '1'):
             ans += (1 << i)
     return ans

def xor(a, b):
    # Perform XOR operation between two binary strings
    result = []
    for i in range(1, len(b)):
        result.append(str(int(a[i]) ^ int(b[i])))
    return ''.join(result)

def mod2div(dividend, divisor):
    # Performs Modulo-2 division
    pick = len(divisor)
    tmp = dividend[0:pick]

    while pick < len(dividend):
        if tmp[0] == '1':
            tmp = xor(divisor, tmp) + dividend[pick]
        else:
            tmp = xor('0'*pick, tmp) + dividend[pick]
        pick += 1

    if tmp[0] == '1':
        tmp = xor(divisor, tmp)
    else:
        tmp = xor('0'*pick, tmp)

    return tmp
def bitflip(message,i):
    return message[:i] + str(1 - int(message[i])) + message[i+1:]

def error_correction(error_message):
    for i in range(len(error_message)):
        message = bitflip(error_message,i)
        if mod2div(message,GENERATOR) == "0" * (len(GENERATOR) - 1):
            return message[:-len(GENERATOR)]
    for i in range(len(error_message)):
        for j in range(i+1,len(error_message)):
            message = bitflip(error_message,i)
            message = bitflip(message,j)
            if mod2div(message,GENERATOR) == "0" * (len(GENERATOR) - 1):
                return message[:-len(GENERATOR)]
        

# Parameters for recording
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (stereo)
RATE = 88200  # Sample rate (44.1kHz)
CHUNK = 1024  # Size of each audio chunk
RECORD_SECONDS = 50 # Duration of recording
OUTPUT_FILENAME = "output.wav"  # Output file name
GENERATOR = "010111010111"

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open a stream for recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Recording...")

frames = []

# Record for the specified number of seconds
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Finished recording.")

# Stop and close the stream
stream.stop_stream()
stream.close()
audio.terminate()

# Save the recorded data to a WAV file
with wave.open(OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print(f"Audio saved to {OUTPUT_FILENAME}")

with wave.open(OUTPUT_FILENAME, 'rb') as wf:
    n_frames = wf.getnframes()
    waveform = np.frombuffer(wf.readframes(n_frames), dtype=np.int16)
    waveform = waveform / 32767.0  # Normalize the waveform to -1.0 to 1.0

window_size = 1024
hop_size = 512

frequencies, times, Zxx = stft(waveform, fs=RATE, nperseg=window_size, noverlap=window_size - hop_size)

# Threshold for detection (you can adjust this value)
magnitude_threshold = 0.0001 # Magnitude threshold for considering a frequency detected

# List to store detected frequencies in each time interval
detected_frequencies = []

received_message = ""
# Loop over time intervals
for i, time in enumerate(times):
    if np.isclose(time % 1, 0, atol=hop_size/RATE):  # Check if time is close to a multiple of 1 second
        # Get the magnitudes at the current time step
        magnitudes = np.abs(Zxx[:, i])

        # Get the indices of frequencies with magnitudes above the threshold
        detected_indices = np.where(magnitudes > magnitude_threshold)[0]
        
        if detected_indices.size > 0:
            # Get the corresponding frequencies
            detected_freqs = frequencies[detected_indices]
            
            # Determine the maximum frequency detected at this time step
            max_freq = np.max(detected_freqs)
        else:
            max_freq = 0  # No significant frequency detected
            
        # Print 1 if the maximum frequency is greater than 8000 Hz, else print 0
        if max_freq > 19000:
            print(f"Time {time:.2f}s: 1 (Max Frequency: {max_freq:.2f} Hz)"); received_message += "1"
        else:
            print(f"Time {time:.2f}s: 0 (Max Frequency: {max_freq:.2f} Hz)"); received_message += "0"


n = len(received_message)
i = 0
while(i<n):
   if(received_message[i : i+6] == '101011'):
       break
   else:
       i += 1

lenBits = received_message[i + 6 : i + 11]
lengthOfMessage = strToDec(lenBits)
error_message = received_message[i+11 : i + 11 + lengthOfMessage]

corrected_message = error_correction(error_message)
print(lengthOfMessage)
print(corrected_message)

# Step 3: Plot the STFT result (Spectrogram)
plt.figure(figsize=(10, 6))
plt.pcolormesh(times, frequencies, np.abs(Zxx), shading='gouraud')
plt.title('STFT Spectrogram')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [s]')
plt.colorbar(label='Magnitude')
plt.show()
# code ended