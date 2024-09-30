import numpy as np
import pyaudio
from scipy.signal import get_window
import queue
import time

cnt = 0
# Parameters for recording
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels
RATE = 88200  # Sample rate
CHUNK = 1024  # Size of each audio chunk
Mymac = "01"
framesize_latter_part = 20

# Queue for receiving messages
recv_que = queue.Queue()

# Initialize PyAudio
p = pyaudio.PyAudio()

# Function to perform Goertzel frequency detection
def goertzel(samples, sample_rate, target_freq):
    # Calculate the normalized target frequency
    num_samples = len(samples)
    k = int(0.5 + (num_samples * target_freq) / sample_rate)
    omega = (2.0 * np.pi * k) / num_samples
    coeff = 2.0 * np.cos(omega)

    s_prev = 0.0
    s_prev2 = 0.0

    for sample in samples:
        s = sample + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s

    power = s_prev2 ** 2 + s_prev ** 2 - coeff * s_prev * s_prev2
    return power

# Function to process the audio stream and detect frequencies
def process_audio_stream(zero_freq, one_freq, duration=0.1):
    # Open audio stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Listening...")

    try:
        state = 0  # 0-waiting for preamble, 1 -> in preamble, 2-> preamble done look for macid 
        prevbit = -1  # -1 for '.', 0 for '0', 1 for '1'
        msg_in_progress = ""
        tomac = ""
        dotcount = 0
        cnt = 0
        start_time = time.time()
        ocnt = 0
        zcnt = 0
        dcnt=0
        while True:
            # Read audio chunk
            data = stream.read(CHUNK, exception_on_overflow=False)
            waveform = np.frombuffer(data, dtype=np.int16) / 32767.0

            # Use the Goertzel algorithm to detect energy at the '0' and '1' frequencies
            zero_energy = goertzel(waveform, RATE, zero_freq)
            one_energy = goertzel(waveform, RATE, one_freq)

            # Set a dynamic energy threshold for detecting presence of signals
            threshold = 1  # You can adjust this threshold based on environment
            
            # Compare the energies to decide if we have a '0', '1', or silence
            if one_energy > threshold and one_energy > zero_energy:
                ocnt += 1
            elif zero_energy > threshold and zero_energy > one_energy:
                zcnt += 1
            else:
                dcnt += 1
            if time.time() - start_time >= duration:

                # Calculate the detected signal
                if ocnt >= zcnt and ocnt > dcnt:
                    detected_signal = "0"
                elif zcnt > ocnt and zcnt > dcnt:
                    detected_signal = "1"
                else:
                    detected_signal = "."
                ocnt = 0
                zcnt = 0
                dcnt = 0
                # Print the detected signal
                print(detected_signal, end="", flush=True)

                # Implement the rest of your state machine logic based on the detected signal
                if detected_signal == ".":
                    prevbit = -1
                    dotcount += 1
                    if state == 4 and msg_in_progress != "":  # Message is done
                        recv_que.put(msg_in_progress)
                    state = 0  # Reset state
                    msg_in_progress = ""
                else:
                    if state == 0:  # Waiting for preamble
                        if dotcount >= 10:
                            dotcount = 0
                            state = 1
                            if detected_signal == "1":
                                prevbit = 1
                            else:
                                prevbit = 0
                    elif state == 1:  # In preamble
                        if detected_signal == "1":
                            if prevbit == 1:
                                state = 2
                                tomac = ""
                            else:
                                state = 0
                        else:
                            if prevbit == 1:
                                state = 1
                            else:
                                state = 0
                    elif state == 2:  # Preamble done, reading macid
                        if detected_signal == "1":
                            tomac += "1"
                            prevbit = 1
                        else:
                            tomac += "0"
                            prevbit = 0

                        if len(tomac) < 2:
                            state = 2
                        else:
                            if tomac == Mymac or tomac == "00":
                                msg_in_progress = ""
                                state = 3
                            else:
                                state = 0
                    elif state == 3:  # Reading message
                        if detected_signal == "1":
                            msg_in_progress += "1"
                            prevbit = 1
                        else:
                            msg_in_progress += "0"
                            prevbit = 0
                        if len(msg_in_progress) == framesize_latter_part:
                            state = 4  # Message done
                        else:
                            state = 3

                cnt += 1
                cur_time = time.time()
                if cur_time - start_time >= duration:
                    start_time = time.time()
                    cnt = 1

    except KeyboardInterrupt:
        pass
    finally:
        # Stop and close the stream
        stream.stop_stream()
        stream.close()

# Main entry point
if __name__ == "__main__":
    zero_freq = float(input("Enter the frequency for '0' (e.g., 3000 Hz): "))
    one_freq = float(input("Enter the frequency for '1' (e.g., 8000 Hz): "))
    duration = float(input("Enter the duration (in seconds) for real-time monitoring: "))

    # Start real-time audio processing
    process_audio_stream(zero_freq=zero_freq, one_freq=one_freq, duration=duration)

# Terminate PyAudio when done
p.terminate()