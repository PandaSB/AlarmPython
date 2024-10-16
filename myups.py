# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import gpiod
import smbus
import struct

UPS_TYPE_MAX17040           = 'MAX17040'
UPS_TYPE_INA219             = 'INA219'

_REG_CONFIG                 = 0x00
_REG_SHUNTVOLTAGE           = 0x01
_REG_BUSVOLTAGE             = 0x02
_REG_POWER                  = 0x03
_REG_CURRENT                = 0x04
_REG_CALIBRATION            = 0x05


class BusVoltageRange:
    """Constants for ``bus_voltage_range``"""
    RANGE_16V               = 0x00      # set bus voltage range to 16V
    RANGE_32V               = 0x01      # set bus voltage range to 32V (default)

class Gain:
    """Constants for ``gain``"""
    DIV_1_40MV              = 0x00      # shunt prog. gain set to  1, 40 mV range
    DIV_2_80MV              = 0x01      # shunt prog. gain set to /2, 80 mV range
    DIV_4_160MV             = 0x02      # shunt prog. gain set to /4, 160 mV range
    DIV_8_320MV             = 0x03      # shunt prog. gain set to /8, 320 mV range

class ADCResolution:
    """Constants for ``bus_adc_resolution`` or ``shunt_adc_resolution``"""
    ADCRES_9BIT_1S          = 0x00      #  9bit,   1 sample,     84us
    ADCRES_10BIT_1S         = 0x01      # 10bit,   1 sample,    148us
    ADCRES_11BIT_1S         = 0x02      # 11 bit,  1 sample,    276us
    ADCRES_12BIT_1S         = 0x03      # 12 bit,  1 sample,    532us
    ADCRES_12BIT_2S         = 0x09      # 12 bit,  2 samples,  1.06ms
    ADCRES_12BIT_4S         = 0x0A      # 12 bit,  4 samples,  2.13ms
    ADCRES_12BIT_8S         = 0x0B      # 12bit,   8 samples,  4.26ms
    ADCRES_12BIT_16S        = 0x0C      # 12bit,  16 samples,  8.51ms
    ADCRES_12BIT_32S        = 0x0D      # 12bit,  32 samples, 17.02ms
    ADCRES_12BIT_64S        = 0x0E      # 12bit,  64 samples, 34.05ms
    ADCRES_12BIT_128S       = 0x0F      # 12bit, 128 samples, 68.10ms

class Mode:
    """Constants for ``mode``"""
    POWERDOW                = 0x00      # power down
    SVOLT_TRIGGERED         = 0x01      # shunt voltage triggered
    BVOLT_TRIGGERED         = 0x02      # bus voltage triggered
    SANDBVOLT_TRIGGERED     = 0x03      # shunt and bus voltage triggered
    ADCOFF                  = 0x04      # ADC off
    SVOLT_CONTINUOUS        = 0x05      # shunt voltage continuous
    BVOLT_CONTINUOUS        = 0x06      # bus voltage continuous
    SANDBVOLT_CONTINUOUS    = 0x07      # shunt and bus voltage continuous

class MyUps:
    pwpluglines = None
    bus = None
    upstype = None
    addr = None

    def set_calibration_32V_2A(self):
        if self.upstype == UPS_TYPE_INA219:
            self._current_lsb = .1
            self._cal_value = 4096
            self._power_lsb = .002 
            self.write(_REG_CALIBRATION,self._cal_value)
            self.bus_voltage_range = BusVoltageRange.RANGE_32V
            self.gain = Gain.DIV_8_320MV
            self.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
            self.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
            self.mode = Mode.SANDBVOLT_CONTINUOUS
            self.config = self.bus_voltage_range << 13 | \
                        self.gain << 11 | \
                        self.bus_adc_resolution << 7 | \
                        self.shunt_adc_resolution << 3 | \
                        self.mode
            self.write(_REG_CONFIG,self.config)

    def readVoltage(self):
        """This function returns as float the voltage from the Raspi UPS Hat via the provided SMBus object on MAX17040 """
        voltage = -1,0
        if self.upstype == UPS_TYPE_MAX17040:
            try:
                read = self.bus.read_word_data(self.addr, 0X02)
                swapped = struct.unpack("<H", struct.pack(">H", read))[0]
                voltage = swapped * 1.25 /1000/16
            except IOError:
                voltage = 0.0
        elif self.upstype == UPS_TYPE_INA219:
            self.write(_REG_CALIBRATION,self._cal_value)
            self.read(_REG_BUSVOLTAGE)
            voltage = (self.read(_REG_BUSVOLTAGE) >> 3) * 0.004
        else:
            printf ("UPS unknown type")  
        return voltage

    def readCurrent (self):
        current = 0.0
        if self.upstype == UPS_TYPE_INA219:
            value = self.read(_REG_CURRENT)
            if value > 32767:
                value -= 65535
            current = value * self._current_lsb
        elif self.upstype == UPS_TYPE_MAX17040:
            print ("Read Current ")
        else:
            printf ("UPS unknown type")  
        return current

    def readpower (self):
        power = 0.0
        if self.upstype == UPS_TYPE_INA219:
            self.write(_REG_CALIBRATION,self._cal_value)
            value = self.read(_REG_POWER)
            if value > 32767:
                value -= 65535
            power = value * self._power_lsb
        elif self.upstype == UPS_TYPE_MAX17040:
            print ("Read Power ")
        else:
            printf ("UPS unknown type")  
        return power

    def readCapacity(self):
        """This function returns as a float the remaining capacity of the battery connected to the Raspi UPS Hat via the provided SMBus object on MAX17040"""
        capacity = 0.0
        if self.upstype == UPS_TYPE_MAX17040:
            try:
                read = self.bus.read_word_data(self.addr, 0X04)
                swapped = struct.unpack("<H", struct.pack(">H", read))[0]
                capacity = swapped/256
            except IOError:
                capacity = 0.0
        elif self.upstype == UPS_TYPE_INA219:
            bus_voltage = self.readVoltage()
            capacity = (bus_voltage - 6)/2.4*100
            if(capacity > 100):capacity = 100
            if(capacity < 0):capacity = 0

        else:
            printf ("UPS unknown type")  
        return capacity


    def QuickStart(self):
        """Quick start UPS chipset"""
        if self.upstype == UPS_TYPE_MAX17040:
            try:
                self.bus.write_word_data(self.addr, 0x06,0x4000)
            except IOError : 
                print ("Error I2C Write")
        elif self.upstype == UPS_TYPE_INA219:
            print ('Quick start')
        else:
            printf ("UPS unknown type")            

    def PowerOnReset(self):
        """Power reset of UPS device MAX17040"""
        if self.upstype == UPS_TYPE_MAX17040:
            try:
                self.bus.write_word_data(self.addr, 0xfe,0x0054)
            except IOError : 
                print ("Error I2C Write")            
        elif self.upstype == UPS_TYPE_INA219:
            print ('Power on Reset')
        else:
            printf ("UPS unknown type")           

    def pwlinegetvalue(self):
        value = 0 
        if self.upstype == UPS_TYPE_MAX17040:
            """Read GPIO Plugged power supply"""
            value = self.pwpluglines.get_values()[0]
        elif self.upstype == UPS_TYPE_INA219:
            value = 0 
            print ('Read ups pw value ')
        else:
            printf ("UPS unknown type")                     
        return value

    def read(self,address):
        try:
            data = self.bus.read_i2c_block_data(self.addr, address, 2)
        except IOError:
            return (0)
        return ((data[0] * 256 ) + data[1])

    def write(self,address,data):
        temp = [0,0]
        temp[1] = data & 0xFF
        temp[0] =(data & 0xFF00) >> 8
        try:
            self.bus.write_i2c_block_data(self.addr,address,temp)
        except IOError:
            print ("Error I2C write")


    def __init__(self, upstype=UPS_TYPE_MAX17040):
        """Init UPS"""
        if upstype == UPS_TYPE_MAX17040:
            self.upstype = UPS_TYPE_MAX17040
            chip = gpiod.Chip("gpiochip0")
            pwplugline = gpiod.find_line('GPIO4')
            self.pwpluglines = chip.get_lines([pwplugline.offset()])
            self.pwpluglines.request(
                consumer="alarm",
                type=gpiod.LINE_REQ_DIR_IN,
                flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
            )
            self.bus = smbus.SMBus(1)
            self.addr = 0x36
            self.PowerOnReset()
        elif upstype == UPS_TYPE_INA219:
            self.upstype = UPS_TYPE_INA219
            self.bus = smbus.SMBus(1)
            self.addr = 0x42
            self._cal_value = 0
            self._current_lsb = 0
            self._power_lsb = 0
            self.set_calibration_32V_2A()
        else:
            printf ("UPS unknown type")


  