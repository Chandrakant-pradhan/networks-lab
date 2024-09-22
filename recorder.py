import numpy as np
import pyaudio
from scipy.signal import stft

# Parameters for recording
FORMAT = pyaudio.paInt16  
CHANNELS = 1  
RATE = 88200 
CHUNK = 1024  

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Recording...")

# STFT parameters
window_size = 1024
hop_size = 512
magnitude_threshold = 0.0001

mystack= []

# Function to process each audio chunk
def process_chunk(chunk):
    waveform = np.frombuffer(chunk, dtype=np.int16)
    waveform = waveform / 32767.0  # Normalize
    frequencies, times, Zxx = stft(waveform, fs=RATE, nperseg=window_size, noverlap=window_size - hop_size)
    num=0
    placeholder=[]
    for i, time in enumerate(times):
        magnitudes = np.abs(Zxx[:, i])
        detected_indices = np.where(magnitudes > magnitude_threshold)[0]
        if detected_indices.size > 0:
            detected_freqs = frequencies[detected_indices]
            max_freq = np.max(detected_freqs)
        else:
            max_freq = 0  # No frequency detected
        num=num+1
        if num < 20:
        # Frequency-based output
            if max_freq > 7000:
               
            elif max_freq > 3000:
                print("0", end="", flush=True)
            else:
                print(".", end="", flush=True)

# Continuously process audio chunks in real-time
try:
    while True:
        data = stream.read(CHUNK)
        process_chunk(data)

except KeyboardInterrupt:
    print("\nStopping...")
    stream.stop_stream()
    stream.close()
    audio.terminate()
