import binascii
import os, sys
from PIL  import Image
from LoRaRF import SX127x
import time
import datetime
import logging
import sqlite3
import board
import busio
import digitalio

import subprocess
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

logging.basicConfig(filename='/home/pi/items.log')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

image_dir = "/home/pi/Pictures/LoRaComm_Imgs/"
output_file=''

img_index =0

oled_reset = digitalio.DigitalInOut(board.D4)
WIDTH = 128
HEIGHT = 64
BORDER = 5
LOOPTIME = 1.0

i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

busId = 0; csId = 0
resetPin = 22; irqPin = -1; txenPin = -1; rxenPin = -1
LoRa = SX127x()
print("Begin LoRa radio")
if not LoRa.begin(busId, csId, resetPin, irqPin, txenPin, rxenPin) :
    raise Exception("Something wrong, can't begin LoRa radio")

print("Set RX gain to power saving gain")
LoRa.setRxGain(LoRa.RX_GAIN_POWER_SAVING, LoRa.RX_GAIN_AUTO)


print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
LoRa.setSpreadingFactor(7)                                      # LoRa spreading factor: 7
LoRa.setBandwidth(125000)                                       # Bandwidth: 125 kHz
LoRa.setCodeRate(5)                                            # Coding rate: 4/5

image_width = 376
image_height = 134
image = Image.new('L',(image_width, image_height))

print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
LoRa.setHeaderType(LoRa.HEADER_EXPLICIT)                        # Explicit header mode
LoRa.setPreambleLength(12)                                      # Set preamble length to 12
LoRa.setPayloadLength(15)                                       # Initialize payloadLength to 15
LoRa.setCrcEnable(True)

txSyncWord = 0x34
txFrequency = 470000000

recSyncWord = 0x34
recFrequency = 433000000

print("\n-- LoRa Radio --\n")

m_list = []


def transmitF(filepath):
    
    print("Set frequency to: "+ str(txFrequency/1000000) + "MHz")
    LoRa.setFrequency(txFrequency)

    print("Set syncronize word to: ",hex(txSyncWord))
    LoRa.setSyncWord(txSyncWord)

    print("\n-- LoRa Transmiter --\n")

    draw.text((2, 24),"Initiating img", font=font1, fill=255)
    draw.text((2, 36),"transmission.....", font=font1, fill=255)
    
    oled.image(image)
    oled.show()
    time.sleep(LOOPTIME)


    with open(filepath, "rb") as f:
        pic_bytes = f.read()

    hex_string = pic_bytes.hex()
    size = len(hex_string)
    df = 1

    for i in range(113,1,-1):
        d = (size/2) % i
        if d == 0 :
            df = i
            print("elements per list: ",df)
            #print(df)
            break
    #    else :
    #    df =2
    
    time.sleep(0.6)
    #draw = ImageDraw.Draw(image)
    # Draw a white background
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    T_lists = size/(2*df)

    tx_text = "Sending "+ str((size/(2*1000)))+" KB"
    tx_des  = "in "+ str(int(T_lists))+ " packets"
    dtr = "at "+str(int(df))+" B/packet"

    draw.text((0, 11),tx_text, font=font1, fill=255)
    draw.text((0, 23),tx_des, font=font1, fill=255)
    draw.text((0, 35),dtr, font=font1, fill=255)

    oled.image(image)
    oled.show()
    time.sleep(LOOPTIME)



    while True:
        counter = 0
        c=0
        hex_values = []

        for i in range(0, size ,2):
            value = int(hex_string[i:i+2], 16)
            hex_values.append(value)
            c += 1
            if c == df:
                #for i in hex_values:
                LoRa.beginPacket()
                LoRa.write(hex_values)
                LoRa.endPacket()
                time.sleep(0.3)
                print("sent : ")
                print(hex_values)
    #    print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(LoRa.transmitTime(), LoRa.dataRate()))
                LoRa.wait()
                c=0
                a=hex_values[-1]
                b=hex_values[-2]
                     #if a=hex_values[-1] == 217 and b=hex_values[-2] == 255:
                     #    LoRa.endPacket()
                     #    print("end of jpg img")
                hex_values.clear()
                continue
            if len(hex_string) == 0:
                break

        # Print transmit time and data rate
#        print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(LoRa.transmitTime(), LoRa.dataRate()))

        time.sleep(1)
        counter = (counter + 1) % 256
        
        if a == 217 and b == 255 :
            LoRa.endPacket()
            draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
            draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
            
            print(hex_values)
            #print(value)
            print( "total no. of bytes: ",(size/2) )
            print("End of jpg img")
            with open('/home/pi/items.log', 'a') as log_file:
                log_file.write(f"[{datetime.datetime.now()}] Transmitted file: {filepath}\n")
                
            draw.text((3,16),"Transmission done", font=font1, fill=255)
            draw.text((12, 28),"("+str(size/(2*1000))+" KB img)", font=font1, fill=255)
            oled.image(image)
            oled.show()
            time.sleep(LOOPTIME)
            time.sleep(0.6)
            break

        # else:
        #     print("error with jpg file")
        #     break


def recF():

    LoRa.setFrequency(recFrequency)
    print("Seting frequency to: "+ str(recFrequency/1000000) + "MHz")

    LoRa.setSyncWord(recSyncWord)
    print("Setting syncronize word to: ",hex(recSyncWord))

    print("\n-- LoRa Receiver --\n")
    l_cnt = 0

    #IRQ_RX_TIMEOUT = 0x0A


    while True:
        try:
            img_index = len(os.listdir("/home/pi/Pictures/LoRaComm_Imgs/"))
            img_index += 1
        except:
            img_index = 0
        timestamp = datetime.datetime.now().strftime("%d-%m-%H:%M:%S")

        draw.text((2, 24),"Waiting for data", font=font1, fill=255)
        draw.text((2, 36),"Mode : Tranceiver", font=font1, fill=255)
        # draw.text((2, 38),"Incomming data...", font=font1, fill=255)
    
        oled.image(image)
        oled.show()

        LoRa.request()
        # Wait for incoming LoRa packet
        LoRa.wait(timeout=15)


        message = []
        # available() method return remaining received payload length and will decrement each read() or get() method called

        status = LoRa.status()

        while LoRa.available() >= 1 :
            data = LoRa.read()

            if status != LoRa.STATUS_CRC_ERR and status != LoRa.STATUS_HEADER_ERR and LoRa.snr() > 3 and LoRa.snr() < 10 :
                message.append(data)
                #m = int(m,16)
                m_list.append(data)

            # draw.text((2, 13),"Incomming data...", font=font1, fill=255)
            # oled.image(image)
            # oled.show()
            # time.sleep(LOOPTIME)


        if  LoRa.available() < 1 :
            im_dir = "/home/pi/Pictures/LoRaComm_Imgs/"
            cur_ls = os.listdir(im_dir)

            with open('/home/pi/items.log', 'r') as log_file:
                log_data = log_file.read()

            new_files1 = [file for file in cur_ls if file not in log_data]
            if new_files1:
                break
            #else:
            #    LoRa.request()
            #    LoRa.wait(timeout=10)

        l_cnt += 1
        
        # draw.text((2, 13),"Incomming data...", font=font1, fill=255)
        # draw.text((2, 30),"received "+str(l_cnt)+" packets", font=font1, fill=255)
        # oled.image(image)
        # oled.show()
        # time.sleep(LOOPTIME)

        output_file_path = os.path.join(image_dir, f"img_{img_index}_{timestamp}.jpeg")

        try:
            if message[-1] == 217 and message[-2] == 255 and status != LoRa.STATUS_CRC_ERR :
                print("reached End of jpg")
                print("total no. lists received: ",l_cnt)
                with open(output_file_path, 'wb') as f:
                    f.write(bytes(m_list))
                img_index+=1
                Bytes = len(m_list)

                print(bytes(m_list))
                print("recieve file size: ",Bytes)
                size = len(m_list)
               # with open('/home/pi/items.log', 'a') as log_file:
                #    log_file.write(f"[{datetime.datetime.now()}] Received file: {output_file_path}\n")
                break
        except:
            pass
        # counter = LoRa.read()
        # message.append(counter)
        

        # Print received message and counter in serial
        print(f"{message}")

        # Print packet/signal status including RSSI, SNR, and signalRSSI
        print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(LoRa.packetRssi(), LoRa.snr()))

        # Show received status in case CRC or header error occur
        
        if status == LoRa.STATUS_CRC_ERR :
            print("CRC error")
        elif status == LoRa.STATUS_HEADER_ERR :
            print("Packet header error")

    #print(m_list)
    size=len(m_list)
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    draw.text((3,16),"Recieved img", font=font1, fill=255)
    draw.text((12, 28),"("+str(size/(2*1000))+" KB img)", font=font1, fill=255)
    oled.image(image)
    oled.show()
    time.sleep(1)
    m_list.clear()
    message.clear()


while True:
    oled.fill(0)
    oled.show()

    image = Image.new("1", (oled.width, oled.height))

    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

    font1 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
    font2 = ImageFont.truetype('DejaVuSansMono.ttf', 16)
    time.sleep(0.3)
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    im_dir = "/home/pi/Pictures/LoRaComm_Imgs/"
    cur_ls = os.listdir(im_dir)

    with open('/home/pi/items.log', 'r') as log_file:
        log_data = log_file.read()

    new_files = [file for file in cur_ls if file not in log_data]

    if new_files:
        for file in new_files:
            file_path = os.path.join(im_dir, file)
            transmitF(file_path)
            con = sqlite3.connect('/var/www/application/instance/logs2.db')    #change the file path of the path where "data.db is present"
            # create cursor object
            cur = con.cursor()
            y = datetime.datetime.now()
            cur.execute(
                '''INSERT INTO log2(object_detected, photo_capture, image_name, time) 
                VALUES (?,?,?,?)''',('Transmitted', file_path, file,y))
            # commit changes
            con.commit()
            con.close()
    else:
        recF()

    sent_counter = 0  
    time.sleep(1)
