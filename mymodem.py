# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import time
import json
import shlex
from subprocess import STDOUT, CalledProcessError, check_output
from threading import Thread



class MyModem:
    """Access to usb LTE dongle"""

    modemid = -1
    async_modemid = -1
    async_phone_number = None
    async_timeout = 0
    async_direct_at = False

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

    def __init__(self):
        """ Init connection to modem , looking for modem in ModemManager""" 
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
        if int(self.modemid) >= 0:
            out= ''
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
        if int(self.modemid) >= 0:
            result = self.getpathsms(modemid)
            if result: 
                count = len(result)
            else:
                count = 0 
            return count

    def readsms(self, modemid, smspath):
        """Read a specific sms"""
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
        if int(modemid) >= 0:
            output = ''
            cmd = "mmcli  -m " + modemid + " --messaging-delete-sms=" + smspath
            output, success = self.system_call(cmd)
            print ('delete sms : ' + cmd + ' '+ output)

    def createsms(self, modemid, phone_number, text):
        """Creaate a sms in memory of LTE dongle"""
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

    def phonecall (self,modemid , phone_number,timeout,direct_at):
        phone_list = phone_number.split()
        for tel in phone_list:
            if int(self.modemid) >= 0:
                if (direct_at == True) :
                    cmd = (
                        "mmcli -m "
                        + modemid
                        + " --command=\"ATD"
                        + tel
                        + "\""
                    )
                    output, success = self.system_call(cmd)
                    time.sleep(timeout)
                    cmd = (
                        "mmcli -m "
                        + modemid
                        + " --command=\"ATH\""
                    )
                    output, success = self.system_call(cmd)
                else :
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


    def async_phonecall (self,modemid , phone_number,timeout,direct_at):
        try:
            self.async_modemid = modemid
            self.async_phone_number = phone_number
            self.async_timeout = timeout
            self.async_direct_at = direct_at
            thread = Thread(target=self.run_async_phonecall)
            thread.start()
        except KeyboardInterrupt:
            pass

    def run_async_phonecall(self):
            self.phonecall (self.async_modemid ,self.async_phone_number,self.async_timeout,self.async_direct_at  )
