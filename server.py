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
global ons
ons = []
global pedal
pedal = False
global kills
kills = []
global last_input
last_input = time.time()

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


global strip
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

def led():
    print('starting led')
    global strip
    print('running begin()')
    strip.begin()
    try:
        global stop
        global ons
        global pedal
        global kills
        print('entering try')
        while True and not stop:
            notes = [x[1] for x in ons]
            kill_notes = [i for i in range(strip.numPixels()) if i not in notes]
            for i in kill_notes:
                strip.setPixelColor(i, Color(0, 0, 0))
            for item in ons:
                new_color = fade(item[3], item[4], SECONDS)
                strip.setPixelColor(item[1], Color(new_color[0], new_color[1], new_color[2]))
            strip.show()

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


def midio():
    conn, addr = s.accept()
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    print('Connected by', addr)
    global stop
    global ons
    global pedal
    global kills
    global last_input
    try:
        while True and not stop:
            message = conn.recv(1024)
            midi_in = pickle.loads(message)
            if midi_in:
                last_input = time.time()
                # print(midi_in)
                if midi_in[0] == 'note_on':
                    new_midi_in = (midi_in[0], midi_in[1], midi_in[2], color_map(midi_in[2]), midi_in[3])
                    ons.append(new_midi_in)
                if midi_in[0] == 'note_off':
                    kills.append(midi_in[1])
                if midi_in[0] == 'pedal':
                    pedal = midi_in[1]
                if not pedal:
                    ons = [x for x in ons if x[1] not in kills]
                    kills = []
            print(ons)
        s.close()
    except:
        print('closing')
        s.close()


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, idle_monitor, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        if not idle_monitor:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(0, 0, 0))
                strip.show()
            break
        time.sleep(wait_ms/1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)


def idle():
    global last_input
    global strip
    while True:
        idle_monitor = time.time() - last_input > 10
        while idle_monitor:
            rainbow(strip, idle_monitor)
            idle_monitor = time.time() - last_input > 10
        while not idle_monitor:
            pass


try:
    midi_thread = threading.Thread(target=midio)
    midi_thread.start()
    led_thread = threading.Thread(target=led)
    led_thread.start()
    idle_thread = threading.Thread(target=idle)
    idle_thread.start()
except:
    s.close()
    stop = True