#!/bin/python3
# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

from subprocess import STDOUT, CalledProcessError, check_output
import shlex
import json


def action_sms ( phone, content ):
    print ("SMS recu de " + phone +" :")
    print (content)

def system_call(command):
    """Call a system command"""
    command = shlex.split(command)
    try:
        output = check_output(command, stderr=STDOUT).decode()
        success = True
    except CalledProcessError as e:
        output = e.output.decode()
        success = False
    return output, success


def send_sms(phone, content):

    """Modem id """
    output, success = system_call("mmcli --list-modems -J")
    try:
        data = json.loads(output)
        text = data["modem-list"][0]
        modemid = text[-1:]
    except Exception as e:
        print(e)   
    output, success = system_call("mmcli -m " + modemid + " --messaging-create-sms=\"text='" + content + "',number='" + phone + "'\"" )
    status = output.split(" ")
    print(status)
    if status[0] == "Successfully":
        path = status[-1]
        output, success = system_call("mmcli -m " + modemid + " -s " + path + "--send")
        output, success = system_call( "mmcli  -m " + modemid + " --messaging-delete-sms=" + path)


def read_sms():  
    """Modem id """
    output, success = system_call("mmcli --list-modems -J")
    try:
        data = json.loads(output)
        text = data["modem-list"][0]
        modemid = text[-1:]
    except Exception as e:
        print(e)   


    print ("modem id : " + modemid)

    output, success = system_call("mmcli --modem=" + modemid + " --messaging-list-sms -J")
    try:
        data = json.loads(output)
        text = data["modem.messaging.sms"]
        count = len(text)
    except Exception as e:
        print(e)       
    print (text)
    print (count)

    for smspath in text:
        output, success = system_call("mmcli -m " + modemid + " -s " + smspath + " -J")
        try:
            data = json.loads(output)
            phone_number = data["sms"]["content"]["number"]
            content = data["sms"]["content"]["text"]
            action_sms(phone_number,content)
        except Exception as e:
            print(e)   
        output, success = system_call( "mmcli  -m " + modemid + " --messaging-delete-sms=" + smspath)



def main():
    """Programme principal """
    print("Test SMS a travers mmcli")
    read_sms()
    send_sms("+33600000000","Test SMS")

if __name__ == "__main__":
    main()
