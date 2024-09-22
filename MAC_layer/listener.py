import numpy as np
import pyaudio
import wave
import signal
import time
import keyboard

# message => frame
def frameGenerator(message):
    return message  

# input
MAC = int(input('Enter the device MAC address: '))
howManyMessage = int(input('Enter how many messages to send: '))

# input queue
InitQueue = []
SendQueue = []

for i in range(howManyMessage):
    message = input(f"Enter message {i + 1}: ")
    frame = frameGenerator(message)
    InitQueue.append([frame, i + 1]) 

# Function to handle key events
def on_key_event(e):
    if e.name in ['enter', 'return']: 
        if len(InitQueue) > 0:
            msg = InitQueue[0][0]  
            msgIdx = InitQueue[0][1] 
            SendQueue.append(msg) 
            InitQueue.pop(0) 
            print(f"Message {msgIdx} : {msg} added to sending queue")
        else:
            print("You sent all the messages")

keyboard.on_press(on_key_event)

while True:
    time.sleep(5) 
    print("hi")
