from microWebSrv import MicroWebSrv
import parserGen
import pycom
import time
from machine import UART
import network
from mqtt import MQTTClient
import json	

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
        <body style="background-color: lightgrey; text-align: center;">
            <h1><b>===MODE SWITCH===</b></h1>
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
        <body style="background-color: lightgrey; text-align: center;">
            <h1><b>===MODE SWITCH===</b></h1>
            Choice = %s<br />
        </body>
    </html>
	""" % ( MicroWebSrv.HTMLEscape(status))
    httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "text/html",
								  contentCharset = "UTF-8",
								  content 		 = content )

    if status == "mqtt":
        print(">>MQTT mode selected<<")
        mf = open("status.txt", "w")
        mf.write("yes")
        mf.close()

def switchToParallelMQTT():
    # BEGIN SETTINGS
    AIO_CLIENT_ID = "Charles"
    AIO_SERVER = "203.101.227.137"
    AIO_PORT = 1883
    AIO_USER = "qut"
    AIO_KEY = "qut"
    AIO_CONTROL_FEED = "fipy/test"
    AIO_RANDOMS_FEED = "fipy/randoms"

    # Setup thingsboard connection
    THINGSBOARD_HOST = '203.101.225.130'
    QUT01_ACCESS_TOKEN = 'test12345'

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

    def send_readings():
        try:
            latlon, velocity, gpsQ, height, GMT, PDOP, HDOP, VDOP, uniqsatNum = parsedReadings.__next__() 
        except:
            latlon = velocity = gpsQ = height = GMT = PDOP = HDOP = VDOP = uniqsatNum = 'Error occurred, please restart FiPy...'

        gnssReadings = "Laitude and Longitude: {0},  Velocity: {1}, Orthometric height: {2}, Time in GMT: {3}, GPS Quality indicator: {4}, Number of active satellites: {5}, PDOP:{6} HDOP:{7} VDOP:{8}"\
            .format(latlon, velocity, gpsQ, height, GMT, uniqsatNum, PDOP, HDOP, VDOP)       

        if 'Error' in latlon:
            location = {'lat': latlon, 'lon': latlon}

        elif 'N/A' in latlon:
            location = {'lat': latlon, 'lon': latlon}

        else:
            temp1 = latlon.split(";")
            Lat = float(temp1[0].replace("S","-").replace("N",""))
            Lon = float(temp1[1].replace("E","").replace("W","-"))
            location = {'lat': float(Lat), 'lon': float(Lon)}
        
        try:
            print("Publishing: {0} to {1} ... ".format(gnssReadings, AIO_RANDOMS_FEED), end='')
            client.publish(topic=AIO_RANDOMS_FEED, msg=str(gnssReadings))
            print("DONE")
            time.sleep(0.5)
            client2.publish(topic='v1/devices/me/attributes', msg=json.dumps(location))
            print("coordinate sent: {0}".format(latlon))

        except Exception:
            print("FAILED")

        finally:
            print("------------------------------------------------------------------------------")

    client2 = MQTTClient(client_id="test", server=THINGSBOARD_HOST, port=1883, user=QUT01_ACCESS_TOKEN, password=QUT01_ACCESS_TOKEN, keepalive=60)

    #Connect to Thingsboard using default MQTT port and 60 seconds keepalive intervals
    client2.connect()

    print(">>>connected to things platform<<<")
    pycom.rgbled(0x00ff00) #green
    # Use the MQTT protocol to connect to Adafruit IO
    client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)

    # Subscribed messages will be delivered to this callback
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(AIO_CONTROL_FEED)
    print("Connected to %s, subscribed to %s topic" % (AIO_SERVER, AIO_CONTROL_FEED))
    pycom.rgbled(0x00ff00) # Status green: online to Adafruit IO  

    try:
        while True:              # Repeat this loop forever
            client.check_msg()# Action a message if one is received. Non-blocking.
            send_readings()     # Send current GNSS readings
            time.sleep(3)  # publish every 3 seconds

    except KeyboardInterrupt: 		# catches the ctrl-c command, which breaks the loop above
            print("Continuous polling stopped")

    finally:                  # If an exception is thrown ...
        client.disconnect()   # ... disconnect the client and clean up.
        client2.disconnect()
        client2 = None
        client = None
        global wlan # add globale so that wlan can be modified
        wlan.disconnect()
        wlan = None
        pycom.rgbled(0x000022) # Status blue: stopped
        print("MQTT stopped")

print(">>starting web server<<")
pycom.rgbled(0xff0000) #red
time.sleep(1)

uart = UART(1, baudrate = 115200, pins = ('P3','P4')) # create uart object
uart.init(115200, bits = 8, parity = None, stop = 1) # init reading
parsedReadings = parserGen.output(uart) # generator object yields parsed readings

# configure server
routeHandlers = [ ( '/read', 'GET',  _httpHandlerNEOGet1s ),
                ( "/test",	"GET",	_httpHandlerTestGet ),
                ( "/test",	"POST",	_httpHandlerTestPost )]
srv = MicroWebSrv(routeHandlers=routeHandlers, webPath = '/flash/www/')
time.sleep(0.25)
srv.Start(threaded = True) # start server
pycom.rgbled(0x00ff00) #green
print(">>local webServer started<<")
time.sleep(0.25)
mf = open("status.txt", "w") # use to determine mqtt switch
mf.close()
while True:
    time.sleep(1)
    condf = open("status.txt", "r")
    cond = condf.read()
    condf.close()
    if cond == "yes": # use to determine mqtt switch
        print(">>stopping server<<")
        pycom.rgbled(0xff0000) #red
        time.sleep(1)
        srv.Stop() #stop server
        print(">>local server stopped<<")
        time.sleep(1)
        break
    else:
        pass
print(">>changing WIFI mode<<")
# setup as a station
wlan = network.WLAN(mode=network.WLAN.STA)
print(">>attempting hotspot connection, FiPy is in station mode<<")
wlan.connect('TPU4G_L3TN', auth=(network.WLAN.WPA2, '56156271'))
time.sleep(5)
while not wlan.isconnected(): #retry every 5 seconds
    wlan.connect('TPU4G_L3TN', auth=(network.WLAN.WPA2, '56156271'))
    time.sleep(5)
print(">>waiting for IP and DNS configuration<<")
pycom.rgbled(0xff00f4) #ligt purple, wifi connected
while True: # ensure that hotspot's ip config is correctly set up
    ipCond = wlan.ifconfig()[1]
    if ipCond == '0.0.0.0':
        time.sleep(0.5)
        pass
    else:
        break
print(wlan.ifconfig())
print(">>connected to hotspot<<")
time.sleep(1)
switchToParallelMQTT()