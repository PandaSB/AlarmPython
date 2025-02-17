# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

#to update specific name for usb serial
#/etc/udev/rules.d/99-usb-serial.rules
#SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="ttySER0"

import serial
from threading import Thread

class MySerial:
    """access to Message on serial interface """
    serialPort = None 
    buffer = ""
    callback = None

    def serialpulling(self):
        """Start pulling of Serial"""
        while (True):
                data = self.serialPort.read(1)
                if (data != b''):
                    if (data == b'\r') or (data == b'\n'):
                        if self.callback:
                            self.callback(self.buffer)
                        self.buffer = ""
                    else:
                        self.buffer = self.buffer + data.decode("utf-8")

    def write (self, writeBuffer):
        """ Send data to serial """
        self.serialPort.write (str.encode(writeBuffer))


    def __init__(self, port , speed , bytesize , parity, stop , callback  ):
        print ("Configure serial port " + port +" : " + speed)
        try:
            self.serialPort = serial.Serial (port,speed,int(bytesize), parity,int(stop),2,False, False)
        except:
            self.serialPort = None 
        self.buffer = ""
        self.callback = callback 
        if (self.serialPort):
            thread = Thread(target=self.serialpulling)
            thread.start()
