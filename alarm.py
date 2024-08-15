#!/bin/python
# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import configparser
import os
import time

from myemail import MyEmail
from myipcamera import MyIpCamera
from myloop import MyLoop
from mymodem import MyModem
from mytelegram import MyTelegram
from myusbcamera import MyUsbCamera


def main():
    """Main program"""
    print("Alarm app")
    hasmodem = 0
    hassms = 0
    hasemail = 0
    hastelegram = 0
    hasloop = 0
    hasusbcamera = 0
    hasipcamera = 0

    modem_object = None
    loop_object = None
    email_object = None
    telegram_object = None
    usbcamera_object = None
    ipcamera_object = None
    lastloopstatue = False
    loopcheck = False

    config = configparser.ConfigParser()
    config.read("config.ini")
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

    if hastelegram:
        telegram_object = MyTelegram(telegram_config["token"])

    if hasusbcamera:
        usbcamera_object = MyUsbCamera(usbcamera_config["port"])

    if hasipcamera:
        ipcamera_object = MyIpCamera(
            ipcamera_config["login"],
            ipcamera_config["password"],
            ipcamera_config["url"],
        )

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
        if modem_object:
            count = modem_object.getcountsms(str(modemid))
            print(count)
            if count > 0:
                paths = modem_object.getpathsms(str(modemid))
                for path in paths:
                    phone_number, content = modem_object.readsms(str(modemid), path)
                    print(phone_number)
                    print(content)

        if loop_object:
            loop = loop_object.pinoutgetvalue()
            print("line " + str(loop))
        if loop and loopcheck:
            if loop and not lastloopstatue:
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
                if filename is not None:
                    os.remove(filename)
                if filename2 is not None:
                    os.remove(filename2)
        lastloopstatue = loop

        time.sleep(1)


if __name__ == "__main__":
    main()
