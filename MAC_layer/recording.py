from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from scipy.signal import stft
import numpy as np
import pyaudio
import wave
import generator as gen

# Parameters for recording
FORMAT = pyaudio.paInt16  
CHANNELS = 1  
RATE = 88200 
CHUNK = 1024  
BIT_INTERVAL = 0.1
CHUNKS_PER_INTERVAL = int(RATE * BIT_INTERVAL / CHUNK) 
THRESHOLD = 0.0001   
GENERATOR = "010111010111"

# For CSMA Protocol
DIFS = 5
SIFS = 0.5
CARRIER_BUSY = False
N = 0
MAX_WAIT = 10
MAC = 1 # Change this !! 

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
    gen.sendMsg(finalMessage)

def waitACK(dest_MAC, waitTime = SIFS):
    global N
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Waiting for Acknowledgement ...")
    frames = []
    ACK = ""
    for _ in range(0, int(RATE / CHUNK * waitTime)):
        data = stream.read(CHUNK)
        frames.append(data)
        if len(frames) >= CHUNKS_PER_INTERVAL:
            # Concatenate the chunks in the buffer
            combined_data = b''.join(frames)
            
            # Convert the byte data to NumPy array for processing
            audio_data = np.frombuffer(combined_data, dtype=np.int16)

            # Apply STFT (Short-Time Fourier Transform)
            f, t, Zxx = stft(audio_data, fs=RATE, nperseg=CHUNK)
            magnitudes = np.abs(Zxx)
            detected_indices = np.where(magnitudes > THRESHOLD)[0]
            if detected_indices.size > 0:
                detected_freqs = f[detected_indices]
                max_freq = np.max(detected_freqs)
            else:
                max_freq = 0
                break
            if max_freq > 12000:
                ACK += "1"
            elif max_freq > 7000:
                ACK += "0"
    if not len(ACK) == 4:
        N = N + 1
        return False
    else:
        sender = ACK[0:2]
        receiver = ACK[2:]
        if not (sender == gen.decTobitstring(MAC) and receiver == gen.decTobitstring(dest_MAC)):
            N = N + 1
            return False
        return True


#carrier sense
def carrierSense(waitTime):
    global N
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Carrier Sensing. Wait ...")
    frames = []; i = 0
    for _ in range(0, int(RATE / CHUNK * waitTime)):
        data = stream.read(CHUNK)
        frames.append(data)
        if len(frames) >= CHUNKS_PER_INTERVAL:
            # Concatenate the chunks in the buffer
            combined_data = b''.join(frames)
            
            # Convert the byte data to NumPy array for processing
            audio_data = np.frombuffer(combined_data, dtype=np.int16)

            # Apply STFT (Short-Time Fourier Transform)
            f, t, Zxx = stft(audio_data, fs=RATE, nperseg= 1024, noverlap=512)
            magnitudes = np.abs(Zxx[:i]); i += 1
            detected_indices = np.where(magnitudes > THRESHOLD)[0]
            if detected_indices.size > 0:
                detected_freqs = f[detected_indices]
                # print(np.max(detected_freqs))
                max_freq = np.max(detected_freqs)
            else:
                max_freq = 0
            if max_freq > 12000:
                print(max_freq)
                print("Carrier is busy 😭. Received a 1")
                CARRIER_BUSY = True
                N = N + 1
                return False
            elif max_freq > 10000:
                print(max_freq)
                print("Carrier is busy 😭. Received a 0")
                CARRIER_BUSY = True
                N = N + 1
                return False
    print("All clear dude 😎")
    return True

#listen function
def listenMsg(waitTime):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Carrier Sensing. Wait ...")
    frames = []
    bitString = ""
    for _ in range(0, int(RATE / CHUNK * waitTime)):
        data = stream.read(CHUNK)
        frames.append(data)
        if len(frames) >= CHUNKS_PER_INTERVAL:
            # Concatenate the chunks in the buffer
            combined_data = b''.join(frames)
            frames = []
            
            # Convert the byte data to NumPy array for processing
            audio_data = np.frombuffer(combined_data, dtype=np.int16)

            # Apply STFT (Short-Time Fourier Transform)
            f, t, Zxx = stft(audio_data, fs=RATE, nperseg=CHUNK)
            magnitudes = np.abs(Zxx)
            detected_indices = np.where(magnitudes > THRESHOLD)[0]
            if detected_indices.size > 0:
                detected_freqs = f[detected_indices]
                max_freq = np.max(detected_freqs)
            else:
                max_freq = 0
            if max_freq > 12000:
                bitString += "1"
            elif max_freq > 7000:
                bitString += "0"
            else:
                bitString += "."
    return bitString


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
    if(gen.mod2div(sentMessage,GENERATOR) != "0" * (len(GENERATOR) - 1)):
        collision = True

    return [isMyMsg , collision , lenBits , lengthOfMessage , senderMAC , receiverMAC , sentMessage]


