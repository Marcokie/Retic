# Import Libraries
import network
import time
import conf
# Set parameters
ssid = conf.wifi["ssid"]
pwd = conf.wifi["pwd"]
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
            time.sleep(0.5)
    print('network config:', sta_if.ifconfig())
# main
def main():
    do_connect(ssid,pwd)
main()