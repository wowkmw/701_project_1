# import os
# import readSrv
from network import WLAN
import pycom
# hahaha
# from machine import SD
# sd = SD()
# os.mount(sd, '/sd')
if __name__=='__main__':
    wlan = WLAN()
    wlan.init(mode=WLAN.AP, ssid='testf9p701', auth=(WLAN.WPA2, 'testf9p701'), channel=1, antenna=WLAN.INT_ANT)
    pycom.heartbeat(False)
    pycom.rgbled(0x007f7f)
    