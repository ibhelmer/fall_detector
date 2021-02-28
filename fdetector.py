# I2C and Pin library
from machine import Pin, I2C
import time
from math import sqrt

alarm = False

# Set LIS331 address
addr = 0x19

# Set the acceleration range
maxScale = 24

# Set the RED led to GPIO pin 5 and green on 9
RED = 5
GREEN = 10
SW = 25

# LIS331 Constants (see Datasheet)
CTRL_REG1 = 0x20
CTRL_REG4 = 0x23
OUT_X_L = 0x28
OUT_X_H = 0x29
OUT_Y_L = 0x2A
OUT_Y_H = 0x2B
OUT_Z_L = 0x2C
OUT_Z_H = 0x2D

POWERMODE_NORMAL = 0x27
RANGE_6G = 0x00
RANGE_12G = 0x10
RANGE_24G = 0x30

# Create I2C bus 0 -> SCL pin 22, SDA pin 21
bus = I2C(1,scl=Pin(22),sda=Pin(21), freq=100000)

# Initialize Pin for led and pushbuttom 
LED_RED = Pin(RED, Pin.OUT)
LED_RED.off()
LED_GREEN = Pin(GREEN, Pin.OUT)
LED_GREEN.off()
SW = Pin(SW, Pin.IN, Pin.PULL_UP)

# Initiliaze LIS331
def initialize(addr, maxScale):
 
    scale = int(maxScale)
    # Initialize accelerometer control register 1: Normal Power Mode and 50 Hz sample rate
    lst = [CTRL_REG1, POWERMODE_NORMAL]
    buf = bytearray (lst)
    bus.writeto(addr, buf)
    # Initialize acceleromter scale selection (6g, 12 g, or 24g). This example uses 24g
    if maxScale == 6:
        lst = [CTRL_REG4, RANGE_6G]
        buf = bytearray (lst)
        bus.writeto(addr,buf)
    elif maxScale == 12:
        lst = [CTRL_REG4, RANGE_12G]
        buf = bytearray (lst)
        bus.writeto(addr,buf)
    elif maxScale == 24:
        lst = [CTRL_REG4, RANGE_24G]
        buf = bytearray (lst)
        bus.writeto(addr,buf)
    else:
        print("Error in the scale provided -- please enter 6, 12, or 24")


# Function to read the data from accelerometer
def readAxes(addr):
    data0 = bus.readfrom_mem(addr, OUT_X_L,1)
    data1 = bus.readfrom_mem(addr, OUT_X_H,1)
    data2 = bus.readfrom_mem(addr, OUT_Y_L,1)
    data3 = bus.readfrom_mem(addr, OUT_Y_H,1)
    data4 = bus.readfrom_mem(addr, OUT_Z_L,1)
    data5 = bus.readfrom_mem(addr, OUT_Z_H,1)
    
    # Combine the two bytes and leftshit by 8
    
    x = ord(data0) | ord(data1) << 8
    y = ord(data2) | ord(data3) << 8
    z = ord(data4) | ord(data5) << 8
    # in case overflow
    if x > 32767:
        x -= 65536
    if y > 32767:
        y -= 65536
    if z > 32767:
        z -= 65536
    # Calculate the two's complement as indicated in the datasheet
    x = ~x
    y = ~y
    z = ~z
    return x, y, z


# Function to calculate g-force from acceleration data
def convertToG(maxScale, xAccl, yAccl, zAccl):
    # Caclulate "g" force based on the scale set by user
    # Eqn: (2*range*reading)/totalBits (e.g. 48*reading/2^16)
    X = (2 * float(maxScale) * float(xAccl)) / (2 ** 16);
    Y = (2 * float(maxScale) * float(yAccl)) / (2 ** 16);
    Z = (2 * float(maxScale) * float(zAccl)) / (2 ** 16);
    return X, Y, Z
    
i=0    
while True:
    # initialize LIS331 accelerometer
    mydev = bus.scan()
    initialize(addr, 24)
    xAccl, yAccl, zAccl = readAxes(addr)
    # Calculate G force based on x, y, z acceleration data
    x, y, z = convertToG(maxScale, xAccl, yAccl, zAccl)
    acc = sqrt(x*x+y*y+z*z)
    if acc <  0.6:
        LED_RED.on()
        alarm = True
    if SW.value() == 0:
        LED_RED.off()
        alarm = False
    print(acc)
    if i>=10:
        if LED_GREEN.value()==1:
            LED_GREEN.off()
        else:
            LED_GREEN.on()
        i=0
    i+=1
    
    time.sleep(0.1)
