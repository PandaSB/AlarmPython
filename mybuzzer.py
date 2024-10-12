# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import time 
import gpiod
from threading import Thread


class MyBuzzer:
    number = 0 
    buzzer_on = False
    pulse = 0.0
    delay = 0.0

    def __init__(self, buzzerpin):
        chip = gpiod.Chip("gpiochip0")
        buzzerline = gpiod.find_line(buzzerpin)
        self.buzzerlines = chip.get_lines([buzzerline.offset()])
        self.buzzerlines.request(
            consumer="alarm", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0]
        )
        self.buzzerlines.set_values([0])

        try:
            thread = Thread(target=self.run_thread)
            thread.start()
        except KeyboardInterrupt:
            pass

    def run_thread(self):
        while True:
            if self.buzzer_on:
                for x in range(self.number):
                    self.buzzerlines.set_values([1])
                    time.sleep(self.pulse)
                    self.buzzerlines.set_values([0])
                    time.sleep(self.delay)
                    if self.buzzer_on == False:
                        break ; 
                self.buzzer_on = False


    def clearbuzzer(self):
        self.buzzer_on = False


    def setbuzzer (self, number , pulse , delay ):
        self.number = number 
        self.pulse = pulse
        self.delay = delay
        self.buzzer_on = True
