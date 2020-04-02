# server
# this section borrows heavily from https://github.com/jgarff/rpi_ws281x (Jeremy Garff)
# Author: Tony DiCola (tony@tonydicola.com)
import socket
import pickle
import time
import threading
import sys
import math

sys.path.append('/home/pi/rpi_ws281x/python')
from neopixel import *

global stop
stop = False
global ons
ons = []
global pedal
pedal = False
global kills
kills = []
global last_message_ts
last_message_ts = time.time()
global idle
idle = False

# LED strip configuration:
LED_COUNT = 88  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

SECONDS = 10  # this constant controls the number of seconds to fade to black
IDLE_TIME = 10  # time to go to idle


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

def multiplier():
    seconds = time.time() % 60
    return_value = abs(math.sin(seconds/(30/math.pi)))
    return return_value


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    global idle
    global last_message_ts
    global ons
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
            idle = (time.time() - last_message_ts) > IDLE_TIME and len(ons) == 0
            if not idle:
                break
        if not idle:
            break
        strip.show()
        time.sleep(wait_ms/1000.0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    multi = multiplier()
    if pos < 85:
        return Color(int(pos * 3 * multi), int((255 - pos * 3) * multi), 0)
    elif pos < 170:
        pos -= 85
        return Color(int((255 - pos * 3) * multi), 0, int((pos * 3) * multi))
    else:
        pos -= 170
        return Color(0, int(pos * 3 * multi), int((255 - pos * 3) * multi))


HOST = '192.168.1.37'
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
        global ons
        global pedal
        global kills
        global last_message_ts
        global idle
        while not stop:
            while not idle and not stop:
                notes = [x[1] for x in ons]
                kill_notes = [i for i in range(strip.numPixels()) if i not in notes]
                for i in kill_notes:
                    strip.setPixelColor(i, Color(0, 0, 0))
                for item in ons:
                    new_color = fade(item[3], item[4], SECONDS)
                    strip.setPixelColor(item[1], Color(new_color[0], new_color[1], new_color[2]))
                strip.show()
                # the initial step into idle requires that it be at approximately the minute mark
                idle = (time.time() - last_message_ts) > IDLE_TIME and len(ons) == 0 and abs(time.time() % 60) < 1
            while idle and not stop:
                rainbow(strip)
                idle = (time.time() - last_message_ts) > IDLE_TIME and len(ons) == 0
                if not idle:
                    for i in range(strip.numPixels()):
                        strip.setPixelColor(i, Color(0, 0, 0))
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
    except:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()


def fade(tup, input_time, seconds):
    multiplier = 1 - min((time.time() - input_time), seconds) / seconds
    new_tup = tuple([int(multiplier*x) for x in tup])
    return new_tup


def remove_dupes(lst):
    new_lst = sorted(lst, key=lambda x: (x[1], -x[4]))
    output = list()
    output_filter = list()
    for item in new_lst:
        if item[1] not in output_filter:
            output.append(item)
            output_filter.append(item[1])
    return output


def midio():
    conn, addr = s.accept()
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    print('Connected by', addr)
    global stop
    global ons
    global pedal
    global kills
    global last_message_ts
    try:
        while not stop:
            this_message_s = conn.recv(38)
            this_message = pickle.loads(this_message_s)
            last_message_ts = time.time()
            if this_message:
                message_list = [word.strip() for word in this_message.split(',')]
                this_type = message_list[0]
                if this_type == 'on':
                    this_note = int(message_list[1])
                    this_velocity = int(message_list[2])
                    this_time = float(message_list[3])
                    new_midi_in = (this_type, this_note, this_velocity, color_map(this_velocity), this_time)
                    ons.append(new_midi_in)
                    ons = remove_dupes(ons)
                if this_type == 'off':
                    this_note = int(message_list[1])
                    kills.append(this_note)
                if this_type == 'pedal':
                    pedal = int(message_list[1])
                if not pedal:
                    ons = [x for x in ons if x[1] not in kills]
                    ons = remove_dupes(ons)
                    kills = []
            print(ons)
        s.close()
    except:
        stop = True
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
