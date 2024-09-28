import keyboard
from generator import addPreamble , sendMsg , encode_data
import time

# input
MAC = int(input('Enter the device MAC address: '))
howManyMessage = int(input('Enter how many messages to send: '))

# message => frame
def frameGenerator(message):
    parsedMsg = message.split()
    msgString = parsedMsg[0]
    destMAC = parsedMsg[1]
    crcPlusMessage = encode_data(msgString)
    finalMsg = addPreamble(crcPlusMessage , MAC , destMAC)
    return finalMsg

# input queue
InitQueue = []
SendQueue = []

for i in range(howManyMessage):
    message = input(f"Enter message {i + 1}: ")
    parsedMsg = message.split()
    msgString = parsedMsg[0]
    destMAC = parsedMsg[1]
    if destMAC == -1 :
        #ignore this input
        continue
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
            print(f"Message added to send queue {msgIdx} : {msg}")
            sendMsg(msg)
        else:
            print("You sent all the messages")

keyboard.on_press(on_key_event)

while True:
    time.sleep(5)
    print("hi")
