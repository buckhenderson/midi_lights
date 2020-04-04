# player
import socket
import time
import pickle
import mido
import os
import random

port2 = mido.open_output('test_port', virtual=True)

HOST = '192.168.1.36'
PORT = 2031
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

current_directory = os.getcwd()
jazz_directory = os.path.join(os.getcwd(), 'jazz_midis')
classical_directory = os.path.join(os.getcwd(), 'classical_midis')
jazz = [os.path.join(jazz_directory, x) for x in os.listdir(jazz_directory)]
classical = [os.path.join(classical_directory, x) for x in os.listdir(classical_directory)]
midis = jazz
midis.extend(classical)
random.shuffle(midis)

for midi in midis:
    ons = []
    for msg in mido.MidiFile(midi).play():
        print(msg)
        port2.send(msg)
        if hasattr(msg, 'note'):
            if msg.type == 'note_on' and msg.velocity != 0:
                this_type = 'on'
            else:
                this_type = 'off'
            this_note = 87 - (msg.note - 21)
            if hasattr(msg, 'velocity'):
                this_velocity = msg.velocity
            if hasattr(msg, 'value'):
                this_velocity = msg.value
            this_time = time.time()
            this_message = '{0:<3},{1:<2},{2:<3},{3:6f}'.format(this_type, this_note, this_velocity, this_time)
            print(this_message)
            this_message_s = pickle.dumps(this_message)
            s.send(this_message_s)
            if msg.type == 'note_on':
                ons.append(msg)
            if msg.type == 'note_off':
                ons = [x for x in ons if x.note != msg.note]
        if hasattr(msg, 'control'):
            if msg.control == 65:
                this_message = 'pedal, {}                    '.format(0 if msg.value == 0 else 1)
                this_message_s = pickle.dumps(this_message)
                s.send(this_message_s)
                print(this_message)
        print(ons)