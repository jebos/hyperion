import hyperion
import colorsys
import socket
 


#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

# import required modules
import RPi.GPIO as GPIO
import time

# define GPIO pin with button
GPIOFrontLight = 13
GPIOSwitchAmbianceMode = 11
GPIODimmer = 15

# main function
def main():
  try:
    # use GPIO pin numbering convention
    GPIO.setmode(GPIO.BOARD)

    # set up GPIO pin for input
    GPIO.setup(GPIOFrontLight, GPIO.IN)
    GPIO.setup(GPIOSwitchAmbianceMode, GPIO.IN)
    GPIO.setup(GPIODimmer, GPIO.IN)

    GPIO.setup(GPIOFrontLight, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(GPIOSwitchAmbianceMode, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(GPIODimmer, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


    frontLightStatus = 0  # 0 = off , 1 = on
    ambianceLightStatus = 0 # 0 = off, 1 = on

    ambianceMode = 0 # 0 = normal ambiance light , 1 = tv ambiance mode

    dimmerValue = 10 # 0 to 10

    UDP_IP = ""
    UDP_PORT = 8888

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(0.3)
    
    ledDataWandOn = bytearray()
    ledDataLampenOn = bytearray()
    ledDataWandOff = bytearray()
    ledDataLampenOff = bytearray()
    hsv = colorsys.rgb_to_hsv(250/255.0, 1.0, 158.0/255.0)
    hsvFront = colorsys.rgb_to_hsv(250.0/255.0, 1.0, 158.0/255.0)


    for i in range(1,152):
      rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1]*2, 1)
      ledDataWandOn += bytearray((int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))
      ledDataWandOff += bytearray((0,0,0))
	 
    for i in range(1,61):
      rgb = colorsys.hsv_to_rgb(hsvFront[0], hsvFront[1]*2, hsvFront[2])
      ledDataLampenOn += bytearray((int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))
      ledDataLampenOff += bytearray((0,0,0))
	
    while not hyperion.abort():
      # get GPIO value
      if GPIO.input(GPIOSwitchAmbianceMode) and ambianceMode <> 1:
        ambianceMode = 1
	time.sleep(0.2)
        print("Button 2  pressed")

      if not GPIO.input(GPIOSwitchAmbianceMode) and ambianceMode <> 0:
        ambianceMode = 0
        ambianceLightStatus = 0
	time.sleep(0.2)
        print("Button 2 released")

		
      if GPIO.input(GPIOFrontLight) and frontLightStatus <> 1:
        frontLightStatus = 1
	time.sleep(0.2)
        print("Button 1  pressed")

      if not GPIO.input(GPIOFrontLight) and frontLightStatus <> 0:
        frontLightStatus = 0
	time.sleep(0.2)
        print("Button 1 released")
    
    
      if GPIO.input(GPIODimmer):
        print("DIMMER 1")        

        timeCounter = 0
        
        if GPIO.input(GPIODimmer) and ambianceLightStatus == 0:
          print("Light on")
          ambianceLightStatus = 1
          ledData = ledDataWandOn

          if frontLightStatus == 1:
            ledData = ledData + ledDataLampenOn
          else:
            ledData = ledData + ledDataLampenOff

          hyperion.setColor(ledData)


        time.sleep(0.4)

        while GPIO.input(GPIODimmer):
          timeCounter = timeCounter + 1
          print("TIME COUNTER")
          if timeCounter > 10:
            ambianceLightStatus = 0

            ledData = ledDataWandOff

            if frontLightStatus == 1:
              ledData = ledData + ledDataLampenOn
            else:
              ledData = ledData + ledDataLampenOff

            hyperion.setColor(ledData)

 #           print("Light off")
          
          time.sleep(0.1)
        
        if ambianceLightStatus == 1 and timeCounter <=10:
          print("DIMMING")
          ledDataWandOn = bytearray()
          dimmerValue = dimmerValue - 1

          if dimmerValue == -1:
	    dimmerValue = 10

          for i in range(1,152):
      	    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1]*2, dimmerValue/10.0)
            ledDataWandOn += bytearray((int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))
          
        print("Dimmdone")

      ledData = bytearray()

      sleepTime = 0.1

      if ambianceMode == 1:
        srgb = bytearray(152*3)
        
        try:
          number,addr = sock.recvfrom_into(srgb) # buffer size is 
          ledDataServer = bytearray()
          for i in range(1, number-3, 3): 
            ledDataServer += bytearray((srgb[i+2], srgb[i], srgb[i+1]))
          ledData = ledData + ledDataServer        
          sleepTime = 0.01
        except socket.timeout:
          ledData = ledData + ledDataWandOff    

      else:

        if ambianceLightStatus == 1:
          ledData = ledData + ledDataWandOn
        else:
          ledData = ledData + ledDataWandOff

      if frontLightStatus == 1:
	ledData = ledData + ledDataLampenOn
      else:
        ledData = ledData + ledDataLampenOff   
           
      hyperion.setColor(ledData)
	  
      # wait 100ms
      time.sleep(sleepTime)
	  
	
	  
  # reset GPIO settings if user pressed Ctrl+C
  except KeyboardInterrupt:
    print("Execution stopped by user")
    GPIO.cleanup()

if __name__ == '__main__':
  main()




