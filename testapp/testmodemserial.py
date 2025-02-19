#!/bin/python3
# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import serial
import time
import sys
import getopt
from threading import Thread


serialPort = None
buffer = ""
bufferlist = list()
callback = None
voicecall = False
end = False

def callback(callbackbuffer):
    global voicecall
    global bufferlist
    if (callbackbuffer != "") :
        print ("message : " + buffer)
        bufferlist.append(callbackbuffer)
    if (callbackbuffer == "VOICE CALL: BEGIN"):
        print ("Voice call start")
        voicecall = True
    if (callbackbuffer == "VOICE CALL: END"):    
        print ("Voice call stop")
        voicecall = False



def serialpulling():
    global serialPort
    global buffer
    global callback
    global end
    """Start pulling of Serial"""
    while (end == False):
            data = serialPort.read(1)
            if (data != b''):
                print(data.decode("utf-8", errors="ignore"),end="")
                if (data == b'\r') or (data == b'\n'):
                    if callback:
                        callback(buffer)
                    buffer = ""
                else:
                    buffer = buffer + data.decode("utf-8", errors="ignore")

def write (writeBuffer, answer ="" , timeout= 0 , clean = True ):
    """ Send data to serial """
    global serialPort
    global buffer
    global bufferlist
    bufferlist = list()
    serialPort.write (str.encode(writeBuffer))
    start = time.time()
    if timeout > 0:
        while (time.time()-start < timeout) and (answer not in ''.join(bufferlist)):
            time.sleep(0.1)
        if answer not in ''.join(bufferlist): 
            print ("Cmd timeout")

if __name__ == '__main__':
    SerialName = "/dev/ttyUSB1"
    speed = 115200
    bytesize = 8
    parity = 'N'
    stop = 1
    phone=""
    
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hp:s:n:',
            ['help','port=','speed=','number='])
    except getopt.GetoptError:
        print ('test.py -s <speed> -p <serial port> -n <number>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print ('test.py -s <speed> -p <serial port> -n <number>')
            sys.exit()
        elif opt in ("-n", "--number"):
            phone = arg
        elif opt in ("-p", "--port"):
            SerialName = arg
        elif opt in ("-s", "--speed"):
            speed = int(arg)

    serialPort = serial.Serial (SerialName,speed,int(bytesize), parity,int(stop),2,False, False)
    if (serialPort):
        thread = Thread(target=serialpulling)
        thread.start()
    write ("\x1B\r\n")
    write ("AT\r\n","OK",1)
    write ("ATI\r\n","OK",2)
    write ("AT+SIMCOMATI\r\n","OK",2)
    write ("AT+CSQ\r\n","OK",2)
    write ("AT+COPS?\r\n","+COPS:",2)
    if (phone != ""): 
        # write ("AT+DTAM?\r\n")
        # write ("AT+CTTSPARAM=?\r\n")
        # write ("AT+CTTSPARAM=1,3,0,1,1\r\n")
        # write ("AT+CTTSPARAM?\r\n")
        # write ("ATD"+phone+";\r\n")
        # for i in range(20):
        #     time.sleep (1)
        #     if (voicecall):
        #         write ("AT+CTTS=2,\"TEST MESSAGE\"\r\n")
        #         voicecall = False
        #         time.sleep(4)
        #         break ; 
        # write ("AT+CHUP\r\n")   # AT+CVHU=0 ATH
        write ("AT+CMGF=1\r\n","OK",2)
        write ("AT+CMGF?\r\n","+CMGF:",2)
        write ("AT+CSCS=\"GSM\"\r\n","OK",2)
        write ("AT+CSCS?\r\n","+CSCS:",2)
        write ("AT+CPMS=\"ME\"\r\n")
        write ("AT+CPMS=?\r\n")
        write ("AT+CPMS?\r\n")
        write ("AT+CLBS=?\r\n","OK",5)
        write ("AT+SIMEI?\r\n","OK",5)
        write ("AT+CLBS=2\r\n","+CLBS:",10)
        write ("AT+CLBS=1\r\n","+CLBS:",10)
        write ("AT+CMGS=\""+phone+"\"\r")
        for i in range(20):
            if len (bufferlist) > 0:
                if "> " in bufferlist:
                    write ("Test Message \x1A")
                    break
                else:
                    time.sleep(1)
            else:
                time.sleep(1)
            if i == 19:
                    write ("\x1B\r\n") 
    write ("","OK",2)                
    write ("AT+CMGL=\"ALL\"\r\n","OK",10)
    for infosms in bufferlist:
        if infosms.startswith("+CMGL") : 
            index = infosms.split(',')[0].split()[1]
            print ('%s : %s' % (index, infosms))
    write ("AT+CMGR=1\r\n","OK",10)
    content = ""
    phone = ""
    if (bufferlist[-1].startswith("OK")):
        for infosms in bufferlist[:-1]:
            if infosms.startswith("+CMGR") : 
                listsms = infosms.split(",")
                phone = listsms[1]
            else:
                content += infosms + "\r\n"
    print ("phone %s " %phone)
    print ("content %s" %content)
    time.sleep (10)
    end = True ; 
    sys.exit()
    

