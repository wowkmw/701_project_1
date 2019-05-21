import network
import time
import pycom
import machine

# setup as a station
wlan = network.WLAN(mode=network.WLAN.STA)
print("attempting to connect to hotspot...")
wlan.connect('TPU4G_L3TN', auth=(network.WLAN.WPA2, '56156271'))
time.sleep(5)
while not wlan.isconnected(): #retry every 5 seconds
    wlan.connect('TPU4G_L3TN', auth=(network.WLAN.WPA2, '56156271'))
    time.sleep(5)
time.sleep(10) #wait for ipconfig set-up
print(wlan.ifconfig()) #
pycom.rgbled(0xff00f4) #ligt purple, wifi connected
time.sleep(2)
# from machine import UART
# import parserGen
# uart = UART(1, baudrate = 115200, pins = ('P3','P4'))
# uart.init(115200, bits = 8, parity = None, stop = 1)
# parsedReadings = parserGen.output(uart)
import basicMQTT #starts minimal  bi-directional MQTT client