# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import gpiod


class MyLoop:
    """Dection of sensors on loop"""
    enablelines = None
    pinoutlines = None
    inversed = 0

    def __init__(self, in_pinout, in_enable, in_inverse):
        """Init of loop pinout """
        print("Init loop")
        chip = gpiod.Chip("gpiochip0")

        self.inversed = in_inverse

        enableline = gpiod.find_line(in_enable)
        self.enablelines = chip.get_lines([enableline.offset()])
        self.enablelines.request(
            consumer="alarm", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0]
        )
        self.enablelines.set_values([1])

        pinoutline = gpiod.find_line(in_pinout)
        self.pinoutlines = chip.get_lines([pinoutline.offset()])
        self.pinoutlines.request(
            consumer="alarm",
            type=gpiod.LINE_REQ_DIR_IN,
            flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
        )

        print(
            "config loop : pinout : "
            + in_pinout
            + ", pinout enable : "
            + in_enable
            + ", inverse mode : "
            + str(in_inverse)
        )

    def enablesetvalue(self, value):
        """Change Enable pinout value"""
        self.enablelines.set_values([value])

    def pinoutgetvalue(self):
        """Read value of loop"""
        value = self.pinoutlines.get_values()[0] != 0
        if self.inversed:
            value = not value
        return value
