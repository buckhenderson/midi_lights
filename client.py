#client
import socket
import time
import pickle
import mido


HOST = '192.168.1.37'
PORT = 2031
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
ons = []
with mido.open_input('MIDI Matrix Encoder:MIDI Matrix Encoder MIDI 1 20:0') as inport:
    while True:
        for msg in inport:
            if hasattr(msg, 'note'):
                midi_in = (msg.type, msg.note - 21, msg.velocity)
                message = pickle.dumps(midi_in)
                s.send(message)
                if msg.type == 'note_on':
                    ons.append(msg)
                if msg.type == 'note_off':
                    ons = [x for x in ons if x.note != msg.note]
            if hasattr(msg, 'control'):
                midi_in = ('pedal', False if msg.value == 0 else True)
                message = pickle.dumps(midi_in)
                s.send(message)
            print(ons)
