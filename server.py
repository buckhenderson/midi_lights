# server
import socket
import pickle
import time
import threading
import sys

sys.path.append('/home/pi/rpi_ws281x/python')
from neopixel import *

global stop
stop = False
global this_list
this_list = []

# LED strip configuration:
LED_COUNT = 150  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53


def color_map(value):
    # colors are GRB for some reason
    if value == 0:
        return (0, 0, 0)
    if value < 10:
        return (0, 0, 255)
    if value < 20:
        return (102, 0, 255)
    if value < 35:
        return (144, 0, 255)
    if value < 40:
        return (174, 0, 255)
    if value < 50:
        return (198, 0, 255)
    if value < 60:
        return (220, 0, 192)
    if value < 70:
        return (240, 0, 115)
    if value < 75:
        return (255, 0, 0)
    if value < 80:
        return (228, 134, 0)
    if value < 85:
        return (199, 182, 0)
    if value < 90:
        return (167, 215, 0)
    if value < 100:
        return (130, 238, 0)
    if value < 100:
        return (86, 251, 0)
    else:
        return (0, 255, 0)


HOST = '192.168.1.36'
PORT = 2031
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)


def led():
    print('starting led')
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    print('running begin()')
    strip.begin()
    try:
        global stop
        global this_list
        print('entering try')
        while True and not stop:
            notes = [x[1] for x in this_list]
            kill_notes = [i for i in range(strip.numPixels()) if i not in notes]
            for i in kill_notes:
                strip.setPixelColor(i, Color(0, 0, 0))
            for item in this_list:
                strip.setPixelColor(item[1], Color(item[3][0], item[3][1], item[3][2]))
            strip.show()

        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
    except:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()


def midio():
    conn, addr = s.accept()
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    print('Connected by', addr)
    global stop
    global this_list
    try:
        while True and not stop:
            message = conn.recv(1024)
            midi_in = pickle.loads(message)
            if midi_in:
                # print(midi_in)
                if midi_in[0] == 'note_on':
                    new_midi_in = (midi_in[0], midi_in[1], midi_in[2], color_map(midi_in[2]))
                    this_list.append(new_midi_in)
                if midi_in[0] == 'note_off':
                    this_list = [x for x in this_list if x[1] != midi_in[1]]
            print(this_list)
        s.close()
    except:
        print('closing')
        s.close()


try:
    midi_thread = threading.Thread(target=midio)
    midi_thread.start()
    led_thread = threading.Thread(target=led)
    led_thread.start()
except:
    s.close()
    stop = True