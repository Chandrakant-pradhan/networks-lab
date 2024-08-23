import numpy as np
import wave
#nimish joined

# Parameters for decoding
sample_rate = 88200  # Sample rate in Hz
duration = 1.0       # Duration of each bit in seconds
frequency = 250    # Frequency of the tone in Hz

# Load the waveform from the WAV file
filename = "output.wav"
with wave.open(filename, 'rb') as wf:
    n_frames = wf.getnframes()
    waveform = np.frombuffer(wf.readframes(n_frames), dtype=np.int16)
    waveform = waveform / 32767.0  # Normalize the waveform to -1.0 to 1.0

# Function to decode waveform to bitstring
def waveform_to_bitstring(waveform, sample_rate, duration, frequency):
    samples_per_bit = int(sample_rate * duration)
    bitstring = ""

    for i in range(0, len(waveform), samples_per_bit):
        bit_waveform = waveform[i:i + samples_per_bit]
        # Calculate the mean value of the waveform
        mean_value = np.mean(bit_waveform)
        
        # Determine if the bit is '1' or '0' based on the mean value
        if mean_value > 0:
            bitstring += '1'
        else:
            bitstring += '0'

    return bitstring

# Decode the waveform to bitstring
recovered_bitstring = waveform_to_bitstring(waveform, sample_rate, duration, frequency)
print(f"Recovered bitstring: {recovered_bitstring}")
