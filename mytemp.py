# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC
import smbus
import time 

TEMP_TYPE_AM2320 = 'AM2320'
# temp register address
AM2320_REG_TEMP_H = 0x02
# humidity register address
AM2320_REG_HUM_H = 0x00 
AM2320_CMD = 0x03  

class MyTemp:
    "Read Temp on external device "
    temp_type = None
    addr = 0
    def __init__(self, temp_type='',temp_addr=0x00 ):
        if temp_type == TEMP_TYPE_AM2320:
                self.addr = int(temp_addr,0)
                self.temp_type = temp_type
                self.bus = smbus.SMBus(1)

    def wakeSensor(self):
        for _ in range(3):
            try:
                self.bus.write_i2c_block_data(self.addr,0x00,[0x00])
                return
            except IOError: 
                pass
            time.sleep (0.25)

    def readTemperature(self ):
        block = None
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
        else:
             return None


        