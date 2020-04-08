# client
import socket
import time
import pickle
import mido


def client():
    try:
        ons = []
        with mido.open_input('MIDI Matrix Encoder:MIDI Matrix Encoder MIDI 1 20:0') as inport:
            while True:
                for msg in inport:
                    print(msg)
                    if hasattr(msg, 'note'):
                        if msg.type == 'note_on':
                            this_type = 'on'
                        else:
                            this_type = 'off'
                        this_note = 87 - (msg.note - 21)
                        this_velocity = msg.velocity
                        this_time = time.time()
                        this_message = '{0:<3},{1:<2},{2:<3},{3:6f}'.format(this_type, this_note, this_velocity, this_time)
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
                    print(ons)
    except KeyboardInterrupt:
        print('exiting client')
