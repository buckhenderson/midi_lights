import client
import player


while True:
    print('loading piano_leds')
    print('mode?')
    print('1: manual')
    print('2: player')
    user_input = input()
    if user_input == '1':
        client.client()
    if user_input == '2':
        player.player_piano()
