# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import json
import shlex
from subprocess import STDOUT, CalledProcessError, check_output


class MyModem:
    """Access to usb LTE dongle"""

    modemid = -1

    def system_call(self, command):
        """Call a system command"""
        command = shlex.split(command)
        try:
            output = check_output(command, stderr=STDOUT).decode()
            success = True
        except CalledProcessError as e:
            output = e.output.decode()
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
            count = len(result)
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
        if int(self.modemid) >= 0:
            cmd = (
                "mmcli -m "
                + modemid
                + " --messaging-create-sms=\"text='"
                + text
                + "',number='"
                + phone_number
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
