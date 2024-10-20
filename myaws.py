# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

# sudo apt-get install python3-paho-mqtt

import time
import paho.mqtt.client as mqtt
from threading import Thread
import ssl
import os
import json
from myutils import MyUtils


import logging
logging.basicConfig(level=logging.INFO)


myaws_endpoint = ''
myaws_topicsub = ''
myaws_topicpub = ''

class MyAws:
    ca_certs = ""
    certfile = ""
    keyfile  = ""
    client   = None 
    connect = False
    callback = None

    def on_connect(self , client , userdata,flags, reason, properties = None ):
        global myaws_endpoint
        global myaws_topicsub
        global myaws_topicpub

        print ('connected to endpoint ' + myaws_endpoint + ' with result code '+ str (reason))
        print ('userdata: '+ str(userdata) + ', flags: ' + str(flags) + ' properties: ' + str(properties))

        if reason == 0:
            print("Connected to AWS IoT Core successfully.")
            self.connect = True
            print(" subscribing to topic " + myaws_topicsub + '/all')
            print(" subscribing to topic " + myaws_topicsub + '/' + MyUtils.get_serialnumber())

            self.client.subscribe(myaws_topicsub + '/all', qos=0, options=None, properties=None)
            self.client.subscribe(myaws_topicsub + '/' + MyUtils.get_serialnumber(), qos=0, options=None, properties=None)
        else:
            print(f'Connection error:' + str (reason))
        print ("on connect done")

    def on_message(self, client, userdata, msg):
        reply = None
        print ('received message: topic: ' + msg.topic +' payload: '+ msg.payload.decode())
        try:
            data = json.loads (msg.payload.decode())
            cmd = data['cmd']
            if (self.callback):
                reply = self.callback (cmd)
        except Exception as e:
            print ("Message not a command")
        if reply:
            if (reply != "Command unknown"):
                self.client.publish(myaws_topicpub, payload=reply)

    def __on_log(self, client, userdata, level, buf):
        self.logger.debug("{0}, {1}, {2}, {3}".format(client, userdata, level, buf))

    def publish_message(self, message):
        global myaws_topicpub
        print ("Published " + message + " to AWS IoT Core")
        if (self.connect == True ):
            try:
                self.client.publish(myaws_topicpub, payload=message)
                print("Published ok " + message + 'on ' + myaws_topicpub)
            except Exception as e:
                print(f"Error publishing message: {e}")
            

    def start_pulling ( self ):
        self.client.loop_start()
        while True:
            time.sleep(1)

    def isconnected(self):
        return self.connect

    def __init__(self, endpoint , ca_certs, keyfile ,  certfile , topicpub, topicsub, _callback = None):
        global myaws_endpoint
        global myaws_topicsub
        global myaws_topicpub
        myaws_endpoint  = endpoint
        self.ca_certs  = ca_certs
        self.certfile  = certfile
        self.keyfile   = keyfile
        self.callback = _callback
        myaws_topicsub    = topicsub
        myaws_topicpub    = topicpub

        print ("endpoint : " + myaws_endpoint)
        print ("ca_certs : " + self.ca_certs)
        print ("certfile : " + self.certfile)
        print ("keyfile  : " + self.keyfile)
        print ("topicsub : " + myaws_topicsub)
        print ("topicpub : " + myaws_topicpub)


        self.client = mqtt.Client(protocol=mqtt.MQTTv5)

        try:
            self.client.tls_set(ca_certs=self.ca_certs, certfile=self.certfile, keyfile=self.keyfile, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
        except FileNotFoundError as e:
            print(f"Error: Certificate file not found - {e}")
            return

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_log = self.__on_log

        result = self.client.connect(host= myaws_endpoint, port=8883, keepalive=60, clean_start=True , properties= None )
        print ('result connection aws: ' + str(result))

        if (result == 0 ):
            print ("Connect ok aws Iot")

        thread = Thread(target=self.start_pulling)
        thread.start()