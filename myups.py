# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import gpiod
import smbus
import struct



class MyUps:
    pwpluglines = None
    bus = None

    def readVoltage(self):
        """This function returns as float the voltage from the Raspi UPS Hat via the provided SMBus object on MAX17040 """
        address = 0x36
        read = self.bus.read_word_data(address, 0X02)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        voltage = swapped * 1.25 /1000/16
        return voltage


    def readCapacity(self):
        """This function returns as a float the remaining capacity of the battery connected to the Raspi UPS Hat via the provided SMBus object on MAX17040"""
        address = 0x36
        read = self.bus.read_word_data(address, 0X04)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        capacity = swapped/256
        return capacity


    def QuickStart(self):
        """Quick start UPS chipset"""
        address = 0x36
        self.bus.write_word_data(address, 0x06,0x4000)
        

    def PowerOnReset(self):
        """Power reset of UPS device MAX17040"""
        address = 0x36
        self.bus.write_word_data(address, 0xfe,0x0054)


    def __init__(self):
        """Init UPS"""
        chip = gpiod.Chip("gpiochip0")
        pwplugline = gpiod.find_line('GPIO4')
        self.pwpluglines = chip.get_lines([pwplugline.offset()])
        self.pwpluglines.request(
            consumer="alarm",
            type=gpiod.LINE_REQ_DIR_IN,
            flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
        )
        self.bus = smbus.SMBus(1)
        self.PowerOnReset()

    def pwlinegetvalue(self):
        """Read GPIO Plugged power supply"""
        value = self.pwpluglines.get_values()[0]
        return value
