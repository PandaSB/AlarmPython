# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISCimport json

import sqlite3
import os.path
import paho.mqtt.client as mqtt
import configparser
import json


DB_Name             = None
MQTT_Broker         = None
MQTT_Port           = None
Keep_Alive_Interval = None
MQTT_Topic          = None
MQTT_Username       = None
MQTT_Password       = None

class DatabaseManager():
    def __init__(self):
        global DB_Name
        try:
            self.conn = sqlite3.connect(DB_Name)
            self.conn.execute('pragma foreign_keys = on')
            self.conn.commit()
            self.cur = self.conn.cursor()
        except sqlite3.Error as e:
            print(e)
		
    def add_del_update_db_record(self, sql_query, args=()):
        try:
            self.cur.execute(sql_query, args)
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def __del__(self):
        try:
            self.cur.close()
            self.conn.close()
        except sqlite3.Error as e:
            print(e)


def on_connect(client, userdata, flags, rc, properties=None):
    global MQTT_Topic
    client.subscribe(MQTT_Topic, 0)


def on_message(client, userdata, message):
    time = ''
    alarm_status = ''
    alarm_zone = ''
    serialnumber = ''
    cid = ''
    lac = ''
    mcc = ''
    mnc = ''
    tac = ''
    signal = ''
    access = ''
    state = ''


    msg = message.payload.decode("utf-8")
    print ("MQTT Data Received...")
    print ("MQTT Topic: " + message.topic)
    print ("Data: " + msg)

    try:
        json_Dict = json.loads(msg)
        time         = json_Dict['heartbeat']['time']
        alarm_status = json_Dict['heartbeat']['alarm']
        alarm_zone   = json_Dict['heartbeat']['zone']
        serialnumber = json_Dict['serialnumber']
        cid = json_Dict['gsm']['cell']['cid']
        lac = json_Dict['gsm']['cell']['lac']
        mcc = json_Dict['gsm']['cell']['mcc']
        mnc = json_Dict['gsm']['cell']['mnc']
        tac = json_Dict['gsm']['cell']['tac']
        signal = json_Dict['gsm']['signal']
        access = json_Dict['gsm']['access'][0]
        state  = json_Dict['gsm']['state']

        print ("time   : " + time)
        print ('alarm  : ' + alarm_status + ' ' + alarm_zone)
        print ('gsm    : cid:' + cid + ' lac:' + lac + ' mcc:' + mcc + ' mnc:' + mnc + ' tac:' + tac )
        print ('signal : ' + signal +' (' + access + ') ' + state )

        dbObj = DatabaseManager()
        dbObj.add_del_update_db_record("insert into Alarm_HeartBeat ( SerialNumber, Time , CellCid ,CellLac ,CellMcc ,CellMnc ,Celltac ,Signal ,Acess ,State ) values (?,?,?,?,?,?,?,?,?,?)",[serialnumber, time, cid, lac, mcc, mnc, tac, signal, access, state ])
        dbObj.add_del_update_db_record("insert into Alarm_Status ( SerialNumber, Time, AlarmStatus, AlarmZone ) values (?,?,?,?)", [serialnumber, time, alarm_status, alarm_zone])
        del (dbObj)
        print ("Inserted Data into Database.")

    except:
        print ('Error decode')




def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    pass

def create_database():
    global DB_Name
    sql_statements = [ 
        """ create table if not exists Alarm_HeartBeat (
            id integer primary key autoincrement,
            SerialNumber text,
            Time text,
            CellCid text,
            CellLac text,
            CellMcc text,
            CellMnc text,
            Celltac text,
            Signal text,
            Acess text,
            State text
            );""",
        """ create table if not exists Alarm_Status (
            id integer primary key autoincrement,
            SerialNumber text,
            Time text,
            AlarmStatus text,
            AlarmZone text
            ); """]
    try:
        with  sqlite3.connect(DB_Name) as conn:
            curs = conn.cursor()
            for statement in sql_statements:
                curs.execute (statement)
            conn.commit()
    except sqlite3.Error as e:
        print(e)        
    curs.close()
    conn.close()

def main():

    global MQTT_Broker         
    global MQTT_Port           
    global Keep_Alive_Interval 
    global MQTT_Username       
    global MQTT_Password
    global MQTT_Topic
    global DB_Name

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
        MQTT_Broker = global_config["broker"]
        MQTT_Port = int(global_config["port"])
        Keep_Alive_Interval  = int (global_config["keepaliveinterval"])
        MQTT_Username = global_config["username"]
        MQTT_Password   = global_config["password"]
        MQTT_Topic  = global_config["topic"]
        DB_Name  = global_config["dbname"]
   
    if not os.path.isfile(DB_Name):
       create_database() 

    mqttc = mqtt.Client(protocol=mqtt.MQTTv5, transport = "websockets")
    mqttc.username_pw_set(username=MQTT_Username,password=MQTT_Password)


    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_subscribe = on_subscribe

    result = mqttc.connect( MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))
    print ('result connection mqtt : ' + str(result))

    if (result == 0 ):
        print ("Connect ok mqtt")
        mqttc.loop_forever()


if __name__ == "__main__":
    main()