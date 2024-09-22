import numpy as np
import pyaudio
import wave
import signal
import time

#message => frame
def frameGenerator(message):
    #message to frame
    return message

#input
MAC = int(input('Enter the device MAC address :'))
howManyMessage = int(input('Enter how many message to send :'))
InitQueue = []
for i in range(howManyMessage):
    message = input()
    frame = frameGenerator(message)
    InitQueue.append(frame)

def handle_sigint(signal_number, frame):
    print("Trigger received:", signal_number)

signal.signal(signal.SIGQUIT, handle_sigint)

#run indefinetely
while True:
    time.sleep(5)
    print("hi")
    



    

