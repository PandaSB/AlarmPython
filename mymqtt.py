# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

# sudo apt-get install python3-paho-mqtt
# add user to mosquito mqtt broker : mosquitto_passwd -b passwordfile user password


import time
import paho.mqtt.client as mqtt
from threading import Thread
import os
import json
from myutils import MyUtils

mymqtt_endpoint = ''
mymqtt_topicsub = ''
mymqtt_topicpub = ''


class MyMqtt:
    client   = None 
    connect = False
    callback = None

    def on_connect(self , client , userdata,flags, reason, properties = None ):
        global mymqtt_endpoint
        global mymqtt_topicsub
        global mymqtt_topicpub

        client   = None 
        connect = False
        callback = None

        print ('connected to endpoint ' + mymqtt_endpoint + ' with result code '+ str (reason))
        print ('userdata: '+ str(userdata) + ', flags: ' + str(flags) + ' properties: ' + str(properties))

        if reason == 0:
            print("Connected to mqtt successfully.")
            self.connect = True
            print(" subscribing to topic " + mymqtt_topicsub + '/all')
            print(" subscribing to topic " + mymqtt_topicsub + '/' + MyUtils.get_serialnumber())
            self.client.subscribe(mymqtt_topicsub + '/all', qos=0, options=None, properties=None)
            self.client.subscribe(mymqtt_topicsub + '/' + MyUtils.get_serialnumber(), qos=0, options=None, properties=None)
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
                self.client.publish(mymqtt_topicpub, payload=reply)

    def publish_message(self, message):
        global mymqtt_topicpub
        print ("Published " + message + " to mqtt")
        if (self.connect == True ):
            try:
                self.client.publish(mymqtt_topicpub, payload=message)
                print("Published ok " + message + ' on ' + mymqtt_topicpub)
            except Exception as e:
                print(f"Error publishing message: {e}")

    def __on_log(self, client, userdata, level, buf):
        self.logger.debug("{0}, {1}, {2}, {3}".format(client, userdata, level, buf))

    def start_pulling ( self ):
        self.client.loop_start()
        while True:
            time.sleep(1)

    def isconnected(self):
        return self.connect

    def __init__(self, endpoint , port, user, passwd ,  topicpub, topicsub, _callback = None):

        global mymqtt_endpoint
        global mymqtt_topicsub
        global mymqtt_topicpub
        mymqtt_endpoint  = endpoint
        mymqtt_topicsub    = topicsub
        mymqtt_topicpub    = topicpub
        self.callback = _callback

        try: 
            self.client = mqtt.Client(protocol=mqtt.MQTTv5, transport = "websockets")

            #self.client.tls_set()

            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.username_pw_set(username=user,password=passwd)

            result = self.client.connect(host= mymqtt_endpoint, port=int(port), keepalive=60, clean_start=True , properties= None )
        except:
            result = -1
        print ('result connection mqtt : ' + str(result))

        if (result == 0 ):
            print ("Connect ok mqtt")

        thread = Thread(target=self.start_pulling)
        thread.start()


