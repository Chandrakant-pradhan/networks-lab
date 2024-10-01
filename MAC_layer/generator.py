import numpy as np
import pyaudio
import wave

#Parameters for the audio
sample_rate = 88200  
duration = 0.5      #change this!    
frequency1 = 12000  #change this!
frequency0 = 6000  #change this!
frequencyx = 50
amplitude = 0.5    #change this!
GENERATOR = "010111010111"

#num to string
def decTobitstring(n , noOfBits):
    str = ""
    while(n > 0):
        if(n%2 == 0):
            str += '0'
        else:
            str += '1'
        n = n // 2
    
    length = len(str)
    str += "0"*(noOfBits-length)
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
def encode_data(data):
    appended_data = data + '0'*(len(GENERATOR)-1)
    remainder = mod2div(appended_data, GENERATOR)
    crc = remainder
    return data + crc

#adding the preamble
def addPreamble(bitstring , senderMAC , destMAC):
    #+4 for including the length of the 2 bit mac addresses
    message = "101010101010101011" + decTobitstring(len(bitstring) + 4 , 5) + decTobitstring(int(senderMAC) , 2) + decTobitstring(int(destMAC) , 2) + bitstring
    return message

#Convert bitstring to waveform
def bitstring_to_waveform(bitstring, sample_rate, duration, freq1, freq0, freqx, amplitude):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform_parts = []
    for bit in bitstring:
        if bit == '1':
            waveform_part = amplitude * np.sin(2 * np.pi * freq1 * t)
        elif bit == '0':
            waveform_part = amplitude * np.sin(2 * np.pi * freq0 * t)
        elif bit == 'x':
            waveform_part = amplitude * np.sin(2 * np.pi * freqx * t)

        waveform_parts.append(waveform_part)
    
    waveform = np.concatenate(waveform_parts)
    return waveform


def convertMessage(message):
    result = ""
    for bit in message:
        result += f"x{bit}"
    result += "x"
    return result

#send message
def sendMsg(message):
    print(message)
    message = convertMessage(message)
    waveform = bitstring_to_waveform(message, sample_rate, duration, frequency1, frequency0 , frequencyx, amplitude)
    waveform = np.int16(waveform * 32767)  
    # filename = "output(12000-6000)_test2.wav"
    # with wave.open(filename, 'wb') as wf:
    #     wf.setnchannels(1)
    #     wf.setsampwidth(2)  
    #     wf.setframerate(sample_rate)
    #     wf.writeframes(waveform.tobytes())
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    output=True)
    
    stream.write(waveform.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()