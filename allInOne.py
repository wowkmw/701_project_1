from microWebSrv import MicroWebSrv
import parserGen
import pycom
import time
from machine import UART
import network
from mqtt import MQTTClient

def _httpHandlerNEOGet1s(httpClient, httpResponse):
    try:
        latlon, velocity, gpsQ, height, GMT, PDOP, HDOP, VDOP, uniqsatNum = parsedReadings.__next__() 
    except:
        latlon = velocity = gpsQ = height = GMT = PDOP = HDOP = VDOP = uniqsatNum = 'Error occurred, please restart FiPy...'
    second = 1000 
    httpResponse.WriteResponseOk(
        headers = ({'Cache-Control': 'no-cache'}),
        contentType = 'text/event-stream',
        contentCharset = 'UTF-8',
        content =   'retry: {0}\n'.format(second)+
                    'data: {0}<br/>\n'.format('Latitude and Longitude:') +
                    'data: {0}<br/><br/>\n'.format(latlon)+
                    'data: {0}<br/>\n'.format('Velocity:')+
                    'data: {0}<br/><br/>\n'.format(velocity)+
                    'data: {0}<br/>\n'.format('Orthometric height:')+
                    'data: {0}<br/><br/>\n'.format(height)+
                    'data: {0}<br/>\n'.format('Time in GMT:')+
                    'data: {0}<br/><br/>\n'.format(GMT)+
                    'data: {0}<br/>\n'.format('GPS Quality indicator:')+
                    'data: {0}<br/><br/>\n'.format(gpsQ)+
                    'data: PDOP:{0} HDOP:{1} VDOP:{2}<br/><br/>\n'.format(PDOP, HDOP, VDOP)+
                    'data: {0}<br/>\n'.format('Number of active satellites:')+
                    'data: {0}<br/><br/>\n\n'.format(uniqsatNum)
        )

def _httpHandlerTestGet(httpClient, httpResponse) :
	content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>MODE SWITCH</title>
        </head>
        <body>
            <h1><b>MODE SWITCH</b></h1>
            Your IP address = %s
            <br />
			<form action="/test" method="post" accept-charset="ISO-8859-1">
				Choice: type 'mqtt' to switch to MQTT mode...<input type="text" name="status"><br />
				<input type="submit" value="Submit">
			</form>
        </body>
    </html>
	""" % httpClient.GetIPAddr()
	httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )

def _httpHandlerTestPost(httpClient, httpResponse) :
    formData  = httpClient.ReadRequestPostedFormData()
    status = formData["status"]
    content   = """\
    <!DOCTYPE html>
    <html lang=en>
		<head>
			<meta charset="UTF-8" />
            <title>MODE SWITCH</title>
        </head>
        <body>
            <h1><b>MODE SWITCH</b></h1>
            Choice = %s<br />
        </body>
    </html>
	""" % ( MicroWebSrv.HTMLEscape(status))
    httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )

    if status == "mqtt":
        print("switching...")
        mf = open("status.txt", "w")
        mf.write("yes")
        mf.close()

def switchToMQTT1(readGen):
    # setup as a station
    wlan = network.WLAN(mode=network.WLAN.STA)
    print(">>attempting hotspot connection, FiPy is in station mode<<")
    wlan.connect('TPU4G_L3TN', auth=(network.WLAN.WPA2, '56156271'))
    time.sleep(5)
    while not wlan.isconnected(): #retry every 5 seconds
        wlan.connect('TPU4G_L3TN', auth=(network.WLAN.WPA2, '56156271'))
        time.sleep(5)
    time.sleep(10) #wait for ipconfig set-up
    print(wlan.ifconfig()) #
    print(">>connected to hotspot<<")
    pycom.rgbled(0xff00f4) #ligt purple, wifi connected
    time.sleep(2)

    # BEGIN SETTINGS

    AIO_CLIENT_ID = "Charles"

    AIO_SERVER = "203.101.227.137"

    AIO_PORT = 1883

    AIO_USER = "qut"

    AIO_KEY = "qut"

    AIO_CONTROL_FEED = "fipy/test"

    AIO_RANDOMS_FEED = "fipy/randoms"

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

        # if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):

        #     return; # Too soon since last one sent.

        try:
            latlon, velocity, gpsQ, height, GMT, PDOP, HDOP, VDOP, uniqsatNum = readGen.__next__() 
        except:
            latlon = velocity = gpsQ = height = GMT = PDOP = HDOP = VDOP = uniqsatNum = 'Error occurred, please restart FiPy...'

        LatLonSpeed = "Laitude and Longitude: {0},  Speed: {1}".format(latlon, velocity)

        print("Publishing: {0} to {1} ... ".format(LatLonSpeed, AIO_RANDOMS_FEED), end='')

        try:

            client.publish(topic=AIO_RANDOMS_FEED, msg=str(LatLonSpeed))

            print("DONE")

        except Exception:

            print("FAILED")

        finally:

            print("------------------------------------------------------------------------------")

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

        while True:              # Repeat this loop forever

            client.check_msg()# Action a message if one is received. Non-blocking.

            send_readings()     # Send current GNSS readings

            time.sleep(5)  # publish every 5 seconds

    finally:                  # If an exception is thrown ...

        client.disconnect()   # ... disconnect the client and clean up.

        client = None

        wlan.disconnect()

        wlan = None

        pycom.rgbled(0x000022)# Status blue: stopped

        print("MQTT stopped")

pycom.rgbled(0xff0000) #red
time.sleep(1)

uart = UART(1, baudrate = 115200, pins = ('P3','P4'))
uart.init(115200, bits = 8, parity = None, stop = 1)
parsedReadings = parserGen.output(uart)

routeHandlers = [ ( '/read', 'GET',  _httpHandlerNEOGet1s ),
                ( "/test",	"GET",	_httpHandlerTestGet ),
                ( "/test",	"POST",	_httpHandlerTestPost )]
srv = MicroWebSrv(routeHandlers=routeHandlers, webPath = '/flash/www/')
time.sleep(0.25)
srv.Start(threaded = True)
pycom.rgbled(0x00ff00) #green
print(">>local webServer started<<")
time.sleep(0.25)
mf = open("status.txt", "w")
mf.close()
while True:
    time.sleep(1)
    condf = open("status.txt", "r")
    cond = condf.read()
    condf.close()
    if cond == "yes":
        print(">>stopping server<<")
        pycom.rgbled(0xff0000) #red
        # uart.deinit()
        time.sleep(1)
        srv.Stop()
        print(">>local server stopped<<")
        time.sleep(1)
        switchToMQTT1(parsedReadings)
        break
    else:
        time.sleep(1)
