# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import sched
import time 
import gpiod
from threading import Thread



class MySiren:
    mode = 'auto'
    schedule = None
    timeout = 0 
    sirenlines = None 
    state = None
    current_timeout = 0 ; 

    def __init__ (self, defaultMode ,gpio , timeout ):
        self.mode = defaultMode
        self.timeout = timeout 
        print ("Init MYSiren")
        chip = gpiod.Chip("gpiochip0")
        sirenline = gpiod.find_line(gpio)
        self.sirenlines = chip.get_lines([sirenline.offset()])
        self.sirenlines.request(
            consumer="alarm", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0]
        )
        if (self.mode == 'on'):
            self.sirenlines.set_values([1])
            self.state = "on"
        else:  # off / auto 
            self.sirenlines.set_values([0])
            self.state = "off"

        self.schedule = sched.scheduler(time.time, time.sleep)

    def on(self, timeout = None) : 
        if self.mode == "on" or self.mode == "auto":
            self.sirenlines.set_values([1])
            self.state = "on"
        elif self.mode == "off":
            self.sirenlines.set_values([0])
            self.state = "off"

        if (self.mode == "auto" and self.timeout != 0):
            if timeout == None:
                timeout = self.timeout 
            self.current_timeout = timeout 
            try:
                thread = Thread(target=self.run_thread)
                thread.start()
            except KeyboardInterrupt:
                pass

    def run_thread(self):
        time.sleep (int(self.current_timeout))
        self.off()

    def setmode (self , mode):
        self.mode = mode 
    
    def settimeout (self, timeout):
        self.timeout = timeout

    def ison(self):
        return self.state


    def off (self):
        self.sirenlines.set_values([0])
        self.state = 'off'