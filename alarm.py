#!/bin/python
#SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
#SPDX-License-Identifier: ISC

from mymodem import *
from myloop import *
from myemail import *
from mytelegram import *
from myusbcamera import *
from myipcamera import *
import configparser
import os 


def main():
    print("Alarm app")
    hasmodem = 0 
    hassms = 0 
    hasemail = 0 
    hastelegram = 0
    hasloop = 0 
    hasusbcamera = 0 
    hasipcamera = 0

    modemObject = None
    loopObject = None
    emailObject = None
    telegramObject = None
    usbcameraObject = None
    ipcameraObject = None
    lastloopstatue = False ; 
    loopcheck = False


    config = configparser.ConfigParser()
    config.read ('config.ini')
    print (config.sections())
    if 'GLOBAL' in config:
        global_config = config['GLOBAL']
        print (global_config )
        for key in global_config:
            print (key + ':' + global_config[key])
        if global_config['modem'] == 'yes':
            hasmodem = 1
        if global_config['sms'] == 'yes':
            hassms = 1            
        if global_config['loop'] == 'yes':
            hasloop = 1     
        if global_config['email'] == 'yes':
            hasemail = 1     
        if global_config['telegram'] == 'yes':
            hastelegram = 1    
        if global_config['usbcamera'] == 'yes':
            hasusbcamera = 1   
        if global_config['ipcamera'] == 'yes':
            hasipcamera = 1   

    if 'EMAIL' in config:
        email_config = config['EMAIL']
        print (email_config)
        for key in email_config:
            print (key + ':' + email_config[key])

    if 'LOOP' in config:
        loop_config = config['LOOP']
        print (loop_config)
        for key in loop_config:
            print (key + ':' + loop_config[key])

    if 'TELEGRAM' in config:
        telegram_config = config['TELEGRAM']
        print (telegram_config)
        for key in telegram_config:
            print (key + ':' + telegram_config[key])

    if 'SMS' in config:
        sms_config = config['SMS']
        print (sms_config)
        for key in sms_config:
            print (key + ':' + sms_config[key])

    if 'USBCAMERA' in config:
        usbcamera_config = config['USBCAMERA']
        print (usbcamera_config)
        for key in usbcamera_config:
            print (key + ':' + usbcamera_config[key])

    if 'IPCAMERA' in config:
        ipcamera_config = config['IPCAMERA']
        print (ipcamera_config)
        for key in ipcamera_config:
            print (key + ':' + ipcamera_config[key])

    if hasmodem:
        modemObject = mymodem()

    if hasloop:
        loopObject = myloop(loop_config['loop_pin'], loop_config['loop_enable'], loop_config['loop_invert'])
        loopcheck = loop_config['default_loop_check']

        
    if hasemail:
        emailObject = myemail(email_config['login'], email_config['password'], email_config['server'],email_config['port'])

    if hastelegram:
        telegramObject = mytelegram (telegram_config['token'])

    if hasusbcamera:
        usbcameraObject = myusbcamera(usbcamera_config['port'])

    if hasipcamera:
        ipcameraObject = myipcamera(ipcamera_config['login'],ipcamera_config['password'], ipcamera_config['url'])

    if modemObject:
        modemid = modemObject.getmodem()
        print ('modemid ' + str(modemid))
        modemObject.createsms (modemid, sms_config['receiver'],'Alarm restart' )
        count = modemObject.getcountsms(str(modemid)) ; 
        print (count)

    if emailObject:
        emailObject.sendmail(email_config['receiver'],"Alarm restart", "Alarm restarted")

    while True:
        if modemObject:
            count = modemObject.getcountsms(str(modemid)) ; 
            print (count)
            if ( count > 0 ):
                paths = modemObject.getpathsms(str(modemid))
                for path in paths :
                    phone_number , content = modemObject.readsms (str(modemid),path)
                    print (phone_number)
                    print (content)

        if loopObject:
            loop = loopObject.pinoutgetvalue()
            print ('line ' + str (loop))
        if (loop and loopcheck):
            if ( loop and not lastloopstatue):
                filename = None 
                filename2 = None
                if usbcameraObject:
                    filename = usbcameraObject.capture_photo()
                if ipcameraObject:
                    filename2 = ipcameraObject.capture_photo()
                if emailObject:
                    emailObject.sendmail(email_config['receiver'],"Alarm Detected", "Detection alarm boucle",filename, filename2)
                if modemObject:
                    modemObject.createsms (modemid, sms_config['receiver'],'Detection Alarm boucle' )    
                if (filename is not None):
                    os.remove(filename)
                if (filename2 is not None):
                    os.remove(filename2)
        lastloopstatue = loop
            

        time.sleep(1)


if __name__ == "__main__":
    main()