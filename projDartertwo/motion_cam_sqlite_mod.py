import cv2
import os
from datetime import datetime
import sqlite3
from picamera2 import Picamera2
import time

import board
import busio
import digitalio
import subprocess
from PIL import Image, ImageDraw, ImageFont
import PIL
import adafruit_ssd1306
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

WIDTH = 128
HEIGHT = 64
BORDER = 5
LOOPTIME = 1.0

oled_reset = digitalio.DigitalInOut(board.D4)

i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

#con = sqlite3.connect('/home/pi/website/instance/logs1.db')    #change the file path of the path where "data.db is present"
 
# create cursor object
#cur = con.cursor()

# Initialize the video capture object

# Define the background subtractor object (change the parameters as needed)
fgbg = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=16, detectShadows=True)

# Variables for motion detection
motion_detected = False
motion_frames = 0
t= ""
st= ""
prev_time = ""
x_old = 0

oled.fill(0)
oled.show()

image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

font1 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
font2 = ImageFont.truetype('DejaVuSansMono.ttf', 16)
draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

while True:
    # Read a frame from the video capture
    con = sqlite3.connect('/var/www/application/instance/logs1.db')            #change the file path of the path where "data.db is present"

 
# create cursor object
    cur = con.cursor()

   
    
    frame = picam2.capture_array()
    #frame = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # Apply background subtraction to the frame
    fgmask = fgbg.apply(frame)

    # Find contours of the moving objects
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Process each contour
    for contour in contours:
        # Ignore small contours (adjust the threshold as needed)
        if cv2.contourArea(contour) > 1000:
            # Draw a bounding box around the contour
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Set motion detected flag and increment motion frames counter
            motion_detected = True
            motion_frames += 1

    # Display the resulting frame
    #cv2.imshow('Motion Detection', frame)

    # Check if motion is detected for a certain number of frames
    try:
        with open("/var/www/application/trigger.log", 'r') as f:              #change the file path of the path where "trigger.log is present"
            r = f.read()
        st, t = r.split("/")
    except:
        pass

    if t == prev_time:
        pass

    if motion_detected and motion_frames > 10 : 
        dir = os.listdir("/home/Darterone/Pictures/LoRaComm_Imgs")             #change the directory path to the dir where pictures are stored after capture 
        draw.text((0,52),"Capturing Movement", font=font1, fill=255)

        oled.image(image)
        oled.show()
        time.sleep(LOOPTIME)
     
        
        try:
            for d in dir:
                tt = d.split(".")[0]
                xx = int(tt.split("_")[1])
                if xx > x_old:
                    xt = xx + 1
                    x_old = xx
            file_name = "/home/Darterone/Pictures/LoRaComm_Imgs/" + "image_" + str(xt) + ".jpg"           #change the directory path to the dir where pictures are stored after capture 
            print(file_name)
        except:
            file_name = "/home/Darterone/Pictures/LoRaComm_Imgs/image_1.jpg"                          #change the directory path to the dir where pictures are stored after capture 
# Save the current frame as a photo
        print(file_name)
        #cv2.imwrite(file_name, frame)
        #frame.save(file_name,"JPEG",optimize=True,quality=10)
        gaus = cv2.GaussianBlur(frame,(13,13),0)
        font = cv2.FONT_HERSHEY_PLAIN
        cv2.putText(frame, str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")), (10, 20),font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, "D2", (10, 50),font, 1, (0, 255, 0), 1, cv2.LINE_AA)
       
        #frame.save(file_name,"JPEG",optimize=True,quality=10)
        #try:
        #except:
        cv2.imwrite(file_name,frame)
        i1 = Image.open(file_name)
        i1.save(file_name,"JPEG",optimize=True,quality=20)


        print('Photo captured : ',file_name)

        # Reset motion variables
        motion_detected = False
        motion_frames = 0
        prev_time = t
        with open(file_name,  'rb') as f:
            x = f.read()
            yy = (str(x[-2:]) == "b'\\xff\\xd9'"  )
            #f.close()

        if yy:
            y = datetime.now()
            cur.execute(
                '''INSERT INTO log1(object_detected, photo_capture, image_name, time) 
                VALUES (?,?,?,?)''',('Motion Detected', file_name, file_name.split("/")[4],y))
            # commit changes
            con.commit()
            
            # terminate the connection
            con.close()
        
        else:
            os.remove(file_name)
        
    if t != prev_time:
        dir = os.listdir("/home/Darterone/Pictures/LoRaComm_Imgs")             #change the directory path to the dir where pictures are stored after capture 
        try:
            for d in dir:
                tt = d.split(".")[0]
                xx = int(tt.split("_")[1])
                if xx > x_old:
                    xt = xx + 1
                    x_old = xx
            file_name = "/home/Darterone/Pictures/LoRaComm_Imgs/" + "image_" + str(xt) + ".jpg"           #change the directory path to the dir where pictures are stored after capture 
            print(file_name)
        except:
            file_name = "/home/Darterone/Pictures/LoRaComm_Imgs/image_1.jpg"

        dir = os.listdir("/home/Darterone/Pictures/LoRaComm_Imgs")             #change the directory path to the dir where pictures are stored after capture 
        draw.text((0,52),"Capturing Image: " +str(file_name) , font=font1, fill=255)

        oled.image(image)
        oled.show()
        time.sleep(0.1)
        print(file_name)
        #cv2.imwrite(file_name, frame)
        #frame.save(file_name,"JPEG",optimize=True,quality=10)
        gaus = cv2.GaussianBlur(frame,(13,13),0)
        font = cv2.FONT_HERSHEY_PLAIN
        cv2.putText(frame, str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")), (10, 20),font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, "D2", (10, 50),font, 1, (0, 255, 0), 1, cv2.LINE_AA)
        #try:
        
        #except:
        cv2.imwrite(file_name,frame)
        i1 = Image.open(file_name)
        i1.save(file_name,"JPEG",optimize=True,quality=20)

        print('SPhoto captured.')

        # Reset motion variables
        motion_detected = False
        motion_frames = 0
        prev_time = t

        with open(file_name,  'rb') as f:
            x = f.read()
            yy = (str(x[-2:]) == "b'\\xff\\xd9'"  )
            #f.close()

        if yy:
            y = datetime.now()
            oled.fill(0)
            oled.show()

            image = Image.new("1", (oled.width, oled.height))

            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

        
            draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
        
            cur.execute('''INSERT INTO log1(object_detected, photo_capture, image_name, time) VALUES (?,?,?,?)''',('Triggered', file_name, file_name.split("/")[4],y))
            # commit changes
            con.commit()
            
            # terminate the connection
            con.close()

        else:
            os.remove(file_name)

    


# Release the video capture object and close windows
