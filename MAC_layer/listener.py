import keyboard,random
import generator as gen
import recording as rec
import time

# input

howManyMessage = int(input('Enter how many messages to send: '))

# message => frame
def frameGenerator(message):
    msgString = message["msg"]
    destMAC = message["destMAC"]
    crcPlusMessage = gen.encode_data(msgString)
    finalMsg = gen.addPreamble(crcPlusMessage , rec.MAC , destMAC)
    return finalMsg

# input queue
InitQueue = []
SendQueue = []

for i in range(howManyMessage):
    message = input(f"Enter message {i + 1}: ")
    parsedMsg = message.split()
    msgString = parsedMsg[0]
    destMAC = int(parsedMsg[1])
    if destMAC == -1 :
        #ignore this input
        continue
    InitQueue.append({"msg": msgString, "destMAC": destMAC}) 

# Function to handle key events
def on_key_event(e):
    if e.name in ['enter', 'return']: 
        if len(InitQueue) > 0:
            msg = InitQueue.pop(0) 
            msgString = msg["msg"]
            dest_MAC = msg["destMAC"]
            SendQueue.append(msg)  
            print(f"Message added to send queue : {msgString} to {dest_MAC}")
        else:
            print("You sent all the messages")
                
keyboard.on_press(on_key_event)

while True:
    waitTime = rec.DIFS + random.randrange(0,2 ** rec.N) * rec.BIT_INTERVAL
    print("wait time:" ,waitTime)
    carrier_busy = rec.carrierSense(waitTime)
    if(carrier_busy):
        msg = rec.listenMsg(rec.MAX_WAIT)
        info = rec.getInfo(msg)
        print("in while loop listened : ", msg)
        rec.infoPrint(info)
        if((info[0]) and (not info[1])):
            rec.sendACK(info[5],info[4])

    elif(len(SendQueue) == 0):
        continue
    else:
        msg = SendQueue[0]
        msgString = msg["msg"]
        destMAC = msg["destMAC"]
        gen.sendMsg(frameGenerator(msg))
        sent = rec.waitACK(destMAC,rec.DIFS)
        if sent:
            SendQueue.pop(0)
        else:
            print("Transmission failed. Trying again after some time")
            continue
