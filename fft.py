from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from scipy.signal import stft
import numpy as np
import pyaudio
import wave

# Parameters for recording
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (stereo)
RATE = 88200  # Sample rate (44.1kHz)
CHUNK = 1024  # Size of each audio chunk
RECORD_SECONDS = 20 # Duration of recording
OUTPUT_FILENAME = "output.wav"  # Output file name

# Initialize PyAudio
audio = pyaudio.PyAudio()

filename = "output.wav"

with wave.open(filename, 'rb') as wf:
    n_frames = wf.getnframes()
    waveform = np.frombuffer(wf.readframes(n_frames), dtype=np.int16)
    waveform = waveform / 32767.0  # Normalize the waveform to -1.0 to 1.0

window_size = 1024
hop_size = 512

frequencies, times, Zxx = stft(waveform, fs=RATE, nperseg=window_size, noverlap=window_size - hop_size)
# print(f"Zxx are: {Zxx}")



# Threshold for detection (you can adjust this value)
magnitude_threshold = 0.0001 # Magnitude threshold for considering a frequency detected

# List to store detected frequencies in each time interval
detected_frequencies = []

# Loop over time intervals
for i, time in enumerate(times):
    if np.isclose(time % 1, 0, atol=hop_size/RATE):  # Check if time is close to a multiple of 1 second
        # Get the magnitudes at the current time step
        magnitudes = np.abs(Zxx[:, i])
        
        # # Get the indices of frequencies with magnitudes above the threshold
        # detected_indices = np.where(magnitudes > magnitude_threshold)[0]
        
        # # Get the corresponding frequencies
        # detected_freqs = frequencies[detected_indices]
        
        # # Store the detected frequencies for this time interval
        # detected_frequencies.append(detected_freqs)

        # # Print detected frequencies for this time interval
        # # print(f"Time {time:.2f}s: Detected Frequencies: {detected_freqs}")
        # if detected_frequencies.max()> 8000 :
        #     print(f"Time {time:.2f}s: Detected bit : 1")
        # else :
        #     print(f"Time {time:.2f}s: Detected bit : 0")

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
        if max_freq > 8000:
            print(f"Time {time:.2f}s: 1 (Max Frequency: {max_freq:.2f} Hz)")
        else:
            print(f"Time {time:.2f}s: 0 (Max Frequency: {max_freq:.2f} Hz)")



# Step 3: Plot the STFT result (Spectrogram)
plt.figure(figsize=(10, 6))
plt.pcolormesh(times, frequencies, np.abs(Zxx), shading='gouraud')
plt.title('STFT Spectrogram')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [s]')
plt.colorbar(label='Magnitude')
plt.show()