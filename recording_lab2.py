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

# Perform XOR operation between two binary strings
def xor(a, b):
    result = []
    for i in range(1, len(b)):
        result.append(str(int(a[i]) ^ int(b[i])))
    return ''.join(result)

# Performs Modulo-2 division
def mod2div(dividend, divisor):
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

#flip ith bit of message
def bitflip(message,i):
    return message[:i] + str(1 - int(message[i])) + message[i+1:]

#error correction
def error_correction(error_message):
    if mod2div(error_message,GENERATOR) == "0" * (len(GENERATOR) - 1):
        return error_message, None
    for i in range(len(error_message)):
        message = bitflip(error_message,i)
        if mod2div(message,GENERATOR) == "0" * (len(GENERATOR) - 1):
            return message[:-len(GENERATOR) + 1],[i] 
    for i in range(len(error_message)):
        for j in range(i+1,len(error_message)):
            message = bitflip(error_message,i)
            message = bitflip(message,j)
            if mod2div(message,GENERATOR) == "0" * (len(GENERATOR) - 1):
                return message[:-len(GENERATOR) + 1],[i,j]
        

# Parameters for recording
FORMAT = pyaudio.paInt16  
CHANNELS = 1  
RATE = 88200 
CHUNK = 1024  
RECORD_SECONDS = 55 
OUTPUT_FILENAME = "output.wav"  
GENERATOR = "010111010111"

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Recording...")
frames = []
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print("Finished recording.")
stream.stop_stream()
stream.close()
audio.terminate()

with wave.open(OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print(f"Audio saved to {OUTPUT_FILENAME}")
with wave.open(OUTPUT_FILENAME, 'rb') as wf:
    n_frames = wf.getnframes()
    waveform = np.frombuffer(wf.readframes(n_frames), dtype=np.int16)
    waveform = waveform / 32767.0 

window_size = 1024
hop_size = 512

#FFT for frequency detection using STFT
frequencies, times, Zxx = stft(waveform, fs=RATE, nperseg=window_size, noverlap0=window_size - hop_size)
magnitude_threshold = 0.0001 
detected_frequencies = []
received_message = ""
for i, time in enumerate(times):
    if np.isclose(time % 1, 0, atol=hop_size/RATE):  
        magnitudes = np.abs(Zxx[:, i])
        detected_indices = np.where(magnitudes > magnitude_threshold)[0]
        if detected_indices.size > 0:
            detected_freqs = frequencies[detected_indices]
            max_freq = np.max(detected_freqs)
        else:
            max_freq = 0 
        #filtering out the higher frequencies
        if max_freq > 7000:
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

#printing things
lenBits = received_message[i + 6 : i + 11]
lengthOfMessage = strToDec(lenBits)
error_message = received_message[i+11 : i + 11 + lengthOfMessage]
corrected_message,erorr_pos = error_correction(error_message)
print("length of the encoded message:", lengthOfMessage, "length of original message:",lengthOfMessage - len(GENERATOR) + 1)
print("Error Positions:", erorr_pos)
print("Corrected original message:" , corrected_message)

#graph
plt.figure(figsize=(10, 6))
plt.pcolormesh(times, frequencies, np.abs(Zxx), shading='gouraud')
plt.title('STFT Spectrogram')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [s]')
plt.colorbar(label='Magnitude')
#plt.show()
