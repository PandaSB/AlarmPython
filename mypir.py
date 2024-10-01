# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import gpiod
from threading import Thread
import time


class MyPir:
    pirlines = None 
    callback = None 
    old_status = 0 
    def __init__ ( self , gpio , callback ):
        self.callback = callback
        chip = gpiod.Chip("gpiochip0")
        pirline = gpiod.find_line(gpio)
        self.pirlines = chip.get_lines([pirline.offset()])
        self.pirlines.request(
            consumer="alarm",
            type=gpiod.LINE_REQ_DIR_IN,
            flags=gpiod.LINE_REQ_FLAG_BIAS_DISABLE
        )
        self.old_status = self.pirlines.get_values()[0]
        try:
            thread = Thread(target=self.run_thread)
            thread.start()
        except KeyboardInterrupt:
            pass

    def run_thread(self):
        while True:
            value = self.pirlines.get_values()[0]
            if value != self.old_status:
                self.old_status = value 
                if self.callback:
                    self.callback(value)
            time.sleep(1)
        