import network
import pycom

if __name__=='__main__':
    wlan = network.WLAN()
    # reconfigure wifi
    wlan.init(mode=network.WLAN.AP, ssid='testm8l701', auth=(network.WLAN.WPA2, 'testm8l701'), channel=1, antenna=network.WLAN.INT_ANT)
    pycom.heartbeat(False) # turn off led blinking
    pycom.rgbled(0x007f7f) #light blue
    print(">>FiPy set to AP mode<<")
    import allInOne
 
    