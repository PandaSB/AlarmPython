# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

#sudo apt-get install python3-matplotlib
#sudo apt-get install python3-paho-mqtt
#sudo apt-get install python3-flask

from flask import Flask, render_template, request, make_response
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import time



HOST_NAME = "0.0.0.0"
HOST_PORT = 7080
DB_Name =  "alarm.db"

app = Flask(__name__)
app.debug = True

def get_Signal_Alarm_HeartBeat(serialnumber=None):
    results = ''
    if serialnumber:
        if serialnumber.lower() == "all":
            condition = ''
        else:
            condition  = "WHERE SerialNumber LIKE '{0}'".format(serialnumber)
    else:
         condition = ''
    try:
        with  sqlite3.connect(DB_Name) as conn:
            curs = conn.cursor()
            curs.execute("SELECT Time, Signal, Acess,State  FROM Alarm_HeartBeat {0}".format(condition))
            results = curs.fetchall()
    except sqlite3.Error as e:
        print (e)
    curs.close()
    conn.close()
    return results    

def get_Data_Alarm_HeartBeat(serialnumber=None):
    results = ''
    if serialnumber:
        if serialnumber.lower() == "all":
            condition = ''
        else:
            condition  = "WHERE SerialNumber LIKE '{0}'".format(serialnumber)
    else:
         condition = ''
    try:
        with  sqlite3.connect(DB_Name) as conn:
            curs = conn.cursor()
            curs.execute("SELECT * FROM Alarm_HeartBeat {0}".format(condition))
            results = curs.fetchall()
    except sqlite3.Error as e:
        print (e)
    curs.close()
    conn.close()
    return results

def get_UniqueSerialNumber_Alarm_HeartBeat():
    results = ''
    try:
        with  sqlite3.connect(DB_Name) as conn:
            curs = conn.cursor()
            curs.execute("SELECT DISTINCT SerialNumber FROM Alarm_HeartBeat")
            results = curs.fetchall()
    except sqlite3.Error as e:
        print (e)
    curs.close()
    conn.close()
    return results

def Draw_SignalGraph (serialnumber=None):
    npdata = np.empty (0)
    Table = get_Signal_Alarm_HeartBeat(serialnumber)
    for element in Table : 
        a = np.array([float(element[0]),float(element[1])])
        npdata = np.append (npdata , a )
    len = np.shape (npdata)[0]
    npdata = npdata.reshape (int(len/2),2)
    x, y = npdata.T
    plt.figure(figsize=(10,6))
    plt.scatter(x, y) 
    plt.grid(True)
    plt.xlabel("time") 
    plt.ylabel("Signal level")
    plt.axis([None, None, 0, 99])
    return plt



@app.route("/", methods=['GET', 'POST'])
def index():
    selectedsn = request.args.get('sn')
    SerialNumber = get_UniqueSerialNumber_Alarm_HeartBeat()
    Data = get_Data_Alarm_HeartBeat(selectedsn)
    plt = Draw_SignalGraph(selectedsn) 
    plt.savefig('static/signal.png')
    if selectedsn:
        sn = selectedsn
    else:
        sn = 'all'
    return render_template("index.html", snlist=SerialNumber, data=Data, time = int(time.time()), lastsn=sn)

def main():
    app.run(HOST_NAME, HOST_PORT)

if __name__ == "__main__":
    main()