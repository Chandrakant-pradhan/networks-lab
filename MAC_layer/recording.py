from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from scipy.signal import stft
import numpy as np
import pyaudio
import wave
from generator import mod2div , sendMsg

# Parameters for recording
FORMAT = pyaudio.paInt16  
CHANNELS = 1  
RATE = 88200 
CHUNK = 1024  
RECORD_SECONDS = 55 
OUTPUT_FILENAME = "output_recording.wav"  
GENERATOR = "010111010111"

#utility for string to number
def strToDec(s):
     ans = 0
     s = s[::-1]
     for i in range(5):
         if(s[i] == '1'):
             ans += (1 << i)
     return ans

#send ACK
def sendACK(senderMAC , recieverMAC):
    #both supplied as string of binaries
    finalMessage = senderMAC + recieverMAC
    sendMsg(finalMessage)

#carrier sense
def carrierSense():
    return False

#listen function
def listenMsg():
   audio = pyaudio.PyAudio()
   stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
   frames = []

   for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
       data = stream.read(CHUNK)
       frames.append(data)

   stream.stop_stream()
   stream.close()
   audio.terminate()
   waveform = np.frombuffer(b''.join(frames), dtype=np.int16)
   waveform = waveform / 32767.0

   window_size = 1024
   hop_size = 512
    #FFT for frequency detection using STFT
   frequencies, times, Zxx = stft(waveform, fs=RATE, nperseg=window_size, noverlap=window_size - hop_size)
   magnitude_threshold = 0.0001 
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

           if max_freq > 7000:
               received_message += "1"
           else:
               received_message += "0"

   return received_message


def getInfo(received_message , myMAC):
    n = len(received_message)
    i = 0
    while(i<n):
        if(received_message[i : i+6] == '101011'):
            break
        else:
            i += 1
    
    lenBits = received_message[i + 6 : i + 11]
    lengthOfMessage = strToDec(lenBits) - 4
    senderMAC = received_message[i+11 : i+13]
    receiverMAC = received_message[i+13 : i+15]
    sentMessage = received_message[i+15 : i+15 + lengthOfMessage]

    isMyMsg = True
    collision = False

    if(receiverMAC != myMAC):
        isMyMsg = False
    if(mod2div(sentMessage,GENERATOR) != "0" * (len(GENERATOR) - 1)):
        collision = True

    return [isMyMsg , collision , lenBits , lengthOfMessage , senderMAC , receiverMAC , sentMessage]


