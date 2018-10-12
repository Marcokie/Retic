# Import Libraries
import conf
import network
import utime
from machine import Pin
import ubinascii
from umqtt.simple import MQTTClient

# Set parameters
my_ssid = conf.wifi["ssid"]
my_pwd = conf.wifi["pwd"]
SERVER = conf.adafruit["server"]
TOPIC = conf.adafruit["topic"]


# functions
# Connect to wifi
def do_connect(ssid,pwd):
    sta_if = network.WLAN(network.STA_IF)
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


# Main function
def main():
    # Connect to wifi
    do_connect(my_ssid,my_pwd)

    # Print MQTT message
    print("Connecting to %s, subscribed to %s topic" % (SERVER, TOPIC))
    CLIENT_ID = ubinascii.hexlify(machine.unique_id())
    c = MQTTClient(CLIENT_ID, SERVER)
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(TOPIC)
    print("Connected to %s, subscribed to %s topic" % (SERVER, TOPIC))

    try:
        while 1:
            #micropython.mem_info()
            c.wait_msg()
    finally:
        c.disconnect()

    # Toggle LED
    led = Pin(2, Pin.OUT, value=1)
    led.value(state)
    state = 1 - state

# Run main function
if __name__ == __main__:
    main()