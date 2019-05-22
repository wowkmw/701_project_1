import network
import pycom
# from machine import SD
# sd = SD()
# os.mount(sd, '/sd')
if __name__=='__main__':
    wlan = network.WLAN()
    wlan.init(mode=network.WLAN.AP, ssid='testf9p701', auth=(network.WLAN.WPA2, 'testf9p701'), channel=1, antenna=network.WLAN.INT_ANT)
    pycom.heartbeat(False)
    pycom.rgbled(0x007f7f) #light blue
    print(">>FiPy set to AP mode<<")
    import allInOne
 
    