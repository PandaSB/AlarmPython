#!/bin/python
# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import configparser
import os
import time
import shutil
import datetime
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
from myaws import MyAws
from mytemp import MyTemp


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
hastemp             = 0

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
temp_object         = None

lastloopstatus      = False
loopcheck           = False
alarm_on            = False
lastalamstate       = False
intrusion           = False
lastalarmstate      = False
lastintrutiontime   = 0

email_config        = None
loop_config         = None
telegram_config     = None
sms_config          = None
usbcamera_config    = None
ipcamera_config     = None
serial_config       = None
hf_config           = None
aws_config          = None
temp_config         = None

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
    global hashf
    global hf_config
    global intrusion
    global alimserialvalue
    global alimserialvalid
    global batserialvalue
    global batserialvalid
    global lastintrutiontime

    check_cmd = buffer.lower().split()
    if (len(check_cmd) > 0):
        if (check_cmd[0] == 'hfrecu'):
            """ gestion alarme télécommande """
            if (check_cmd[1] == hf_config['onalarm']):
                print ("alarme on : ")
                alarm_on = True
            if (check_cmd[1] == hf_config['offalarm']):
                print ("alarme off : ")
                alarm_on = False
            """ fin gestion alarme télécommande  """

            """ gestion infrarouge  """
            if (check_cmd[1] == hf_config['intrusion']):
                currenttime = int(time.time())
                print ( "intrusion : " + str(currenttime) + "offset : " +  str (currenttime - lastintrutiontime) )
                if currenttime > (lastintrutiontime + 60):
                    lastintrutiontime = currenttime
                    intrusion = True

            """ fin gestion infrarouge """
        elif (check_cmd[0] == 'alim'):
            print ("Tension alim: " + check_cmd[1])
            alimserialvalue = float (check_cmd[1])
            alimserialvalid = True
        elif (check_cmd[0] == 'bat'):
            print ("Tension Batterie : " + check_cmd[1])
            batserialvalue = float (check_cmd[1])
            batserialvalid = True

        else:
            print ('Command inconnu : ' + buffer) 

def command_received (cmd, modem = False , telegram = False):
    reply = None
    global alarm_on
    global email_object
    global email_config
    global upsvoltage
    global upscurrent
    global upscapacity
    global exttemp
    global exthumidity

    print ('command reveived : ', cmd)
    check_cmd = cmd.lower()
    if (check_cmd == 'alarm on'):
        alarm_on = True
        reply = 'Alarm activated'
    if (check_cmd == 'alarm off'):
        alarm_on = False
        reply = 'Alarm desactivated'
    if (check_cmd == 'cpu'):
        reply = 'CPU Temp : ' + str(MyUtils.get_cputemperature()) +'°C'
    if (check_cmd == 'ups'):
        reply = 'UPS: ' + f'{upsvoltage:2.2f}' + 'V - '+ f'{upscurrent:3.2f}' + ' mA - ' + f'{upscapacity:3.2f}' + '%'
    if (check_cmd == 'temp'):
        reply = 'TEMP: ' + f'{exttemp:2.2f}' + '°C - '+ f'{exthumidity:3.2f}' + ' %RH'
    return reply

def command_callback_telegram (cmd):
    """Command receive by telegram channel"""
    print ('cmd telegram: ' + cmd)
    msg = command_received (cmd,telegram=True)
    if msg:
        return msg
    else:
        return 'Command unknown'

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
    global hastemp

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

    global lastloopstatus
    global lastalarmstate
    global loopcheck
    global alarm_on
    global modemid
    global upsvoltage
    global upscurrent
    global upscapacity
    global pwlinegetvalue
    global basewebserver
    global intrusion

    global alimserialvalue
    global alimserialvalid
    global alimseriallow

    global exttemp
    global exthumidity


    config = configparser.ConfigParser()
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
        if global_config["aws"] == "yes":
            hasaws = 1
        if global_config["temp"] == "yes":
            hastemp = 1
        if global_config["default_state"] == "True":
            alarm_on = True


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

    if "TEMP" in config:
        temp_config = config["TEMP"]
        print(temp_config)
        for key in temp_config:
            print(key + ":" + temp_config[key])

    if hasmodem:
        modem_object = MyModem()

    if hasloop:
        loop_object = MyLoop(
            loop_config["loop_pin"],
            loop_config["loop_enable"],
            loop_config["loop_invert"],
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
        aws_object = MyAws( aws_config["endpoint"] , aws_config["ca_cert"], aws_config["certfile"] , aws_config["keyfile"] , aws_config["topic"], None)

    if hastemp:
        temp_object = MyTemp (temp_config["type"], temp_config["address"])
    
    if aws_object:
        aws_object.publish_message("Alarm restart")

    if serial_object:
        serial_object.write ("Serial open \r\n")

    if modem_object:
        modemid = modem_object.getmodem()
        print("modemid " + str(modemid))
        if hassms:
            modem_object.createsms(modemid, sms_config["receiver"], "Alarm restart")
            count = modem_object.getcountsms(str(modemid))
            print(count)

    if email_object:
        email_object.sendmail(
            email_config["receiver"], "Alarm restart", "Alarm restarted"
        )

    if telegram_object:
        print("Telegram bot activate")


    while True:
        print ('Alarm status : ' + str (alarm_on))
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
                msg_status = "Alarm on"
            else:
                msg_status = "Alarm off"
            print ("change alarm status : " + msg_status)
            if email_object:
                        email_object.sendmail(
                            email_config["receiver"],
                            "Alarm change",
                            msg_status,
                            None,
                            None
                        )
            if modem_object:
                modem_object.createsms(
                    modemid, sms_config["receiver"], msg_status
                )
            if telegram_object:
                telegram_object.send_message(msg_status)
            lastalarmstate = alarm_on



        if (alimseriallow == False) and (alimserialvalid == True) and (alimserialvalue  < 1 ):
            alimseriallow = True
            msg_status = "Alarm tension basse : " + str (alimserialvalue) + "V"
            if email_object:
                        email_object.sendmail(
                            email_config["receiver"],
                            "Alarm change",
                            msg_status,
                            None,
                            None
                        )
            if modem_object:
                modem_object.createsms(
                    modemid, sms_config["receiver"], msg_status
                )
            if telegram_object:
                telegram_object.send_message(msg_status)

        if (alimseriallow == True) and (alimserialvalid == True) and (alimserialvalue  > 1 ):
            alimseriallow = False
            msg_status = "Alarm retour tension  : " + str (alimserialvalue) + "V"
            if email_object:
                        email_object.sendmail(
                            email_config["receiver"],
                            "Alarm change",
                            msg_status,
                            None,
                            None
                        )
            if modem_object:
                modem_object.createsms(
                    modemid, sms_config["receiver"], msg_status
                )
            if telegram_object:
                telegram_object.send_message(msg_status)

        if temp_object:
            value = temp_object.readTemperature()
            if value:
                exttemp = value
                print ('Temp ext     : ' + f'{exttemp:2.2f}' + ' °C' )
            value = temp_object.readHumidity()
            if value:
                exthumidity = value
                print ('Humidity ext : ' + f'{exthumidity:2.2f}' + ' %' ) 



        if alarm_on:
            print("alarme on ")

            if intrusion:
                intrusion = False
                filename = None
                filename2 = None
                if usbcamera_object:
                    filename = usbcamera_object.capture_photo()
                if ipcamera_object:
                    filename2 = ipcamera_object.capture_photo()
                msg_status = "Intrusion "
                if email_object:
                            email_object.sendmail(
                                email_config["receiver"],
                                "Alarm change",
                                msg_status,
                                filename,
                                filename2
                            )
                if modem_object:
                    modem_object.createsms(
                        modemid, sms_config["receiver"], msg_status
                    )
                if telegram_object:
                    telegram_object.send_message(msg_status)

                if filename is not None:
                    os.remove(filename)
                if filename2 is not None:
                    os.remove(filename2)

            if loop_object:
                loop = loop_object.pinoutgetvalue()
                print("line " + str(loop))
            if loop and loopcheck:
                if loop and not lastloopstatus:
                    filename = None
                    filename2 = None
                    if usbcamera_object:
                        filename = usbcamera_object.capture_photo()
                    if ipcamera_object:
                        filename2 = ipcamera_object.capture_photo()
                    if email_object:
                        email_object.sendmail(
                            email_config["receiver"],
                            "Alarm Detected",
                            "Detection alarm boucle",
                            filename,
                            filename2,
                        )
                    if modem_object:
                        modem_object.createsms(
                            modemid, sms_config["receiver"], "Detection Alarm boucle"
                        )
                    if telegram_object:
                        telegram_object.send_message("Detection Alarm boucle")

                    if filename is not None:
                        os.remove(filename)
                    if filename2 is not None:
                        os.remove(filename2)
            lastloopstatus = loop
        time.sleep(1)


if __name__ == "__main__":
    main()
