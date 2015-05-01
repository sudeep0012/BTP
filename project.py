from gps import *
import time
import threading
import math
import RPi.GPIO as GPIO
import ConfigParser
import subprocess

GPIO.setmode(GPIO.BCM)
GPIO.setup(25,GPIO.IN)
config=ConfigParser.ConfigParser()
config.read('/home/pi/recording/values.ini')
t1=config.getfloat('SectionOne','initial wait time')
t2=config.getfloat('SectionOne','audio recording time')
t3=config.getfloat('SectionOne','loop time')
time.sleep(t1)
class GpsController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.running = False
    
    def run(self):
        self.running = True
        while self.running:
            # grab EACH set of gpsd info to clear the buffer
            self.gpsd.next()

    def stopController(self):
        self.running = False
  
    @property
    def fix(self):
        return self.gpsd.fix

    @property
    def utc(self):
        return self.gpsd.utc

    @property
    def satellites(self):
        return self.gpsd.satellites



if __name__ == '__main__':
    # create the controller
    gpsc = GpsController() 
    try:
        # start controller
        gpsc.start()
        while True:
            a=gpsc.utc
            b=gpsc.fix.latitude
            c=gpsc.fix.longitude
            d=gpsc.fix.altitude
            x=gpsc.fix.speed
            file=open("/home/pi/recording/data/%s-%f,%f.txt" %(a,b,c),"w")
            file.write("altitude (m)= %f" %(d))
            file.write('\n')
            file.write("speed (m/s)= %f" %(x))
            inputvalue=GPIO.input(25)
            if(inputvalue == True):
              record= ["arecord", "-f", "cd", "-d", "%f" %(t2),"-D", "plughw:0","/home/pi/recording/data/%s-%f,%f.wav" %(a,b,c)]
              p=subprocess.Popen(record, stdout=subprocess.PIPE)
            time.sleep(t3)
            
    
    #Ctrl C
    except KeyboardInterrupt:
        print "User cancelled"

    finally:
        print "Stopping gps controller"
        gpsc.stopController()
        #wait for the tread to finish
        gpsc.join()

    file.close()      
    print "Done"
