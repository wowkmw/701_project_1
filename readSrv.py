from microWebSrv import MicroWebSrv
import parserGen
import pycom
import time
from machine import UART
import sys


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
				Choice: type 'yes' to switch to MQTT mode...<input type="text" name="status"><br />
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
    try:
        if status == "yes":
            print("switching...")
            # srv.Stop() #the web server stopped, but the fipy also stopped responding
            pycom.rgbled(0xff0000)
            time.sleep(1)
            sys.exit(0)
    except:
        pycom.rgbled(0x00ff00)
        time.sleep(1)
        srv.Stop()
        time.sleep(1)
        import modeSwitch
        


uart = UART(1, baudrate = 115200, pins = ('P3','P4'))
uart.init(115200, bits = 8, parity = None, stop = 1)
parsedReadings = parserGen.output(uart)


routeHandlers = [ ( '/read', 'GET',  _httpHandlerNEOGet1s ),
                ( "/test",	"GET",	_httpHandlerTestGet ),
                ( "/test",	"POST",	_httpHandlerTestPost )]
srv = MicroWebSrv(routeHandlers=routeHandlers, webPath = '/flash/www/')
pycom.rgbled(0xff0000)
time.sleep(1)
srv.Start(threaded = True)
pycom.rgbled(0x00ff00)
print("WebServer started.")