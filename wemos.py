# Import Libraries
import utime
import conf
# Set parameters
my_ssid = conf.wifi["ssid"]
my_pwd = conf.wifi["pwd"]
# functions


# Connect to wifi
def do_connect(ssid,pwd):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            utime.sleep_ms(200)
    print('network config:', sta_if.ifconfig())


# Setup Mqtt


# main
def main(state):
    from machine import Pin
    do_connect(my_ssid,my_pwd)
    led = Pin(2, Pin.OUT, value=1)
    led.value(state)
    state = 1 - state
main(0)