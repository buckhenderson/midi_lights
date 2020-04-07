# player
import socket
import time
import pickle
import mido
import os
import random

def player_piano():

    try:
        port2 = mido.open_output('test_port', virtual=True)

        HOST = '192.168.1.37'
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

        these_dirs_0 = list(os.walk(current_directory))
        these_dirs_1 = [x[0] for x in these_dirs_0 if x[0] != current_directory and '.git' not in x[0] and '.idea' not in x[0]]
        song_dic = {}
        for directory in these_dirs_1:
            song_dic[directory] = {(i + 1): song for i, song in enumerate(os.listdir(directory))}
        directory_dic = {(i + 1): directory for i, directory in enumerate(song_dic)}

        print('player_piano!')
        user_input = 0
        while True and user_input != 'x':
            print('what would you like to play?')
            print('1: browse')
            print('2: classical')
            print('3: jazz')
            print('4: all')
            user_input = input()

            if user_input == '1':
                for directory in directory_dic:
                    print('{}: {}'.format(directory, directory_dic[directory]))
                print('0: back')
                user_input = input()
                this_directory = directory_dic[int(user_input)]
                for song in song_dic[this_directory]:
                    print('{}: {}'.format(song, song_dic[this_directory][song]))
                print('0: back')
                user_input = input()
                midis = [os.path.join(this_directory, song_dic[this_directory][int(user_input)])]

            if user_input == '2':
                midis = classical

            if user_input == '3':
                midis = jazz

            if user_input == '4':
                pass
            print(midis)

            for midi in midis:
                ons = []
                print(midi)
                for msg in mido.MidiFile(midi).play():
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
                        # print(this_message)
                        this_message_s = pickle.dumps(this_message)
                        s.send(this_message_s)
                        if this_type == 'on':
                            ons.append(msg)
                        if this_type == 'off':
                            ons = [x for x in ons if x.note != msg.note]
                    if hasattr(msg, 'control'):
                        if msg.control == 65:
                            this_message = 'pedal, {}                    '.format(0 if msg.value == 0 else 1)
                            this_message_s = pickle.dumps(this_message)
                            s.send(this_message_s)
                            # print(this_message)
                    print(ons)
    except KeyboardInterrupt:
        port2.close()
        print('exiting player_piano')
