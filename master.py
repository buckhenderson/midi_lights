import client
import player
import socket

HOST = '192.168.1.37'
PORT = 2031
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


while True:
    print('loading piano_leds')
    print('mode?')
    print('1: manual')
    print('2: player')
    print('3: exit')
    user_input = input()
    if user_input == '1':
        print('selecting client')
        client.client(s)
    if user_input == '2':
        print('selecting player')
        player.player_piano(s)
    if user_input == '3':
        s.close()
        break
