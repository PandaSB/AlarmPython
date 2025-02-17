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

BMP280_ADDR = 0x76

BMP280_DIG_T1 = 0x88
BMP280_DIG_T2 = 0x8A
BMP280_DIG_T3 = 0x8C

BMP280_DIG_P1 = 0x8E
BMP280_DIG_P2 = 0x90
BMP280_DIG_P3 = 0x92
BMP280_DIG_P4 = 0x94
BMP280_DIG_P5 = 0x96
BMP280_DIG_P6 = 0x98
BMP280_DIG_P7 = 0x9A
BMP280_DIG_P8 = 0x9C
BMP280_DIG_P9 = 0x9E

BMP280_DEVICE_ID = 0xD0
BMP280_RESET = 0xE0
BMP280_STATUS = 0xF3
BMP280_CTRL_MEAS = 0xF4
BMP280_CONFIG = 0xF5
BMP280_PRESSURE = 0xF7
BMP280_TEMPERATURE = 0xFA

BMP280_RESET_CMD = 0xB6


BMP280_OVERSAMPLING_P_NONE = 0b000
BMP280_OVERSAMPLING_P_x1   = 0b001
BMP280_OVERSAMPLING_P_x2   = 0b010
BMP280_OVERSAMPLING_P_x4   = 0b011
BMP280_OVERSAMPLING_P_x8   = 0b100
BMP280_OVERSAMPLING_P_x16  = 0b101

BMP280_OVERSAMPLING_T_NONE = 0b000
BMP280_OVERSAMPLING_T_x1   = 0b001
BMP280_OVERSAMPLING_T_x2   = 0b010
BMP280_OVERSAMPLING_T_x4   = 0b011
BMP280_OVERSAMPLING_T_x8   = 0b100
BMP280_OVERSAMPLING_T_x16  = 0b101

BMP280_T_STANDBY_0p5 = 0b000
BMP280_T_STANDBY_62p5 = 0b001
BMP280_T_STANDBY_125 = 0b010
BMP280_T_STANDBY_250 = 0b011
BMP280_T_STANDBY_500 = 0b100
BMP280_T_STANDBY_1000 = 0b101
BMP280_T_STANDBY_2000 = 0b110
BMP280_T_STANDBY_4000 = 0b111

BMP280_IIR_FILTER_OFF = 0b000
BMP280_IIR_FILTER_x2  = 0b001
BMP280_IIR_FILTER_x4  = 0b010
BMP280_IIR_FILTER_x8  = 0b011
BMP280_IIR_FILTER_x16 = 0b100

BMP280_SLEEP_MODE = 0b00
BMP280_FORCED_MODE = 0b01
BMP280_NORMAL_MODE = 0b11


class MyTemp:
    "Read Temp on external device "
    temp_type = None
    addr = 0
    deviceid = 0
    initok = False

    def swap16(self,i):
        return struct.unpack("<H", struct.pack(">H", i))[0]

    def twos_complement(self, input):
        if input > 32767:
            return input - pow(2, 16)
        else:
            return input

    def __init__(self, temp_type='',temp_addr=0x00 ):
        if temp_type == TEMP_TYPE_AM2320:
            try:
                self.bus = smbus.SMBus(1)
                self.addr = int(temp_addr,0)
                self.temp_type = temp_type
                self.initok = True
            except : 
                self.initok = False
        if temp_type == TEMP_TYPE_TMP117:
            try:
                self.bus = smbus.SMBus(1)
                self.addr = int(temp_addr,0)
                self.temp_type = temp_type
            except:
                self.initok = False
            try:
                self.deviceid = self.swap16(self.bus.read_word_data(self.addr,TMP117_DEVICE_ID)) ;
            except IOError as error :
                print ("Error : I2C access ", error )
            print ('DeviceId : ' + hex(self.deviceid))
            if self.deviceid == TMP117_DEVICE_ID_VALUE:
                self.initok = True
                self.reset()
                self.initalize()
        if temp_type == TEMP_TYPE_BMP280:
                self.initok = True
                self.addr = int(temp_addr,0)
                self.temp_type = temp_type
                self.bus = smbus.SMBus(1)
                self.initalize()

    def reset (self):
        if temp_type == TEMP_TYPE_TMP117:
            tmp = self.swap16(self.bus.read_word_data (self.addr, TMP117_CONFIGURATION))
            tmp = tmp | 0x02
            time.sleep(0.002)
            try:
                self.bus.write_word_data(self.addr,TMP117_CONFIGURATION , self.swap16( tmp))
            except IOError as error :
                print ("Error : I2C access ", error )    

    def initalize(self):
        if self.temp_type == TEMP_TYPE_TMP117:
            if self.initok:
                tmp = 0
                tmp |= int(False) << 2 #DR_Alert
                tmp |= int(False) << 3      #POL
                tmp |= int(False) << 4     #T_na
                tmp |= int(0) << 5  #average
                tmp |= int(0) << 7  #conversion cycle time
                tmp |= int(TMP117_CONTINUOUS_CONVERSION_MODE) << 10 # conversion mode
                #
                try:
                    self.bus.write_word_data(self.addr,TMP117_CONFIGURATION , self.swap16( tmp))
                except IOError as error:
                    print ("Error : I2C access ", error )
        if self.temp_type == TEMP_TYPE_BMP280:
            if self.initok:
                mode=BMP280_FORCED_MODE
                oversampling_p=BMP280_OVERSAMPLING_P_x16
                oversampling_t=BMP280_OVERSAMPLING_T_x1
                bme280filter=BMP280_IIR_FILTER_OFF
                standby=BMP280_T_STANDBY_4000
                ctrl_meas_reg = mode + (oversampling_p << 2) + (oversampling_t << 5)
                try:
                    self.bus.write_byte_data(self.addr, BMP280_CTRL_MEAS, ctrl_meas_reg)               
                except IOError as error:
                    print ("Error : I2C access ", error )
                config_reg = 0b000 + (bme280filter << 2) + (standby << 5)
                try:
                    self.bus.write_byte_data(self.addr,  BMP280_CONFIG, config_reg)
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
        elif self.temp_type == TEMP_TYPE_BMP280:
            try:
                t1 = self.bus.read_word_data(self.addr,BMP280_DIG_T1)
                t2 = self.twos_complement(self.bus.read_word_data(self.addr, BMP280_DIG_T2))
                t3 = self.twos_complement(self.bus.read_word_data(self.addr, BMP280_DIG_T3))
                raw_data = self.bus.read_i2c_block_data(self.addr,  BMP280_TEMPERATURE, 3)
            except IOError as error:
                print ("Error reading temp : ", error)
            adc_t = (raw_data[0] * pow(2, 16) + raw_data[1] * pow(2, 8) + raw_data[2]) >> 4
            var1 = ((adc_t / 16384.0) - (t1 / 1024.0)) * t2
            var2 = ((adc_t / 131072.0) - (t1 / 8192.0)) * (((adc_t / 131072.0) - (t1 / 8192.0)) * t3)
            self.t_fine = var1 + var2
            return (var1+var2) / 5120.0      
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
        elif self.temp_type == TEMP_TYPE_BMP280:
            return 0.0
        else:
             return None

    def readPressure(self):
        # Error in Value , must be correct 
        if self.temp_type == TEMP_TYPE_BMP280:
            p1 = self.bus.read_word_data(self.addr, BMP280_DIG_P1)
            p2 = self.twos_complement(self.bus.read_word_data(self.addr, BMP280_DIG_P2))
            p3 = self.twos_complement(self.bus.read_word_data(self.addr, BMP280_DIG_P3))
            p4 = self.twos_complement(self.bus.read_word_data(self.addr, BMP280_DIG_P4))
            p5 = self.twos_complement(self.bus.read_word_data(self.addr, BMP280_DIG_P5))
            p6 = self.twos_complement(self.bus.read_word_data(self.addr, BMP280_DIG_P6))
            p7 = self.twos_complement(self.bus.read_word_data(self.addr, BMP280_DIG_P7))
            p8 = self.twos_complement(self.bus.read_word_data(self.addr, BMP280_DIG_P8))
            p9 = self.twos_complement(self.bus.read_word_data(self.addr, BMP280_DIG_P9))

            raw_data = self.bus.read_i2c_block_data(self.addr,  BMP280_PRESSURE, 3)
            adc_p = (raw_data[0] * pow(2, 16) + raw_data[1] * pow(2, 8) + raw_data[2]) >> 4

            self.readTemperature()

            var1 = (self.t_fine / 2.0) - 64000.0
            var2 = var1 * var1 * p6 / 32768.0
            var2 += var1 * p5 * 2.0
            var2 = (var2 / 4.0) + (p4 * 65536.0)
            var1 = (p3 * var1 * var1 / 524288.0 + (p2 * var1)) / 524288.0
            var1 = (1.0 + (var1 / 32768.0)) * p1
            p = 1048576.0 - adc_p
            p = (p - (var2 / 4096.0)) * 6250.0 / var1
            var1 = p9 * p * p / 2147483648.0
            var2 = p * p8 / 32768.0
            p += (var1 + var2 + p7) / 16.0
            return p / 100
        else:
            return None 
