# Import Libraries
import conf
import network
import utime
import machine
from machine import Pin
import ubinascii
from umqtt.simple import MQTTClient
import json

# Set global parameters
# Wifi params
my_ssid = conf.wifi["ssid"]
my_pwd = conf.wifi["pwd"]
# MQTT params
SERVER = conf.adafruit["server"]
TOPIC = conf.adafruit["topic"]
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
USER = bytearray(conf.adafruit["user"])
KEY = bytearray(conf.adafruit["key"])
# Board params
led = Pin(2, Pin.OUT, value=1)
# Set gpio dictionary
gpio = {}
for k,v in conf.zones.items():
    gpio[k] = [Pin(v, Pin.OUT,value=0),0]  # Dictionary of lists. [0] = assigned pin, [1] = timer minutes


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
        stop = True
    else:
        try:
            jmsg = json.loads(msg)  #load json message
            for k,v in jmsg.items():
                gpio[k][1] = v
            print(gpio)
        except Exception as e:
            print("mqqt message error: " + e)


# Main function
def main():
    # Initial setup
    stop = False
    # Subscribe to MQTT message
    c = MQTTClient(CLIENT_ID, SERVER, user=USER, password=KEY, port=1883)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(TOPIC)
    # [Re]connect Loop
    print(sta_if.isconnected())
    try:
        while not sta_if.isconnected():
            # Connect to wifi
            do_connect(my_ssid,my_pwd)
            print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC))
            while not stop:
                c.check_msg()  # execute call back to field timer requests
                for x in gpio.values():  # Set pin values
                    if x[1] > 0:
                        x[0].value(1)
                    else:
                        x[0].value(0)
                utime.wait(5)
                for x in gpio.values():  #decrease timers
                    x[1] = max(0,x[1]-5)
    except Exception as e:
        print(e)
    finally:
        c.disconnect()
