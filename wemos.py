# Import Libraries
import conf
import network
import utime
import machine
from machine import Pin
import ubinascii
from umqtt.simple import MQTTClient
import json
import webrepl


# Wifi params
my_ssid = conf.wifi["ssid"]
my_pwd = conf.wifi["pwd"]
# MQTT params
SERVER = conf.adafruit["server"]
TOPIC = conf.adafruit["topic"]
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
USER = bytearray(conf.adafruit["user"])
KEY = bytearray(conf.adafruit["key"])
# operation params
freq = conf.operation["freq"]
bf = conf.operation["blink_freq"]
safety = conf.operation["safety"]
# Set gpio dictionary
gpio = {}
for k,v in conf.zones.items():
    gpio[k] = [  # Dictionary to manage GPIO pins
        Pin(v, Pin.OUT,value=1),  # Pin
        0,  # wait time before timer starts
        0,  # timer time
        1   # toggle parameter
    ]


# functions
# Connect to wifi
sta_if = network.WLAN(network.STA_IF)
def do_connect(ssid,pwd):
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            utime.sleep_ms(200)
    print('network config:', sta_if.ifconfig())

# Setup Mqtt
def sub_cb(topic, msg):
    print((topic, msg))
    if msg == b'STOP':
        print("Start webrepl")
        webrepl.start()
    else:
        try:
            jmsg = json.loads(msg)  # load json message
            for k,v in jmsg.items():
                if k != "seq":  # non-series requests
                    if v == -1:  # toggle zone
                        gpio[k][2] = safety * gpio[k][3]
                        gpio[k][3] = 1 - gpio[k][3]
                    else:  # set zone to value
                        gpio[k][2] = min(v,safety)
            if "seq" in jmsg:
                wait = 0  # time to wait before timer starts
                for k,v in jmsg["seq"].items():  # serialise seq requests
                    gpio[k][1] = wait  # set wait
                    gpio[k][2] = min(v,safety)  # set timer
                    wait = wait + v  # wait sum of previous timer values
            print(gpio)
        except ValueError as e:
            return


# Main function
def main():
    # [Re]connect Loop
    while not sta_if.isconnected():
        # Connect to wifi
        do_connect(my_ssid,my_pwd)
        print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC))
    # Subscribe to MQTT message
    c = MQTTClient(CLIENT_ID, SERVER, user=USER, password=KEY, port=1883)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(TOPIC)
    # Board params
    blink = 0
    led = Pin(2, Pin.OUT, value=1)
    try:
        while 1:
            print("retic v1.2")
            c.check_msg()  # execute call back to field timer requests
            for x in gpio.values():  # Set pin values
                if x[2] > 0 and x[1] == 0:
                    x[0].value(0)
                else:
                    x[0].value(1)
            print(gpio)
            for x in range(int(freq/bf)):
                blink = 1 - blink
                led(blink)
                utime.sleep(bf)
                for x in gpio.values():  # decrease waits and timers
                    x[1] = max(0,x[1]-bf)
                    if x[1] == 0:
                        x[2] = max(0,x[2]-bf)
    except Exception as e:
        print(e)
    finally:
        c.disconnect()
