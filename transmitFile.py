import os, sys

#currentdir = os.path.dirname(os.path.realpath(__file__)) 
#sys.path.append(os.path.dirname(os.path.dirname(currentdir)))

from LoRaRF import SX127x
import time

import board
import busio
import digitalio

import subprocess
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

#ls = os.listdir(im_dir)

input_file = "/home/pi/Pictures/SUNGALLERY(1).jpg"
file_name = "SUNGALLERY(1).jpg"

output_directory = "/home/pi/Pictures/output"

oled_reset = digitalio.DigitalInOut(board.D4)

WIDTH = 128
HEIGHT = 64
BORDER = 5

# Display Refresh
LOOPTIME = 1.0

i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

busId = 0; csId = 0
resetPin = 22; irqPin = -1; txenPin = -1; rxenPin = -1
LoRa = SX127x()

print("Begin LoRa radio")
if not LoRa.begin(busId, csId, resetPin, irqPin, txenPin, rxenPin) :
    raise Exception("Something wrong, can't begin LoRa radio")

print("Set TX power to +17 dBm")
LoRa.setTxPower(17, LoRa.TX_POWER_PA_BOOST)                     # TX power +17 dBm using PA boost pin

print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
LoRa.setSpreadingFactor(7)                                      # LoRa spreading factor: 7
LoRa.setBandwidth(125000)                                       # Bandwidth: 125 kHz
LoRa.setCodeRate(5)                                             # Coding rate: 4/5

# Configure packet parameter including header type, preamble length, payload length, and CRC type
# The explicit packet includes header contain CR, number of byte, and CRC type
# Receiver can receive packet with different CR and packet parameters in explicit header mode
print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
LoRa.setHeaderType(LoRa.HEADER_EXPLICIT)                        # Explicit header mode
LoRa.setPreambleLength(12)                                      # Set preamble length to 12
LoRa.setPayloadLength(15)                                       # Initialize payloadLength to 15
LoRa.setCrcEnable(True)
import board
import busio
import digitalio
txSyncWord = 0x34
txFrequency = 470000000

#print("Set frequency to: "+ str(txFrequency/1000000) + "MHz")
#LoRa.setFrequency(txFrequency)

#print("Set syncronize word to: ",hex(txSyncWord))
#LoRa.setSyncWord(txSyncWord)

print("\n-- LoRa Radio --\n")

def transmitF():

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


    with open(input_file, "rb") as f:
        pic_bytes = f.read()

    hex_string = pic_bytes.hex()
    size = len(hex_string)
    df = None

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
        print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(LoRa.transmitTime(), LoRa.dataRate()))

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



while True:
    sent_counter = 0

    oled.fill(0)
    oled.show()

    image = Image.new("1", (oled.width, oled.height))

    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

    font1 = ImageFont.truetype('DejaVuSansMono.ttf', 11)
    font2 = ImageFont.truetype('DejaVuSansMono.ttf', 16)
    time.sleep(1)
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    
    time.sleep(2)

    transmitF()

    
