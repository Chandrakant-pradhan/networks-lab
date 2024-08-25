import numpy as np
import pyaudio
import wave

# Parameters for the audio
sample_rate = 88200  # Sample rate in Hz
duration = 1.0       # Duration of each bit in seconds
frequency = 250   #  of the tone in Hz
amplitude = 0.5      # Amplitude of the waveform

# Example bitstring
bitstring = "1011" * 5

frequency1 = 880
frequency0 = 440

# Convert bitstring to waveform
def bitstring_to_waveform(bitstring, sample_rate, duration, frequency, amplitude):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = np.concatenate([
        amplitude * np.sin(2 * np.pi * frequency1 * t) if bit == '1' 
        else -1 *  amplitude * np.sin(2 * np.pi * frequency0 * t)
        for bit in bitstring
    ])
    return waveform

# Create waveform from bitstring
waveform = bitstring_to_waveform(bitstring, sample_rate, duration, frequency, amplitude)

# Normalize waveform to 16-bit PCM format
waveform = np.int16(waveform * 32767)

# Save waveform to a WAV file
filename = "output.wav"
with wave.open(filename, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 2 bytes per sample (16 bits)
    wf.setframerate(sample_rate)
    wf.writeframes(waveform.tobytes())
# yo daya's here
# Playback the generated audio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True)

# Play the waveform
stream.write(waveform.tobytes())

# Cleanup
stream.stop_stream()
stream.close()
p.terminate()

print(f"Audio has been saved to {filename} and played back.")
