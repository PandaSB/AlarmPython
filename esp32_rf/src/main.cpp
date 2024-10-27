// SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
// SPDX-License-Identifier: GPL V3

// base on 02_output-received-code.ino from RF433any
// https://github.com/sebmillet/RF433any



#include <Wire.h>
#include <SPI.h>
#include "RF433any.h"
#include <Arduino.h>
#include <HardwareSerial.h>
#include "Adafruit_INA219.h"


const int MySerialRX = 16;
const int MySerialTX = 17;
const int I2C_SDA = 21;
const int I2C_SCL = 22;
const int PIN_RFINPUT = 2;

const int INA219_ADDR = 0x41;

HardwareSerial MySerial(2);
Adafruit_INA219 ina219(0x41);

uint64_t starttime = 0;



char* my_BitVector_to_str(const BitVector *bv) {
    if (!bv->get_nb_bits())
        return nullptr;

    byte nb_bytes = bv->get_nb_bytes();

    char *ret = (char*)malloc((nb_bytes * 2) + 1) ;
    memset (ret, '\0' , (nb_bytes * 2) + 1);
    char tmp[3];
    int j = 0;
    for (int i = nb_bytes - 1; i >= 0 ; --i) {
        snprintf(tmp, sizeof(tmp), "%02X", bv->get_nth_byte(i));
        ret[j] = tmp[0];
        ret[j + 1] = tmp[1];
        //ret[j + 2] = (i > 0 ? ' ' : '\0');
        j += 2;
    }

    return ret;
}



void I2cScan()
{


    byte error, address;
    int nDevices;
    Serial.println("Scanning...");
    nDevices = 0;
    for(address = 1; address < 127; address++ ) {
        Wire.beginTransmission(address);
        error = Wire.endTransmission();
        if (error == 0) {
            Serial.print("I2C device found at address 0x");
            if (address<16) {
                Serial.print("0");
            }
            Serial.println(address,HEX);
            nDevices++;
        }
        else if (error==4) {
            Serial.print("Unknow error at address 0x");
            if (address<16) {
                Serial.print("0");
            }
            Serial.println(address,HEX);
        }
    }
    if (nDevices == 0) {
        Serial.println("No I2C devices found\n");
    }
    else {
        Serial.println("done\n");
    }

}

void setup() {

    MySerial.begin(9600, SERIAL_8N1, MySerialRX, MySerialTX);
    pinMode(PIN_RFINPUT, INPUT);
    Serial.begin(9600);
    Wire.begin();
    if (! ina219.begin()) {
        Serial.println("Failed to find INA219 chip");
    }
    starttime = millis();
}

Track track(PIN_RFINPUT);



void loop() {
    float shuntvoltage = 0;
    float busvoltage = 0;
    float current_mA = 0;
    float loadvoltage = 0;
    float power_mW = 0;
    uint64_t currenttime;

    track.treset();


    while (!track.do_events())
    {
        delay(1);
        currenttime = millis();
        if ( currenttime > (starttime + 5000))
        {
            shuntvoltage = ina219.getShuntVoltage_mV();
            busvoltage = ina219.getBusVoltage_V();
            current_mA = ina219.getCurrent_mA();
            power_mW = ina219.getPower_mW();
            loadvoltage = busvoltage + (shuntvoltage / 1000);

            Serial.print("alim ");
            Serial.print(busvoltage);
            Serial.println(" V");
            MySerial.print("alim ");
            MySerial.print(busvoltage);
            MySerial.println(" V");

            Serial.print("bat ");
            Serial.print(loadvoltage);
            Serial.println(" V");
            MySerial.print("bat ");
            MySerial.print(loadvoltage);
            MySerial.println(" V");

            Serial.print("cur ");
            Serial.print(current_mA);
            Serial.println(" mA");
            MySerial.print("cur ");
            MySerial.print(current_mA);
            MySerial.println(" mA");

            starttime = currenttime;

        }



    }
        Decoder *pdec0 = track.get_data(
            RF433ANY_FD_DECODED | RF433ANY_FD_DEDUP | RF433ANY_FD_NO_ERROR
        );
    for (Decoder *pdec = pdec0; pdec != nullptr; pdec = pdec->get_next()) {
        byte nb_bytes = (pdec->get_nb_bits() + 7) >> 3;
        
        char *buf = my_BitVector_to_str(pdec->get_pdata());
        if (buf) {
            Serial.print("hfrecu ");
            Serial.println(buf);
            MySerial.print("hfrecu ");
            MySerial.println(buf);
            free(buf);
        }
    }
    delete pdec0;
}
