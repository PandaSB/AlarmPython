# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import gpiod


class MyLoop:
    """Dection of sensors on loop"""
    enablelines = None
    pinout1lines = None
    pinout2lines = None
    pinout3lines = None
    pinout4lines = None
    inversed1 = 0
    inversed2 = 0
    inversed3 = 0
    inversed4 = 0

    def __init__(self,  in_enable, in_pinout1, in_inverse1, in_pinout2, in_inverse2, in_pinout3, in_inverse3, in_pinout4, in_inverse4):
        """Init of loop pinout """
        print("Init loop")
        print("loop Enable       : " + in_enable)
        print("loop in 1 pinout  : " + in_pinout1)
        print("loop in 1 inverse : " + in_inverse1)
        print("loop in 2 pinout  : " + in_pinout2)
        print("loop in 2 inverse : " + in_inverse2)
        print("loop in 3 pinout  : " + in_pinout3)
        print("loop in 3 inverse : " + in_inverse3)        
        print("loop in 4 pinout  : " + in_pinout4)
        print("loop in 4 inverse : " + in_inverse4)
        chip = gpiod.Chip("gpiochip0")

        self.inversed1 = in_inverse1
        self.inversed2 = in_inverse2
        self.inversed3 = in_inverse3
        self.inversed4 = in_inverse4

        enableline = gpiod.find_line(in_enable)
        self.enablelines = chip.get_lines([enableline.offset()])
        self.enablelines.request(
            consumer="alarm", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0]
        )
        self.enablelines.set_values([1])


        if in_pinout1 != '-1' : 
            pinout1line = gpiod.find_line(in_pinout1)
            self.pinout1lines = chip.get_lines([pinout1line.offset()])
            self.pinout1lines.request(
                consumer="alarm",
                type=gpiod.LINE_REQ_DIR_IN,
                flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
            )
        if in_pinout2 != '-1' : 
            pinout2line = gpiod.find_line(in_pinout2)
            self.pinout2lines = chip.get_lines([pinout2line.offset()])
            self.pinout2lines.request(
                consumer="alarm",
                type=gpiod.LINE_REQ_DIR_IN,
                flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
            )
        if in_pinout3 != '-1' : 
            pinout3line = gpiod.find_line(in_pinout3)
            self.pinout3lines = chip.get_lines([pinout3line.offset()])
            self.pinout3lines.request(
                consumer="alarm",
                type=gpiod.LINE_REQ_DIR_IN,
                flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
            )
        if in_pinout4 != '-1' : 
            pinout4line = gpiod.find_line(in_pinout4)
            self.pinout4lines = chip.get_lines([pinout4line.offset()])
            self.pinout4lines.request(
                consumer="alarm",
                type=gpiod.LINE_REQ_DIR_IN,
                flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
            )

    def enablesetvalue(self, value):
        """Change Enable pinout value"""
        self.enablelines.set_values([value])

    def pinoutgetvalue(self,num ):
        """Read value of loop"""
        value = False
        if (num == 1)  and self.pinout1lines:
            value = self.pinout1lines.get_values()[0] != 0
            if self.inversed1:
                value = not value
        if (num == 2)  and self.pinout1lines:
            value = self.pinout2lines.get_values()[0] != 0
            if self.inversed2:
                value = not value
        if (num == 3)  and self.pinout3lines:
            value = self.pinout3lines.get_values()[0] != 0
            if self.inversed3:
                value = not value
        if (num == 4)  and self.pinout4lines:
            value = self.pinout4lines.get_values()[0] != 0
            if self.inversed3:
                value = not value


        return value
