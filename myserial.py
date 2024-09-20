# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import serial
from threading import Thread

class MySerial:
    """access to Serial Message"""
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
        self.serialPort.write (str.encode(writeBuffer))


    def __init__(self, port , speed , bytesize , parity, stop , callback  ):
        print ("Configure serial port " + port +" : " + speed)
        self.serialPort = serial.Serial (port,speed,int(bytesize), parity,int(stop),2,False, False)
        self.buffer = ""
        self.callback = callback 
        thread = Thread(target=self.serialpulling)
        thread.start()
