#client
import socket
import time
import pickle
import mido
HOST='192.168.1.36'
PORT=2019
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
this_list = []
velocities = []
with mido.open_input('MIDI Matrix Encoder:MIDI Matrix Encoder MIDI 1 20:0') as inport:
    while True:
        for msg in inport:
            midi_in = (msg.type, msg.note - 21, msg.velocity)
            velocities.append(midi_in[2])
            set_velocities = set(velocities)
            velocities = [x for x in set_velocities]
            print(sorted(velocities))
            # print(midi_in)
            message = pickle.dumps(midi_in)
            s.send(message)
            if msg.type == 'note_on':
                this_list.append(msg)
            if msg.type == 'note_off':
                this_list = [x for x in this_list if x.note != msg.note]
            print(this_list)


# try:
#     while True:
#         y = [1, 2, 3]
#         message = pickle.dumps(y)
#         s.send(message)
#         time.sleep(1)
# except:
#     s.close()

