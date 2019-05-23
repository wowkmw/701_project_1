import time
import pycom

def dataParse(reading):
    def parseLat(temp, temp2):
        try:
            raw = list(str(int(float(temp)*10000000)))
            degree = float(raw[0]+raw[1])
            minutes = float(raw[2]+raw[3])/60
            seconds = float(raw[4]+raw[5]+raw[6]+raw[7]+raw[8]+raw[9]+raw[10])/100000/(60*60)
            dms = str(degree + minutes + seconds)
            dirr = temp2
            Lat = str(dirr+dms)
            return Lat
        except:
            return 'N/A'
    def parseLon(temp, temp2):
        try:
            raw = list(str(int(float(temp)*10000000)))
            degree = float(raw[0]+raw[1]+raw[2])
            minutes = float(raw[3]+raw[4])/60
            seconds = float(raw[5]+raw[6]+raw[7]+raw[8]+raw[9]+raw[10]+raw[11])/100000/(60*60)
            dms = str(degree + minutes + seconds)
            dirr = temp2
            Lon = str(dirr+dms)
            return Lon
        except:
            return 'N/A'
    def GPSQ(arg):
        try:
            switcher = {
                0: "Fix not valid",
                1: "GPS fix",
                2: "Differential GPS fix, OmniSTAR VBS",
                4: "Real-Time Kinematic, fixed integers",
                5: "Real-Time Kinematic, float integers, OmniSTAR XP/HP or Location RTK",
            }
            return switcher.get(arg, "Not available")
        except:
            return 'N/A'
    def timeP(arg):
        try:
            raw = list(arg[1])
            hh = raw[0] + raw[1]
            mm = raw[2] + raw[3]
            ss = raw[4] + raw[5]
            hms = hh+":"+mm+":"+ss
            return hms
        except:
            return 'N/A'
    def countSats(arg1, arg2):
        try:
            sat1 = arg1[3:15]
            sat2 = arg2[3:15]
            #sat3 = arg3[3:15]
            allsat = sat1 + sat2
            uniqsat = set(allsat)
            uniqsatNum = len(uniqsat) - 1
            return uniqsatNum
        except:
            return 'N/A'
    def velo(arg):
        if arg[7]:
            velocity = str(arg[7] + ' knots')
            return velocity
        else:
            return 'N/A'
    def height(arg):
        if arg[9]:
            height = str(arg[9] + ' meters')
            return height
        else:
            return 'N/A'
    def PHV(arg):
        try:
            PDOP = arg[15]
            HDOP = arg[16]
            VDOP = arg[17].split('*')[0]
            return PDOP, HDOP, VDOP
        except:
            PDOP = HDOP = VDOP = 'N/A'
            return PDOP, HDOP, VDOP
    try:
        temp1 = reading[0].split(',') #rmc
        #temp2 = reading[1].split(',') #vtg, duplicate information
        temp3 = reading[2].split(',') #gga
        temp4 = reading[3].split(',') #3~14 for satellites, gsa
        temp5 = reading[4].split(',') #15,16,17, gsa
        #temp6 = reading[5].split(',') #gsa third not available in neo m8l
        Lat = parseLat(temp1[3],temp1[4])
        Lon = parseLon(temp1[5],temp1[6])
        gpsQ = GPSQ(int(temp3[6]))
        LatLon = Lat +' ; '+ Lon
        velocity = velo(temp1)
        height = height(temp3)
        GMT = timeP(temp1)
        PDOP, HDOP, VDOP = PHV(temp5)
        uniqsatNum = countSats(temp4, temp5)
        return LatLon, velocity, gpsQ, height, GMT, PDOP, HDOP, VDOP, uniqsatNum
    except:
        LatLon = velocity = gpsQ = height = GMT = PDOP = HDOP = VDOP = uniqsatNum = "Sensor Error"
        return LatLon, velocity, gpsQ, height, GMT, PDOP, HDOP, VDOP, uniqsatNum

def output(UT):
    while True:
        pycom.rgbled(0xff6600) # yellow
        counter = 0
        tempStore = [] # store up to 5 reads, reset at each round
        flushCache = UT.readall() #flush cache on m8l to prevent erroneous readings
        while counter <= 4: # read the first five lines of raw data
            try:
                # keep reading data until the first stream of raw data is received
                data = UT.readline()
                if data:
                    decoded = data.decode("utf-8") #the raw reading from uart needs to be decoded
                    tempStore.append(decoded)
                    counter += 1
                    time.sleep(0.03) # avoid sensor overload
            except:
                pycom.rgbled(0xff0000) # red
                print("Error")    
        pycom.rgbled(0x00ff00)
        LatLon, velocity, gpsQ, height, GMT, PDOP, HDOP, VDOP, uniqsatNum = dataParse(tempStore) # parse decoded raw readings
        yield LatLon, velocity, gpsQ, height, GMT, PDOP, HDOP, VDOP, uniqsatNum # generate readings
