from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from scipy.signal import stft
import numpy as np
import pyaudio
import wave
from timeit import default_timer as timer
import generator as gen

# Parameters for recording
FORMAT = pyaudio.paInt16  
CHANNELS = 1  
RATE = 88200 
CHUNK = 1024  
BIT_INTERVAL = 0.5
THRESHOLD = 0.00005   
GENERATOR = "010111010111"

# For CSMA Protocol
DIFS = 5
SIFS = 2
N = 0
MAX_WAIT = 60 * BIT_INTERVAL
MAC = 2  

#utility for string to number
def strToDec(s,nbits):
     ans = 0
     s = s[::-1]
     for i in range(nbits):
         if(s[i] == '1'):
             ans += (1 << i)
     return ans

#send ACK
def sendACK(senderMAC , recieverMAC):
    #both supplied as string of binaries
    print("Sending Acknowledgement ...")
    finalMessage = senderMAC + recieverMAC
    gen.sendMsg(finalMessage)
    print("Sent the Acknowledgement")

def waitACK(dest_MAC, waitTime = SIFS):
    global N
    ACK = listenMsg(waitTime)
    ACK = ACK.strip("x")
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
    print("Clock Started and Listening for message ...")
    start = timer()
    frames = []
    for _ in range(0, int(RATE / CHUNK * waitTime)):
        data = stream.read(CHUNK)
        frames.append(data)
        now = timer()
        if now - start > BIT_INTERVAL:
            start = np.floor(now * 10) / 10
            combined_data = b''.join(frames)
            audio_data = np.frombuffer(combined_data, dtype=np.int16)
            audio_data = audio_data / 32767.0
            f, t, Zxx = stft(audio_data, fs=RATE, nperseg= 1024, noverlap=512)
            magnitudes = np.abs(Zxx[:,-1])
            detected_indices = np.where(magnitudes > THRESHOLD)[0]
            if detected_indices.size > 0:
                detected_freqs = f[detected_indices]
                max_freq = np.max(detected_freqs)
            else:
                max_freq = 0
            if max_freq > 10000:
                print("Carrier is busy 😭. Received a 1")
                N = N + 1
                return True
            elif max_freq > 5000:
                print(max_freq)
                print("Carrier is busy 😭. Received a 0")
                N = N + 1
                return True
    print("All clear dude 😎")
    stream.stop_stream()
    stream.close()
    audio.terminate()
    return False
            
#listen function
def listenMsg(waitTime = MAX_WAIT):
    audio = audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    start = timer()
    print("Clock started and Listening now ...",start)
    received_message = ""
    frames = []
    for _ in range(0, int(RATE / CHUNK * waitTime)):
        data = stream.read(CHUNK)
        frames.append(data)

    end = timer()
    print("Ended Listening at time t =",end)
    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveform = np.frombuffer(b''.join(frames), dtype=np.int16)
    waveform = waveform / 32767.0 

    frequencies, times, Zxx = stft(waveform, fs=RATE, nperseg=1024, noverlap=512)
    detected_frequencies = []
    for i, time in enumerate(times):
        if np.isclose(time % BIT_INTERVAL, 0, atol= 512/RATE): 
            magnitudes = np.abs(Zxx[:, i])
            detected_indices = np.where(magnitudes > THRESHOLD)[0]
            if detected_indices.size > 0:
                detected_freqs = frequencies[detected_indices]
                max_freq = np.max(detected_freqs)
            else:
                max_freq = 0 
            if max_freq > 10000:
                print(f"Time {time:.2f}s: 1 (Max Frequency: {max_freq:.2f} Hz)"); received_message += "1"
            elif max_freq > 5000:
                print(f"Time {time:.2f}s: 0 (Max Frequency: {max_freq:.2f} Hz)"); received_message += "0"
            else :
                print(f"Time {time:.2f}s: x (Max Frequency: {max_freq:.2f} Hz)")
    print("received_message:", received_message)
    return received_message

def getInfo(received_message):
    n = len(received_message)
    i = 0
    while(i<n):
        if(received_message[i : i+6] == '101011'):
            break
        else:
            i += 1
    
    lenBits = received_message[i + 6 : i + 11]
    lengthOfMessage = strToDec(lenBits,5) - 4
    senderMAC = received_message[i+11 : i+13]
    receiverMAC = received_message[i+13 : i+15]
    sentMessage = received_message[i+15 : i+15 + lengthOfMessage]

    isMyMsg = True
    collision = False

    if(strToDec(receiverMAC,2) != MAC):
        isMyMsg = False
    if(gen.mod2div(sentMessage,GENERATOR) != "0" * (len(GENERATOR) - 1)):
        collision = True

    return [isMyMsg , collision , lenBits , lengthOfMessage , senderMAC , receiverMAC , sentMessage]

def infoPrint(msg):
    if (msg[0]):
        if(not msg[1]):
            print("Message received successfully")
            print("Length:", msg[3])
            print("Sender:", msg[4])
            print("Message:", msg[-1])
        else:
            print("There must be collision")
    else:
        print("Not your message dude")