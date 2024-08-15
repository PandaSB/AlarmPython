
#SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
#SPDX-License-Identifier: ISC

from subprocess import check_output, CalledProcessError, STDOUT
import shlex
import json
from io import StringIO

class mymodem:
    modemid = -1

    def system_call(self, command):
        command = shlex.split(command)
        try:
            output = check_output(command, stderr=STDOUT).decode()
            success = True 
        except CalledProcessError as e:
            output = e.output.decode()
            success = False
        return output, success
    

    def __init__ (self):
        self.modemid = -2
        output, success = self.system_call ('mmcli --list-modems -J')
        if success: 
            data = json.loads (output)
            try:
                text = data["modem-list"][0]
                self.modemid = text[-1:]
                print ("modem id " + str(self.modemid))
            except:
                print ('error init modem')

    def getmodem (self):
        return (self.modemid)

    def getpathsms (self, modemid):
        if (int(self.modemid) >= 0 ):
            output, success = self.system_call ('mmcli --modem=' + modemid + ' --messaging-list-sms -J')
            if success: 
                data = json.loads (output)
                text = data["modem.messaging.sms"]  
                return (text)
                     
    def getcountsms (self, modemid):
        if (int(self.modemid) >= 0 ):
            result = self.getpathsms (modemid)
            count = 0
            for line in result : 
                count +=1
            return (count)

    def readsms (self,modemid,smspath):
        if (int(self.modemid) >= 0 ):
            output, success = self.system_call ('mmcli -m '+ modemid +' -s ' + smspath +' -J')
            if success:
                data = json.loads (output)
                phone_number = data['sms']['content']["number"]
                content = data['sms']['content']["text"]

                return phone_number , content

    def deletesms (self,modemid ,smspath):
        if (int(self.modemid) >= 0 ):
            output, success = self.system_call ('mmcli  -m '+ modemid +  ' --messaging-delete-sms=' + smspath +'-J')

    def createsms (self, modemid ,phone_number , text):
        if (int(self.modemid) >= 0 ):
            cmd = 'mmcli -m ' + modemid + ' --messaging-create-sms="text=\''+ text + '\',number=\'' + phone_number + '\'"'
            output, success = self.system_call (cmd)
            status = output.split(' ')
            print (status)
            if (status[0] =='Successfully'):
                path = status[-1]
                cmd = 'mmcli -m ' + modemid + ' -s '+ path + '--send'
                output, success = self.system_call (cmd)
                self.deletesms (modemid, path)

        
        


