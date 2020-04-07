import client
import player


while True:
    print('loading piano_leds')
    print('mode?')
    print('1: manual')
    print('2: player')
    user_input = input()
    print('{}, {}'.format(user_input, type(user_input)))
    if user_input == '1':
        print('selecting client')
        client.client()
    if user_input == '2':
        print('selecting player')
        player.player_piano()
