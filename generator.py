import numpy as np
import pyaudio
import wave

#functions 
def decTobitstring(n):
    str = ""
    while(n > 0):
        if(n%2 == 0):
            str += '0'
        else:
            str += '1'
        n = n // 2
    
    length = len(str)
    str += "0"*(5-length)
    return str[::-1]

# Parameters for the audio
sample_rate = 88200  # Sample rate in Hz
duration = 1.0       # Duration of each bit in seconds
frequency1 = 8000   # frequency for bit = 1
frequency0 = 4000   # frequency for bit = 0
amplitude = 0.5      # Amplitude of the waveform

# Example bitstring
bitstring = input()
a, b = map(float, input().split())

def addPreamble(bitstring):
    message = "101010101011" + decTobitstring(len(bitstring)) + bitstring
    return message

# Convert bitstring to waveform
def bitstring_to_waveform(bitstring, sample_rate, duration, freq1, freq0, amplitude):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = np.concatenate([
        amplitude * np.sin(2 * np.pi * freq1 * t) if bit == '1' 
        else -1 *  amplitude * np.sin(2 * np.pi * freq0 * t)
        for bit in bitstring
    ])
    return waveform

# Create waveform from bitstring
finalmessage = addPreamble(bitstring)
waveform = bitstring_to_waveform(finalmessage, sample_rate, duration, frequency1, frequency0, amplitude)

# Normalize waveform to 16-bit PCM format
waveform = np.int16(waveform * 32767)

# Save waveform to a WAV file
filename = "output.wav"
with wave.open(filename, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 2 bytes per sample (16 bits)
    wf.setframerate(sample_rate)
    wf.writeframes(waveform.tobytes())

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
