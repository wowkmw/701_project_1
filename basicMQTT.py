from mqtt import MQTTClient
import ubinascii
import time
import pycom
import machine
from machine import UART
import parserGen

# BEGIN SETTINGS
RANDOMS_INTERVAL = 5000 # milliseconds

last_random_sent_ticks = 0  # milliseconds


AIO_CLIENT_ID = "Charles"

AIO_SERVER = "203.101.227.137"

AIO_PORT = 1883

AIO_USER = "qut"

AIO_KEY = "qut"

AIO_CONTROL_FEED = "fipy/test"

AIO_RANDOMS_FEED = "fipy/randoms"

 


uart2 = UART(1, baudrate = 115200, pins = ('P3','P4'))
uart2.init(115200, bits = 8, parity = None, stop = 1)
parsedReadings = parserGen.output(uart2)


# FUNCTIONS

# Function to respond to messages from Adafruit IO

def sub_cb(topic, msg):          # sub_cb means "callback subroutine"

    print((topic, msg))          # Outputs the message that was received. Debugging use.

    if msg == b"ON":             # If message says "ON" ...

        pycom.rgbled(0xffffff)   # ... then LED on

    elif msg == b"OFF":          # If message says "OFF" ...

        pycom.rgbled(0x000000)   # ... then LED off

    else:                        # If any other message is received ...

        print("Unknown message") # ... do nothing but output that it happened.

 

# def random_integer(upper_bound):

#     return machine.rng() % upper_bound

 

def send_readings():

    # global last_random_sent_ticks

    # global RANDOMS_INTERVAL

 

    # if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):

    #     return; # Too soon since last one sent.

    try:
        latlon, velocity, gpsQ, height, GMT, PDOP, HDOP, VDOP, uniqsatNum = parsedReadings.__next__() 
    except:
        latlon = velocity = gpsQ = height = GMT = PDOP = HDOP = VDOP = uniqsatNum = 'Error occurred, please restart FiPy...'

    LatLonSpeed = "Laitude and Longitude: {0},  Speed: {1}".format(latlon, velocity)
    # some_number = random_integer(100)

    print("Publishing: {0} to {1} ... ".format(LatLonSpeed, AIO_RANDOMS_FEED), end='')

    try:

        client.publish(topic=AIO_RANDOMS_FEED, msg=str(LatLonSpeed))

        print("DONE")

    except Exception as e:

        print("FAILED")

    finally:

        last_random_sent_ticks = time.ticks_ms()

 

# Use the MQTT protocol to connect to Adafruit IO

client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)

 

# Subscribed messages will be delivered to this callback

client.set_callback(sub_cb)

client.connect()

client.subscribe(AIO_CONTROL_FEED)

print("Connected to %s, subscribed to %s topic" % (AIO_SERVER, AIO_CONTROL_FEED))



pycom.rgbled(0x00ff00) # Status green: online to Adafruit IO

 

try:                      # Code between try: and finally: may cause an error

                          # so ensure the client disconnects the server if

                          # that happens.

    while 1:              # Repeat this loop forever

        client.check_msg()# Action a message if one is received. Non-blocking.

        send_readings()     # Send current GNSS readings

        time.sleep(5)

finally:                  # If an exception is thrown ...

    client.disconnect()   # ... disconnect the client and clean up.

    client = None

    wlan.disconnect()

    wlan = None

    pycom.rgbled(0x000022)# Status blue: stopped