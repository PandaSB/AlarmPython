#!/bin/python
# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import configparser
import os
import time
import json
import shutil
import datetime
import subprocess
from http.server import BaseHTTPRequestHandler

from myemail import MyEmail
from myipcamera import MyIpCamera
from myloop import MyLoop
from mymodem import MyModem
from mytelegram import MyTelegram
from myusbcamera import MyUsbCamera
from myserial import MySerial
from myutils import MyUtils
from myups import MyUps
from mywebserver import MyWebServer
from mymqtt import MyMqtt
from myaws import MyAws
from mytemp import MyTemp
from mysiren import MySiren
from mypir import MyPir
from mybuzzer import MyBuzzer


hasmodem            = 0
hassms              = 0
hasemail            = 0
hastelegram         = 0
hasloop             = 0
hasusbcamera        = 0
hasipcamera         = 0
hasups              = 0
haswebserver        = 0
hasserial           = 0 
hashf               = 0
hasaws              = 0 
hasmqtt             = 0
hastemp             = 0
hassiren            = 0
haspir              = 0
hasbuzzer           = 0
hasheartbeat        = 0

modem_object        = None
loop_object         = None
email_object        = None
telegram_object     = None
usbcamera_object    = None
ipcamera_object     = None
ups_object          = None
webserver_object    = None
serial_object       = None
aws_object          = None
mqtt_object         = None
temp_object         = None
siren_object        = None
pir_object          = None
buzzer_object       = None

lastloopstatus      = False
loopcheck           = False
alarm_on            = False
alarm_ring          = False
alarm_security      = False
lastalamstate       = False
intrusion           = False
pir                 = False
lastalarmstate      = False
lastintrutiontime   = 0
lastpirtime         = 0
lastserialtime      = 0
startalarmdelay     = 0
heartbeattime       = 0
alarm_zone          = 1
lastserialcmd       = ""

email_config        = None
loop_config         = None
telegram_config     = None
sms_config          = None
usbcamera_config    = None
ipcamera_config     = None
serial_config       = None
hf_config           = None
mqtt_config         = None
aws_config          = None
temp_config         = None
siren_config        = None
pir_config          = None
buzzer_config       = None
heartbeat_config    = None
zone1_config        = None
zone2_config        = None


modemid             = None
upsvoltage          = None
upscurrent          = None
upscapacity         = None
pwlinegetvalue      = None

basewebserver       = None
alimserialvalue     = 0.0
alimserialvalid     = False
alimseriallow       = False
batserialvalue      = 0.0
batserialvalid      = False
batseriallow        = False

exttemp             = 0.0
exthumidity         = 0.0      

last                = None 





class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global basewebserver
        global alarm_on
        global hasups
        global ups_object
        global usbcamera_object
        global ipcamera_object
        global exttemp
        global exthumidity
        file_name, file_extension = os.path.splitext(self.path.lower())
        print ('filename' + file_name)
        print ('extension' + file_extension)
        if (file_name == '/'):
            file_name = '/index'
            file_extension = '.html'

        if (self.path.startswith("/control")):
 
            command = self.path[len('/control'):].split("?")[0]
            print ('command :' + command)

            if (command == '/set_alarm_off'):
                alarm_on = False
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(str(alarm_on), "utf-8"))        
            if (command == '/set_alarm_on'):
                alarm_on = True
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(str(alarm_on), "utf-8"))             
            if (command == '/get_alarm_status'):
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(str(alarm_on), "utf-8"))
            elif (command == '/get_alarm_datetime'):
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers() 
                now = datetime.datetime.now()
                timedate = now.strftime("%d/%m/%Y %H:%M:%S")  
                print (timedate)
                self.wfile.write(bytes(timedate, "utf-8"))
            elif (command == '/get_temperature'):
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(f'{exttemp:2.2f}', "utf-8"))
            elif (command == '/get_humidity'):
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(f'{exthumidity:2.2f}' , "utf-8"))
            elif (command == '/get_alarm_temp'):
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(f'{MyUtils.get_cputemperature():2.2f}', "utf-8"))
            elif (command == '/get_alarm_tension'):
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                if hasups: 
                    self.wfile.write(bytes(f'{ups_object.readVoltage():2.2f}', "utf-8"))
                else:
                    self.wfile.write(bytes(str('--')))
            elif (command == '/get_alarm_current'):
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                if hasups: 
                    self.wfile.write(bytes(f'{ups_object.readCurrent():2.2f}', "utf-8"))
                else:
                    self.wfile.write(bytes(str('--')))
            elif (command == '/get_alarm_capacity'):    
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                if hasups: 
                    self.wfile.write(bytes(f'{ups_object.readCapacity():2.2f}', "utf-8"))
                else:
                    self.wfile.write(bytes(str('---')))
            elif (command == '/img1.jpg'):
                filename = None
                self.send_response(200)
                self.send_header("Content-type", "image/jpeg")
                self.end_headers()   
                if usbcamera_object:
                    filename = usbcamera_object.capture_photo()
                    with open(filename, 'rb') as content:
                        shutil.copyfileobj(content, self.wfile)
                    if filename is not None:
                        os.remove(filename) 
                else:
                    self.send_error(404)

            elif (command == '/img2.jpg'):
                filename = None
                self.send_response(200)
                self.send_header("Content-type", "image/jpeg")
                self.end_headers()   
                if ipcamera_object:
                    filename = ipcamera_object.capture_photo()
                    with open(filename, 'rb') as content:
                        shutil.copyfileobj(content, self.wfile)
                    if filename is not None:
                        os.remove(filename) 
                else:
                    self.send_error(404)
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()   
                self.wfile.write(bytes("<html><head><title>image</title></head>", "utf-8"))
                self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
                self.wfile.write(bytes("<body>", "utf-8"))
                self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))                   
        else:
            print (basewebserver + file_name + file_extension)
            if os.path.isfile(basewebserver + file_name + file_extension):
                self.send_response(200)
                if (file_extension == '.html' ) or (file_extension == ''):
                    self.send_header("Content-type", "text/html")
                elif (file_extension == 'jpeg') or (file_extension == '.jpg'):
                    self.send_header("Content-type", "image/jpeg")
                elif (file_extension == '.css') :
                    self.send_header("Content-type", "text/css")
                elif (file_extension == '.js') :
                    self.send_header("Content-type", "application/javascript")
                else:
                    self.send_header("Content-type", "text/plain")
                self.end_headers()
                
                with open(basewebserver + file_name + file_extension, 'rb') as content:
                    shutil.copyfileobj(content, self.wfile)
            
            else:
                self.send_error(404)

def command_serial ( buffer):
    reply = None
    global alarm_on
    global alarm_zone
    global alarm_ring
    global alarm_security
    global hashf
    global hf_config
    global intrusion
    global alimserialvalue
    global alimserialvalid
    global batserialvalue
    global batserialvalid
    global lastintrutiontime
    global lastserialtime
    global lastserialcmd
    global last

    check_cmd = buffer.lower().split()
    currenttime = int(time.time())
    if (len(check_cmd) > 0):
        if (currenttime > (lastserialtime + 2)) or ( buffer != lastserialcmd):
            lastserialtime = currenttime
            lastserialcmd = buffer
            if (check_cmd[0] == 'hfrecu'):
                if (check_cmd[1] == hf_config['onalarm'].lower()):
                    print ("alarme on : ")
                    alarm_on = True
                    alarm_zone = 1
                if (check_cmd[1] == hf_config['homealarm'].lower()):
                    print ("alarme home : ")
                    alarm_on = True
                    alarm_zone = 2
                if (check_cmd[1] == hf_config['offalarm'].lower()):
                    print ("alarme off : ")
                    alarm_on = False
                if (check_cmd[1] == hf_config['security'].lower()):
                    print ("alarme security : ")
                    alarm_security = True
                if (check_cmd[1] == hf_config['ring'].lower()):
                    print ("alarme ring : ")
                    alarm_ring = True
                if (check_cmd[1] == hf_config['intrusion'].lower()):
                    print ( "intrusion : " + str(currenttime) + " offset : " +  str (currenttime - lastintrutiontime) )
                    if currenttime > (lastintrutiontime + 60):
                        lastintrutiontime = currenttime
                        intrusion = True
            elif (check_cmd[0] == 'alim'):
                print ("Tension alim: " + check_cmd[1])
                alimserialvalue = float (check_cmd[1])
                alimserialvalid = True
            elif (check_cmd[0] == 'bat'):
                print ("Tension Batterie : " + check_cmd[1])
                batserialvalue = float (check_cmd[1])
                batserialvalid = True
            elif (check_cmd[0] == 'arret'):
                print ("Arret raspberry PI : ")
                subprocess.Popen(['sudo','shutdown','-h','now'])
            else:
                print ('Command inconnu : ' + buffer)
    if alarm_on:
        last['STATUS']['alarm'] = 'True'
    else:
        last['STATUS']['alarm'] = 'False'
    last['STATUS']['zone'] = str(alarm_zone)
    with open('last.ini', 'w') as configfile:
        last.write(configfile)      



def command_received (cmd, modem = False , source = None  ):
    reply = None
    global alarm_on
    global alarm_zone
    global email_object
    global email_config
    global siren_object
    global upsvoltage
    global upscurrent
    global upscapacity
    global exttemp
    global exthumidity

    print ('command reveived : ', cmd)
    check_cmd = cmd.lower()
    if (check_cmd == 'alarm on'):
        alarm_on = True
        alarm_zone = 1
        reply = 'Alarm on zone 1'
    if (check_cmd == 'alarm home'):
        alarm_on = True
        alarm_zone = 2
        reply = 'Alarm on zone 2'
    if (check_cmd == 'alarm off'):
        alarm_on = False
        reply = 'Alarm off'
    if (check_cmd == 'alarm status'):
            if alarm_on:
                if alarm_zone == 1:
                    reply = "alarm on zone 1"
                else:
                    reply = "alarm on zone 2"
            else:
                reply = "alarm off"
    if (check_cmd == 'cpu'):
        reply = 'CPU Temp : ' + str(MyUtils.get_cputemperature()) +'°C'
    if (check_cmd == 'ups'):
        reply = 'UPS: ' + f'{upsvoltage:2.2f}' + 'V / '+ f'{upscurrent:3.2f}' + ' mA / ' + f'{upscapacity:3.2f}' + '%'
    if (check_cmd == 'temp'):
        reply = 'TEMP: ' + f'{exttemp:2.2f}' + '°C / '+ f'{exthumidity:3.2f}' + ' %RH'
    if (check_cmd == 'siren on'):
        siren_object.on()
        reply = 'Set siren on'
    if (check_cmd == 'siren off'):
        siren_object.off()
        reply = 'Set siren off'
    if (check_cmd == 'siren force on'):
        siren_object.setmode('on')
        siren_object.on(0)
        reply = 'Set siren on , timeout 0'
    if (check_cmd == 'siren force off'):
        siren_object.off()
        reply = 'Set siren off'
    if (check_cmd == 'siren status'):
        reply = 'Siren status = ' + siren_object.ison()
    if (check_cmd) == 'cell info':
        text = ''
        if modem_object:
            text = modem_object.getlocation(str(modemid))
        reply = 'location : ' + text
    if alarm_on:
        last['STATUS']['alarm'] = 'True'
    else:
        last['STATUS']['alarm'] = 'False'
    last['STATUS']['zone'] = str(alarm_zone)
    with open('last.ini', 'w') as configfile:
        last.write(configfile)    
    return reply

def command_callback_telegram (cmd):
    """Command receive by telegram channel"""
    print ('cmd telegram: ' + cmd)
    msg = command_received (cmd,source='telegram')
    if msg:
        print ("answer telegram : " + msg)
    else:
        msg =  'Command unknown'
    return msg

def command_callback_mqtt (cmd):
    """Command receive by aws"""
    msg = None
    print ('string  aws: ' + cmd)
    msg = command_received (cmd,source='aws')
    if msg:
        print ("answer aws mqtt : " + msg)
        out = {}
        out['answer'] = msg
        out['serialnumber'] = MyUtils.get_serialnumber()
        json_data = json.dumps(out)
        return json_data
    else:
        msg =  'Command unknown'
    return msg

def command_callback_aws (cmd):
    """Command receive by aws"""
    return (command_callback_mqtt(cmd))


def command_callback_modem(cmd):
    """Command received by modem channel"""
    global modem_object
    global sms_config
    global modemid
    msg = None
    print ('cmd modem: ', cmd )
    msg = command_received (cmd,modem=True)
    if msg:
        modem_object.createsms(modemid, sms_config["receiver"], cmd +'\r\n'+msg)

def callback_pir (value):
    global pir
    global lastpirtime
    if (value == 1):
        currenttime = int(time.time())
        print ( "pir  : " + str(currenttime) + " offset : " +  str (currenttime - lastpirtime) )

        if currenttime > (lastpirtime + 60):
            lastpirtime = currenttime
            pir = True


def send_status (title , msg_status, filename1,filename2):
    """Send status to Email / Telegram / Mqtt  / Aws / SMS  """
    global email_object
    global email_config

    global telegram_object

    global modem_object
    global sms_config
    global modemid

    global aws_object
    global mqtt_object

    if modem_object:
        modem_object.createsms(
            modemid, sms_config["receiver"], msg_status
        )

    if email_object:
        email_object.sendmail(
            email_config["receiver"],
            title,
            msg_status,
            filename1,
            filename2
                )

    if telegram_object:
        telegram_object.send_message(msg_status)

    out = {}
    out['status'] = msg_status
    out['serialnumber'] = MyUtils.get_serialnumber()
    json_data = json.dumps(out)

    if aws_object:
        if aws_object.isconnected():
            aws_object.publish_message(json_data)

    if mqtt_object:
        if mqtt_object.isconnected():
            mqtt_object.publish_message(json_data)


def main():
    """Main program"""
    print("Alarm app")

    global hasmodem
    global hassms
    global hasemail
    global hastelegram
    global hasloop
    global hasusbcamera
    global hasipcamera
    global hasups
    global haswebserver
    global hasserial
    global hashf
    global hasaws
    global hasmqtt
    global hastemp
    global hassiren
    global haspir
    global hasbuzzer
    global hasheartbeat

    global modem_object
    global loop_object
    global email_object
    global telegram_object
    global usbcamera_object
    global ipcamera_object
    global webserver_object
    global serial_object
    global ups_object
    global aws_object
    global mqtt_object
    global siren_object
    global pir_object
    global buzzer_object

    global email_config
    global loop_config
    global telegram_config
    global sms_config
    global usbcamera_config
    global ipcamera_config
    global webserver_config
    global serial_config 
    global hf_config
    global aws_config
    global mqtt_config
    global siren_config
    global pir_config
    global buzzer_config
    global heartbeat_config
    global zone1_config
    global zone2_config

    global lastloopstatus
    global lastalarmstate
    global loopcheck
    global alarm_on
    global alarm_zone
    global alarm_ring
    global alarm_security
    global modemid
    global upsvoltage
    global upscurrent
    global upscapacity
    global pwlinegetvalue
    global basewebserver
    global intrusion
    global pir

    global alimserialvalue
    global alimserialvalid
    global alimseriallow

    global exttemp
    global exthumidity

    global startalarmdelay
    global heartbeattime

    global last


    config = configparser.ConfigParser()
    last = configparser.ConfigParser()
    config.read("config.ini")
    if (len (config.sections()) == 0):
        print ("config file missing !")
        exit(-1) 
    print(config.sections())
    if "GLOBAL" in config:
        global_config = config["GLOBAL"]
        print(global_config)
        for key in global_config:
            print(key + ":" + global_config[key])
        if global_config["modem"] == "yes":
            hasmodem = 1
        if global_config["sms"] == "yes":
            hassms = 1
        if global_config["loop"] == "yes":
            hasloop = 1
        if global_config["email"] == "yes":
            hasemail = 1
        if global_config["telegram"] == "yes":
            hastelegram = 1
        if global_config["usbcamera"] == "yes":
            hasusbcamera = 1
        if global_config["ipcamera"] == "yes":
            hasipcamera = 1
        if global_config["serial"] == "yes":
            hasserial = 1
        if global_config["ups"] == "yes":
            hasups = 1
        if global_config["webserver"] == "yes":
            haswebserver = 1
        if global_config["hf"] == "yes":
            hashf = 1
        if global_config["mqtt"] == "yes":
            hasmqtt = 1
        if global_config["aws"] == "yes":
            hasaws = 1
        if global_config["temp"] == "yes":
            hastemp = 1
        if global_config["siren"] == "yes":
            hassiren = 1
        if global_config["pir"] == "yes":
            haspir = 1
        if global_config["buzzer"] == "yes":
            hasbuzzer = 1
        if global_config["heartbeat"] == "yes":
            hasheartbeat = 1
        if global_config["default_state"] == "True":
            alarm_on = True
            alarm_zone = int (global_config["default_zone"])
            last['STATUS'] = {  'alarm': 'True' ,
                                'zone' : global_config["default_zone"]} 
            with open('last.ini', 'w') as configfile:
                last.write(configfile)              
        if global_config["default_state"] == "False":
            alarm_on = False
            last['STATUS'] = {  'alarm': 'False' ,
                                'zone' : global_config["default_zone"]} 
            with open('last.ini', 'w') as configfile:
                last.write(configfile)              

        if global_config["default_state"] == "Last":
            last.read("last.ini")
            if (len (last.sections()) == 0):
                print ("last status  file missing !")
                last['STATUS'] = {  'alarm': 'True' , 
                                     'zone' : global_config["default_zone"]} 
                print(last.sections())    
                with open('last.ini', 'w') as configfile:
                    last.write(configfile)        
            if last['STATUS']['alarm'] == "True":
                alarm_on = True
            else:
                alarm_on = False

        alarm_zone = int (last['STATUS']['zone'])
        alarmdelay = int(global_config["delayalarm"])


    if "EMAIL" in config:
        email_config = config["EMAIL"]
        print(email_config)
        for key in email_config:
            print(key + ":" + email_config[key])

    if "LOOP" in config:
        loop_config = config["LOOP"]
        print(loop_config)
        for key in loop_config:
            print(key + ":" + loop_config[key])

    if "TELEGRAM" in config:
        telegram_config = config["TELEGRAM"]
        print(telegram_config)
        for key in telegram_config:
            print(key + ":" + telegram_config[key])

    if "SMS" in config:
        sms_config = config["SMS"]
        print(sms_config)
        for key in sms_config:
            print(key + ":" + sms_config[key])

    if "USBCAMERA" in config:
        usbcamera_config = config["USBCAMERA"]
        print(usbcamera_config)
        for key in usbcamera_config:
            print(key + ":" + usbcamera_config[key])

    if "IPCAMERA" in config:
        ipcamera_config = config["IPCAMERA"]
        print(ipcamera_config)
        for key in ipcamera_config:
            print(key + ":" + ipcamera_config[key])

    if "WEBSERVER" in config:
        webserver_config = config["WEBSERVER"]
        print(webserver_config)
        for key in webserver_config:
            print(key + ":" + webserver_config[key])

    if "SERIAL" in config:
        serial_config = config["SERIAL"]
        print(serial_config)
        for key in serial_config:
            print(key + ":" + serial_config[key])

    if "HF" in config:
        hf_config = config["HF"]
        print(hf_config)
        for key in hf_config:
            print(key + ":" + hf_config[key])

    if "AWS" in config:
        aws_config = config["AWS"]
        print(aws_config)
        for key in aws_config:
            print(key + ":" + aws_config[key])

    if "MQTT" in config:
        mqtt_config = config["MQTT"]
        print(mqtt_config)
        for key in mqtt_config:
            print(key + ":" + mqtt_config[key])


    if "SIREN" in config:
        siren_config = config["SIREN"]
        print(siren_config)
        for key in siren_config:
            print(key + ":" + siren_config[key])

    if "TEMP" in config:
        temp_config = config["TEMP"]
        print(temp_config)
        for key in temp_config:
            print(key + ":" + temp_config[key])

    if "PIR" in config:
        pir_config = config["PIR"]
        print(pir_config)
        for key in pir_config:
            print(key + ":" + pir_config[key])

    if "BUZZER" in config:
        buzzer_config = config["BUZZER"]
        print(buzzer_config)
        for key in buzzer_config:
            print(key + ":" + buzzer_config[key])

    if "HEARTBEAT" in config:
        heartbeat_config = config["HEARTBEAT"]
        print(heartbeat_config)
        for key in heartbeat_config:
            print(key + ":" + heartbeat_config[key])


    if "ZONE1" in config:
        zone1_config = config["ZONE1"]
        print(zone1_config)
        for key in zone1_config:
            print(key + ":" + zone1_config[key])

    if "ZONE2" in config:
        zone2_config = config["ZONE2"]
        print(zone2_config)
        for key in zone2_config:
            print(key + ":" + zone2_config[key])

    if hasmodem:
        modem_object = MyModem()
        modemid = modem_object.getmodem()

    if hasloop:
        loop_object = MyLoop(
            loop_config["loop_enable"],
            loop_config["loop1_pin"],
            loop_config["loop1_invert"],
            loop_config["loop2_pin"],
            loop_config["loop2_invert"],
            loop_config["loop3_pin"],
            loop_config["loop3_invert"],
            loop_config["loop4_pin"],
            loop_config["loop4_invert"], 
        )
        loopcheck = loop_config["default_loop_check"]

    if hasemail:
        email_object = MyEmail(
            email_config["login"],
            email_config["password"],
            email_config["server"],
            email_config["port"],
        )

    if hasups:
        ups_object = MyUps('INA219')

    if hastelegram:
        telegram_object = MyTelegram(telegram_config["chat_id"],  telegram_config["token"],command_callback_telegram)

    if hasusbcamera:
        usbcamera_object = MyUsbCamera(usbcamera_config["port"])

    if hasipcamera:
        ipcamera_object = MyIpCamera(
            ipcamera_config["login"],
            ipcamera_config["password"],
            ipcamera_config["url"])

    if haswebserver:
        basewebserver = webserver_config["base"]
        webserver_object = MyWebServer(webserver_config["hostname"], webserver_config["port"], MyServer)

    if hasserial:
        serial_object = MySerial(serial_config["port"],serial_config["speed"],serial_config["bytesize"],serial_config["parity"],serial_config["stop"], command_serial)

    if hasaws:
        aws_object = MyAws( aws_config["endpoint"] , aws_config["ca_cert"], aws_config["certfile"] , aws_config["keyfile"] , aws_config["topicpub"],aws_config["topicsub"],  command_callback_aws)

    if hasmqtt:
        mqtt_object = MyMqtt( mqtt_config["endpoint"] ,mqtt_config["port"], mqtt_config["user"], mqtt_config["password"] , mqtt_config["topicpub"],mqtt_config["topicsub"],  command_callback_mqtt)


    if hassiren:
        siren_object = MySiren(siren_config["defaultmode"] ,siren_config["gpio"] , siren_config["timeout"] )

    if hastemp:
        temp_object = MyTemp (temp_config["type"], temp_config["address"])

    if haspir:
        pir_object = MyPir (pir_config["gpio"], callback_pir)

    if hasbuzzer:
        buzzer_object = MyBuzzer (buzzer_config["gpio"])
    
    msg_status = 'Alarm restart'
    if alarm_on:
        msg_status += ' on'
    else:
        msg_status += ' off'
    if alarm_zone == 1:
        msg_status += 'zone 1'
    else:
        msg_status += 'zone 2'
    send_status ('Alarm restart' , msg_status, None,None)

    startalarmdelay = 0
    if loop_object:
        loop_object.enablesetvalue(alarm_on)
    while True:
        print ('Alarm status : ' + str (alarm_on))

        if hasheartbeat:
            currenttime = int(time.time())
            if ( currenttime > (heartbeattime + int(heartbeat_config['delay']))):

                heartbeattime = currenttime
                out = {}
                heartbeatdata = {}
                gsmdata = {}
                if int(modemid) >= 0:
                    output1, success1 = MyUtils.system_call("mmcli --modem=" + modemid + " --location-get -J")
                    output2, success2 = MyUtils.system_call("mmcli --modem=" + modemid + " -J")
                if success1 and  success2:
                    data1 = json.loads(output1)
                    data2 = json.loads(output2)
                    gsmdata['cell']=data1["modem"]["location"]["3gpp"]
                    gsmdata['signal']=data2["modem"]["generic"]["signal-quality"]["value"]
                    gsmdata['access']=data2["modem"]["generic"]["access-technologies"]
                    gsmdata['state']=data2["modem"]["generic"]["state"]
                    out['gsm'] = gsmdata


                heartbeatdata['time'] = str(currenttime)
                if alarm_on:
                    heartbeatdata['alarm'] = 'on'
                else:
                    heartbeatdata['alarm'] = 'off'
                heartbeatdata['zone'] = str(alarm_zone)
                out['heartbeat'] = heartbeatdata
                out['serialnumber'] = MyUtils.get_serialnumber()
                json_data = json.dumps(out)

                if aws_object:
                    if aws_object.isconnected():
                        aws_object.publish_message(json_data)

                if mqtt_object:
                    if mqtt_object.isconnected():
                        mqtt_object.publish_message(json_data)


        if ups_object:
            upsvoltage = ups_object.readVoltage()
            upscapacity = ups_object.readCapacity()
            upscurrent = ups_object.readCurrent()
            pwlinegetvalue = ups_object.pwlinegetvalue()

            print ('pw connected : ' + str (pwlinegetvalue))
            print ('Voltage      : ' + f'{upsvoltage:2.2f}' + ' V' )
            print ('Current      : ' + f'{upscurrent:2.2f}' + ' mA' ) 
            print ('Capacity     : ' + f'{upscapacity:2.2f}' + ' %' )

        if modem_object:
            count = modem_object.getcountsms(str(modemid))
            if count > 0:
                paths = modem_object.getpathsms(str(modemid))
                for path in paths:
                    phone_number, content = modem_object.readsms(str(modemid), path)
                    modem_object.deletesms(str(modemid), path)
                    lines = content.splitlines()
                    if (lines[0] == sms_config["password"]) and (len (lines) == 2):
                        command_callback_modem(lines[1])
                    else:
                        email_object.sendmail(email_config["receiver"],'SMS received', 'SMS content : \r\n<br>'+content)

                    print(phone_number)
                    print(content)
        if lastalarmstate != alarm_on:
            if alarm_on:
                msg_status = "Alarm on zone " + str (alarm_zone)
                last['STATUS'] = {'alarm': 'True' , 
                                  'zone' : str(alarm_zone)}
                with open('last.ini', 'w') as configfile:
                    last.write(configfile)        
                if buzzer_object:
                    buzzer_object.setbuzzer (number = 1 , pulse = 1.0 , delay = 0.0)
            else:
                msg_status = "Alarm off"
                last['STATUS'] = {'alarm': 'False' , 
                                  'zone' : str(alarm_zone)}
                with open('last.ini', 'w') as configfile:
                    last.write(configfile)     
                if buzzer_object:
                    buzzer_object.setbuzzer (number = 2 , pulse = 0.25 , delay = 0.25)

            print ("change alarm status : " + msg_status)
            if loop_object:
                loop_object.enablesetvalue(alarm_on)

 
            lastalarmstate = alarm_on
            send_status ("alarm change", msg_status,None, None)


        if (alimseriallow == False) and (alimserialvalid == True) and (alimserialvalue  < 1 ):
            alimseriallow = True
            msg_status = "Alarm tension basse : " + str (alimserialvalue) + "V"
            send_status ("alarm change", msg_status,None, None)

        if (alimseriallow == True) and (alimserialvalid == True) and (alimserialvalue  > 1 ):
            alimseriallow = False
            msg_status = "Alarm retour tension  : " + str (alimserialvalue) + "V"
            send_status ("alarm change", msg_status,None, None)

        if temp_object:
            value = temp_object.readTemperature()
            if value:
                exttemp = value
                print ('Temp ext     : ' + f'{exttemp:2.2f}' + ' °C' )
            value = temp_object.readHumidity()
            if value:
                exthumidity = value
                print ('Humidity ext : ' + f'{exthumidity:2.2f}' + ' %' ) 

        if alarm_ring:
            filename = None
            filename2 = None

            if buzzer_object:
                buzzer_object.setbuzzer (number = 10 , pulse = 0.1 , delay = 0.1)
            if usbcamera_object:
                filename = usbcamera_object.capture_photo()
            if ipcamera_object:
                filename2 = ipcamera_object.capture_photo()
            msg_status = 'Ring'

            send_status ("Ring", msg_status,filename, filename2)

            if filename is not None:
                os.remove(filename)
            if filename2 is not None:
                os.remove(filename2)
            if alarm_ring:
                alarm_ring = False

        if alarm_on:
            print("alarme on ")
            if startalarmdelay != 0:
                currentalarmtime = int(time.time())
                if currentalarmtime > (startalarmdelay + alarmdelay):
                    startalarmdelay = 0
                    if siren_object:
                        siren_object.on()
                        buzzer_object.clearbuzzer()

            alarm_detect = False

            if ((alarm_zone == 1) and (zone1_config["intrusion"] == 'yes') ) or ((alarm_zone == 2) and (zone2_config["intrusion"] == 'yes')) : 
                if intrusion == True: 
                    alarm_detect = True
            if ((alarm_zone == 1) and (zone1_config["pir"] == 'yes') ) or ((alarm_zone == 2) and (zone2_config["pir"] == 'yes')) : 
                if pir == True: 
                    alarm_detect = True
            if ((alarm_zone == 1) and (zone1_config["security"] == 'yes') ) or ((alarm_zone == 2) and (zone2_config["security"] == 'yes')) : 
                if alarm_security == True: 
                    alarm_detect = True

            if alarm_detect == True:
                filename = None
                filename2 = None
                startalarmdelay =  int(time.time())
                if buzzer_object:
                    buzzer_object.setbuzzer (number = alarmdelay , pulse = 0.25 , delay = 0.75)
                if usbcamera_object:
                    filename = usbcamera_object.capture_photo()
                if ipcamera_object:
                    filename2 = ipcamera_object.capture_photo()
                msg_status = ''
                if intrusion:
                    msg_status += 'Intrusion '
                if pir:
                    msg_status += 'Pir '
                if alarm_security:
                    msg_status += 'Security keyboard '
                if msg_status == '':
                    msg_status = "Unknown"

                send_status ("Alarm detected", msg_status,filename, filename2)

                if filename is not None:
                    os.remove(filename)
                if filename2 is not None:
                    os.remove(filename2)
                if intrusion:
                    intrusion = False
                if pir:
                    pir = False
                if alarm_security:
                    alarm_security = False

            if loop_object:
                loop = False
                if ((alarm_zone == 1) and (zone1_config["loop1"] == 'yes') ) or ((alarm_zone == 2) and (zone2_config["loop1"] == 'yes')) : 
                    if loop_object.pinoutgetvalue(1) == True: 
                        loop = True
                if ((alarm_zone == 1) and (zone1_config["loop2"] == 'yes') ) or ((alarm_zone == 2) and (zone2_config["loop2"] == 'yes')) : 
                    if loop_object.pinoutgetvalue(2) == True: 
                        loop = True
                if ((alarm_zone == 1) and (zone1_config["loop3"] == 'yes') ) or ((alarm_zone == 2) and (zone2_config["loop3"] == 'yes')) : 
                    if loop_object.pinoutgetvalue(3) == True: 
                        loop = True
                if ((alarm_zone == 1) and (zone1_config["loop4"] == 'yes') ) or ((alarm_zone == 2) and (zone2_config["loop4"] == 'yes')) : 
                    if loop_object.pinoutgetvalue(4) == True: 
                        loop = True        
                print("line " + str(loop))

            if loop and loopcheck:
                if loop and not lastloopstatus:
                    filename = None
                    filename2 = None
                    startalarmdelay = int(time.time())
                    if buzzer_object:
                        buzzer_object.setbuzzer (number = alarmdelay , pulse = 0.25 , delay = 0.75)
                    msg_status = "Coupure boucle"
                    if usbcamera_object:
                        filename = usbcamera_object.capture_photo()
                    if ipcamera_object:
                        filename2 = ipcamera_object.capture_photo()

                    send_status ("Alarm detected", msg_status,filename, filename2)

                    if filename is not None:
                        os.remove(filename)
                    if filename2 is not None:
                        os.remove(filename2)

            lastloopstatus = loop
        else:
            startalarmdelay = 0
            if siren_object:
                siren_object.off()
            intrusion = False
            pir = False
            alarm_security = False
        time.sleep(1)



if __name__ == "__main__":
    main()
