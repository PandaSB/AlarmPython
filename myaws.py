# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

# sudo apt-get install python3-paho-mqtt

import time
import paho.mqtt.client as mqtt
from threading import Thread
import ssl
import os


myaws_endpoint = ''
myaws_topic = ''

class MyAws:
    ca_certs = ""
    certfile = ""
    keyfile  = ""
    client   = None 

    def on_connect(client, userdata, flags, rc, properties=None, last=None):
        global myaws_endpoint
        global myaws_topic

        print ('connected to endpoint ' + myaws_endpoint + ' with result code '+ str(rc))
        print ('userdata: '+ str(userdata) + ', flags: ' + str(flags) + ' properties: ' + str(properties))

        if rc == 0:
            print("Connected to AWS IoT Core successfully.")
            print(" subscribing to topic " + self.topic)
            self.client.subscribe(myaws_topic, qos=0, options=None, properties=None)
        else:
            print(f"Connection error: {rc}")

    def on_message(client, userdata, msg):
        print ('received message: topic: ' + msg.topic +' payload: '+ msg.payload.decode())

    def publish_message(self, message):
        global myaws_topic
        try:
            self.client.publish(myaws_topic, payload=message, qos=1, retain=True)
            print("Published " + message + " to AWS IoT Core")
        except Exception as e:
            print(f"Error publishing message: {e}")
            

    def start_pulling ( self ):
        self.client.loop_start()
        while True:
            time.sleep(1)



    def __init__(self, endpoint , ca_certs, keyfile ,  certfile , topic, _callback = None):
            global myaws_endpoint
            global myaws_topic
            myaws_endpoint  = endpoint
            self.ca_certs  = ca_certs
            self.certfile  = certfile
            self.keyfile   = keyfile
            myaws_topic    = topic 

            print ("endpoint : " + myaws_endpoint)
            print ("ca_certs : " + self.ca_certs)
            print ("certfile : " + self.certfile)
            print ("keyfile  : " + self.keyfile)
            print ("topic    : " + myaws_topic)
  

            for f in [self.ca_certs, self.certfile, self.keyfile]:
                print ("certificat : "+f)
                if not os.path.exists(f): 
                    print("Certificate file(s) not found : " + f)
                    return

            self.client = mqtt.Client()
    
            try:
                self.client.tls_set(ca_certs=self.ca_certs, certfile=self.certfile, keyfile=self.keyfile, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
            except FileNotFoundError as e:
                print(f"Error: Certificate file not found - {e}")
                return 

            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
    
            self.client.connect(myaws_endpoint, 8883, 60)

            thread = Thread(target=self.start_pulling)
            thread.start()