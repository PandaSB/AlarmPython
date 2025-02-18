# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import time
import json
import shlex
import serial
from subprocess import STDOUT, CalledProcessError, check_output
from threading import Thread



class MyModem:
    """Access to usb LTE dongle"""

    modemid = -1
    direct_at = False
    port = None
    async_modemid = -1
    async_phone_number = None
    async_timeout = 0
    async_direct_at = False
    buffer = ""
    bufferlist = list()
    voicecall = False
    end = False

    def system_call(self, command):
        """Call a system command"""
        command = shlex.split(command)
        try:
            output = check_output(command, stderr=STDOUT).decode()
            success = True
        except CalledProcessError as e:
            output = e.output.decode()
            success = False
        except FileNotFoundError as e:
            output = None
            success = False 
        return output, success

    def callback(self, callbackbuffer):
        if (callbackbuffer != "") :
            print ("message : " + callbackbuffer)
            self.bufferlist.append(callbackbuffer)
        if (callbackbuffer == "VOICE CALL: BEGIN"):
            print ("Voice call start")
            voicecall = True
        if (callbackbuffer == "VOICE CALL: END"):    
            print ("Voice call stop")
            voicecall = False

    def serialpulling(self):
        """Start pulling of Serial"""
        while (self.end == False):
                data = self.port.read(1)
                if (data != b''):
                    #print(data.decode("utf-8", errors="ignore"),end="")
                    if (data == b'\r') or (data == b'\n'):
                        if self.callback:
                            self.callback(self.buffer)
                        self.buffer = ""
                    else:
                        self.buffer = self.buffer + data.decode("utf-8", errors="ignore")

    def write (self,writeBuffer, answer ="" , timeout= 0 , clean = True ):
        """ Send data to serial """
        self.bufferlist = list()
        self.port.write (str.encode(writeBuffer))
        start = time.time()
        if timeout > 0:
            while (time.time()-start < timeout) and (answer not in ''.join(self.bufferlist)):
                time.sleep(0.1)
            if answer not in ''.join(self.bufferlist): 
                print ("Cmd timeout")

    def __init__(self,direct_at,port,speed,bytesize,parity,stop):
        """ Init connection to modem , looking for modem in ModemManager""" 
        if (direct_at == "True"):
            self.direct_at = True
        else:
            self.direct_at = False
        if (self.direct_at == True):
            self.port = serial.Serial (port ,speed,int(bytesize), parity,int(stop),2,False, False)
            if (self.port):
                thread = Thread(target=self.serialpulling)
                thread.start()
            self.write ("AT+CMGF=1\r\n","OK",2)
            self.write ("AT+CSCS=\"GSM\"\r\n","OK",2)
            self.write ("AT+CPMS=\"ME\"\r\n","OK",2)
        else:
            self.modemid = -2
            output, success = self.system_call("mmcli --list-modems -J")
            if success:
                data = json.loads(output)
                try:
                    text = data["modem-list"][0]
                    self.modemid = text[-1:]
                    print("modem id " + str(self.modemid))
                except Exception as e:
                    print(e)

    def getmodem(self):
        """Return Modem id"""
        return self.modemid

    def getlocation(self, modemid):
        """Return information on location"""
        out = ''
        if (self.direct_at == True):
            pass
        else: 
            if int(self.modemid) >= 0:
                output, success = self.system_call(
                    "mmcli --modem=" + modemid + " --location-get"
                )
                if success:
                    out = output
                output, success = self.system_call(
                    "mmcli --modem=" + modemid + " -J"
                )
                if success:
                    data = json.loads(output)
                    signal = data["modem"]["generic"]["signal-quality"]["value"]
                    out += '\n\rSignal level : ' + signal

        return out

    def getsignallevel (self, modemid):
        signal = 0
        if (self.direct_at == True):
            self.write ("AT+CSQ\r\n","OK",2)
            for data in self.bufferlist:
                if data.startswith("+CSQ") :
                    signal = int(data.split()[1].split(",")[0])
        else:
            if int(self.modemid) >= 0:
                out= ''
                output, success = self.system_call(
                    "mmcli --modem=" + modemid + " -J"
                )
                if success:
                    data = json.loads(output)
                    signal = data["modem"]["generic"]["signal-quality"]["value"]
        return signal

    def getpathsms(self, modemid):
        """Return path of sms messages presents"""
        if (self.direct_at == True):
            self.write ("AT+CMGL=\"ALL\"\r\n","OK",10)
            listsms = list()
            for data in self.bufferlist:
                if data.startswith("+CMGL") : 
                    index = data.split(',')[0].split()[1]
                    listsms.append ('%s' % index)
            return (listsms)
        else:
            if int(self.modemid) >= 0:
                output, success = self.system_call(
                    "mmcli --modem=" + modemid + " --messaging-list-sms -J"
                )
                if success:
                    data = json.loads(output)
                    text = data["modem.messaging.sms"]
                    return text

    def getcountsms(self, modemid):
        """Count sms present on LTE dongle"""
        result = self.getpathsms(modemid)
        if result: 
            count = len(result)
        else:
            count = 0 
        return count

    def readsms(self, modemid, smspath):
        """Read a specific sms"""
        phone_number = ""
        content = ""
        if (self.direct_at == True):
            self.write ("AT+CMGR="+smspath+"\r\n","OK",5)
            if (len(self.bufferlist) > 0 ):
                if (self.bufferlist[-1].startswith("OK")):
                    for sms in self.bufferlist[:-1]:
                        if sms.startswith("+CMGR") : 
                            listsms = sms.split(",")
                            phone_number = listsms[1].replace ("\"","")
                        else:
                            if not sms.startswith ("AT+CMGR="+smspath):
                                content += sms + "\r\n"
        else:
            if int(self.modemid) >= 0:
                output, success = self.system_call(
                    "mmcli -m " + modemid + " -s " + smspath + " -J"
                )
                if success:
                    data = json.loads(output)
                    phone_number = data["sms"]["content"]["number"]
                    content = data["sms"]["content"]["text"]
        return phone_number, content

    def deletesms(self, modemid, smspath):
        """Delete a specific sms"""
        if (self.direct_at == True):
            self.write ("AT+CMGD="+smspath+"\r\n","OK",2)
        else:
            if int(modemid) >= 0:
                output = ''
                cmd = "mmcli  -m " + modemid + " --messaging-delete-sms=" + smspath
                output, success = self.system_call(cmd)
                print ('delete sms : ' + cmd + ' '+ output)

    def createsms(self, modemid, phone_number, text):
        """Creaate a sms in memory of LTE dongle"""
        if (self.direct_at == True):
            phone_list = phone_number.split()
            for tel in phone_list:
                self.write ("AT+CMGS=\""+tel+"\"\r")
                for i in range(20):
                    if len (self.bufferlist) > 0:
                        if "> " in self.bufferlist:
                            self.write ("%s \x1A" %text)
                        break
                    else:
                        time.sleep(1)
                else:
                    time.sleep(1)
                if i == 19:
                    self.write ("\x1B\r\n") 
                self.write ("","OK",2)                
        else:
            phone_list = phone_number.split()
            for tel in phone_list:
                if int(self.modemid) >= 0:
                    cmd = (
                        "mmcli -m "
                        + modemid
                        + " --messaging-create-sms=\"text='"
                        + text
                        + "',number='"
                        + tel
                        + "'\""
                    )
                    output, success = self.system_call(cmd)
                    status = output.split(" ")
                    print(status)
                    if status[0] == "Successfully":
                        path = status[-1]
                        cmd = "mmcli -m " + modemid + " -s " + path + "--send"
                        output, success = self.system_call(cmd)
                        self.deletesms(modemid, path)

    def phonecall (self,modemid , phone_number,timeout):
        phone_list = phone_number.split()
        for tel in phone_list:
            if (self.direct_at == True):
                self.write ("ATD"+tel+";\r\n")
                time.sleep(timeout)
                self.write ("AT+CHUP\r\n") 
            else:
                if int(self.modemid) >= 0:
                    cmd = (
                        "mmcli -m "
                        + modemid
                        + " --voice-create-call='number="
                        + tel
                        + "'"
                    )
                    output, success = self.system_call(cmd)
                    cmd = (
                        "mmcli -m "
                        + modemid
                        + " --voice-list-calls -J "
                    )
                    output, success = self.system_call(cmd)
                    if success:
                        data = json.loads(output)

                        try:
                            callid = data["modem.voice.call"][0]
                            time.sleep(timeout)
                            cmd = (
                                "mmcli -m "
                                + modemid
                                + " --voice-delete-call='"
                                + callid
                                + "'"
                            )
                            output, success = self.system_call(cmd)
                        except Exception as e:
                            print(e)


    def async_phonecall (self,modemid , phone_number,timeout):
        try:
            self.async_modemid = modemid
            self.async_phone_number = phone_number
            self.async_timeout = timeout
            thread = Thread(target=self.run_async_phonecall)
            thread.start()
        except KeyboardInterrupt:
            pass

    def run_async_phonecall(self):
            self.phonecall (self.async_modemid ,self.async_phone_number,self.async_timeout  )
