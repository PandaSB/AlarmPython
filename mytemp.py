# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC
import smbus
import time 
import struct

TEMP_TYPE_AM2320 = 'AM2320'
TEMP_TYPE_BMP280 = 'BMP280'
TEMP_TYPE_TMP117 = 'TMP117'



AM2320_REG_TEMP_H = 0x02
AM2320_REG_HUM_H = 0x00 
AM2320_CMD = 0x03  

TMP117_ADDR = 0x48
TMP117_TEMP_RESULT = 0x00
TMP117_CONFIGURATION = 0x01
TMP117_T_HIGH_LIMIT = 0x02
TMP117_T_LOW_LIMIT = 0x03
TMP117_EEPROM_UL = 0x04
TMP117_EEPROM1 = 0x05
TMP117_EEPROM2 = 0x06
TMP117_TEMP_OFFSET = 0x07
TMP117_EEPROM3 = 0x08
TMP117_DEVICE_ID = 0x0F
TMP117_DEVICE_ID_VALUE = 0x0117
TMP117_RESOLUTION = 0.0078125  # Resolution of the device, found on (page 1 of datasheet)


TMP117_CONTINUOUS_CONVERSION_MODE = 0b00  # Continuous Conversion Mode
TMP117_ONE_SHOT_MODE = 0b11  # One Shot Conversion Mode
TMP117_SHUTDOWN_MODE = 0b01  # Shutdown Conversion Mode


class MyTemp:
    "Read Temp on external device "
    temp_type = None
    addr = 0
    deviceid = 0
    initok = False

    def swap16(self,i):
        return struct.unpack("<H", struct.pack(">H", i))[0]

    def __init__(self, temp_type='',temp_addr=0x00 ):
        if temp_type == TEMP_TYPE_AM2320:
                self.addr = int(temp_addr,0)
                self.temp_type = temp_type
                self.bus = smbus.SMBus(1)
                self.initok = True
        if temp_type == TEMP_TYPE_TMP117:
                self.addr = int(temp_addr,0)
                self.temp_type = temp_type
                self.bus = smbus.SMBus(1)
                try:
                    self.deviceid = self.swap16(self.bus.read_word_data(self.addr,TMP117_DEVICE_ID)) ;
                except IOError as error :
                    print ("Error : I2C access ", error )
                print ('DeviceId : ' + hex(self.deviceid))
                if self.deviceid == TMP117_DEVICE_ID_VALUE:
                    self.initok = True
                    self.reset()
                    self.initalize()

    def reset (self):
        tmp = self.swap16(self.bus.read_word_data (self.addr, TMP117_CONFIGURATION))
        tmp = tmp | 0x02
        time.sleep(0.002)
        self.bus.write_word_data(self.addr,TMP117_CONFIGURATION , self.swap16( tmp))


    def initalize(self):
        if self.temp_type == TEMP_TYPE_TMP117:
            if self.initok:
                tmp = 0
                tmp |= int(False) << 2 #DR_Alert
                tmp |= int(False) << 3      #POL
                tmp |= int(False) << 4     #T_na
                tmp |= int(0) << 5  #average
                tmp |= int(0) << 7  #conversion cycle time
                tmp |= int(0) << 10 # conversion mode
                #
                try:
                    self.bus.write_word_data(self.addr,TMP117_CONFIGURATION , self.swap16( tmp))
                except IOError as error:
                    print ("Error : I2C access ", error )




    def wakeSensor(self):
        if self.temp_type == TEMP_TYPE_AM2320:
            for _ in range(3):
                try:
                    self.bus.write_i2c_block_data(self.addr,0x00,[0x00])
                    return
                except IOError:
                    pass
                time.sleep (0.25)


    def readTemperature(self ):
        block = None
        value = 0.0
        if self.temp_type == TEMP_TYPE_AM2320:
            self.wakeSensor()
            for _ in range(3):
                try:
                    self.bus.write_i2c_block_data(self.addr, AM2320_CMD, [0x02, 0x02])
                except IOError:
                    pass
                time.sleep (0.015)
            try:
                block = self.bus.read_i2c_block_data(self.addr, 0,4)
            except IOError:
                    pass       
            if block: 
                value = float(block[2] << 8 | block[3]) / 10
                return value
            else:
                return None
        elif self.temp_type == TEMP_TYPE_TMP117:
            while True :
                try:
                    tmp = self.swap16( self.bus.read_word_data(self.addr,TMP117_CONFIGURATION))
                except IOError as error :
                    print ("Error reading temp : ", error)
                    break
                if ((tmp & 0x2000) != 0):
                    break
            try:
                tmp = self.swap16( self.bus.read_word_data(self.addr,TMP117_TEMP_RESULT))
                value = TMP117_RESOLUTION  * float (tmp)
            except IOError as error:
                print ("Error reading temp : ", error)
            return ( value )
        else:
             return None

    def readHumidity(self):
        block = None
        if self.temp_type == TEMP_TYPE_AM2320:
            self.wakeSensor()
            for _ in range(3):
                try:
                    self.bus.write_i2c_block_data(self.addr, AM2320_CMD, [0x00, 0x02])
                except IOError:
                    pass
                time.sleep (0.015)
            try:
                block = self.bus.read_i2c_block_data(self.addr, 0,4)
            except IOError:
                    pass       
            if block:
                value = float(block[2] << 8 | block[3]) / 10    
                return value
            else:
                return None
        elif self.temp_type == TEMP_TYPE_TMP117:
            return 0.0
        else:
             return None


        