// SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
// SPDX-License-Identifier: GPL V3

// base on 02_output-received-code.ino from RF433any
// https://github.com/sebmillet/RF433any


/

#include "RF433any.h"
#include <Arduino.h>
#include <HardwareSerial.h>

HardwareSerial MySerial(2);
const int MySerialRX = 16;
const int MySerialTX = 17;

#define PIN_RFINPUT  2

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

void setup() {

    MySerial.begin(9600, SERIAL_8N1, MySerialRX, MySerialTX);
    

    pinMode(PIN_RFINPUT, INPUT);
    Serial.begin(9600);
    Serial.print("Waiting for signal\n");
}

Track track(PIN_RFINPUT);

void loop() {
    track.treset();

    while (!track.do_events())
        delay(1);

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
