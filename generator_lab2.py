import numpy as np
import pyaudio
import wave

#num to string
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

#flip ith bit of message
def bitflip(message,i):
    return message[:i] + str(1 - int(message[i])) + message[i+1:]

#xor of a and b
def xor(a, b):
    result = []
    for i in range(1, len(b)):
        result.append(str(int(a[i]) ^ int(b[i])))
    return ''.join(result)

#Performs Modulo-2 division
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

#Append zero bits equivalent to the length of the key minus 1
def encode_data(data, key):
    appended_data = data + '0'*(len(key)-1)
    remainder = mod2div(appended_data, key)
    crc = remainder

    return data + crc

#Parameters for the audio
sample_rate = 88200  
duration = 1     
frequency1 = 8000 
frequency0 = 4000 
amplitude = 0.5     
GENERATOR = "010111010111"

#input
bitstring = input()
a, b = map(float, input().split())

#adding the preamble
def addPreamble(bitstring):
    message = "101010101010101011" + decTobitstring(len(bitstring)) + bitstring
    return message

#Convert bitstring to waveform
def bitstring_to_waveform(bitstring, sample_rate, duration, freq1, freq0, amplitude):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = np.concatenate([
        amplitude * np.sin(2 * np.pi * freq1 * t) if bit == '1' 
        else -1 *  amplitude * np.sin(2 * np.pi * freq0 * t)
        for bit in bitstring
    ])
    return waveform

#Create waveform from bitstring
message = encode_data(bitstring,GENERATOR)
n = len(message)
ind1 = int(n*a)-1
ind2 = int(n*b)-1
errMessage = bitflip(message , ind1)
if(b != 0):
    errMessage = bitflip(errMessage , ind2)
finalmessage = addPreamble(errMessage)

#printing things
print("original message : " , bitstring)
print("length of message : " , len(bitstring))
print("error index 1 : " , ind1)
if(b != 0):
    print("error index 2 : " , ind2)
print("final message sent : ",finalmessage)

#creating waveforms
waveform = bitstring_to_waveform(finalmessage, sample_rate, duration, frequency1, frequency0, amplitude)

#Normalize waveform to 16-bit PCM format
waveform = np.int16(waveform * 32767)

#Save waveform to a WAV file
filename = "output.wav"
with wave.open(filename, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  
    wf.setframerate(sample_rate)
    wf.writeframes(waveform.tobytes())

#Playback the generated audio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True)

#Play the waveform
stream.write(waveform.tobytes())

#Cleanup
stream.stop_stream()
stream.close()
p.terminate()
print(f"Audio has been saved to {filename} and played back.")