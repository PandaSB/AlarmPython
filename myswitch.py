# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import gpiod
from threading import Thread
import time


class MySwitch:
    switchlines = None 
    callback = None 
    old_status = 0 
    def __init__ ( self , gpio , callback ):
        self.callback = callback
        chip = gpiod.Chip("gpiochip0")
        switchline = gpiod.find_line(gpio)
        self.switchlines = chip.get_lines([switchline.offset()])
        self.switchlines.request(
            consumer="alarm",
            type=gpiod.LINE_REQ_DIR_IN,
            flags=gpiod.LINE_REQ_FLAG_BIAS_DISABLE
        )
        self.old_status = self.switchlines.get_values()[0]
        try:
            thread = Thread(target=self.run_thread)
            thread.start()
        except KeyboardInterrupt:
            pass

    def run_thread(self):
        while True:
            value = self.switchlines.get_values()[0]
            if value != self.old_status:
                self.old_status = value 
                if self.callback:
                    self.callback(value)
            time.sleep(1)
        