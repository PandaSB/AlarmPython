# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

# #sudo apt-get install  python3-luma.oled

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, sh1106

from PIL import ImageFont , Image, ImageDraw

DISPLAY_TYPE_SSD1306 = "SSD1306"
DISPLAY_TYPE_SH1107 = "SH1107"

DISPLAY_ADDR = 0x3C
BACKGROUND_COLOR = "black" 

class MyDisplay:

    def __init__(self, type=DISPLAY_TYPE_SSD1306 , address = DISPLAY_ADDR, rotate = '0', width = '128' , height = '64'):
        self.width = int(width)
        self.height = int(height)
        if (type == DISPLAY_TYPE_SSD1306):
            serial = i2c(port=1, address=address)
            self.device = ssd1306(serial,rotate=int(rotate),width=int(width), height=int(height))
        elif (type == DISPLAY_TYPE_SH1107):
            serial = i2c(port=1, address=address)
            self.device = sh1106(serial,rotate=int(rotate),width=int(width), height=int(height))
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf",12)
        #self.whole = Image.new("RGBA",  (self.width,self.height), (0,0,0))
        self.whole = Image.new(self.device.mode,  self.device.size, BACKGROUND_COLOR)
        self.draw = ImageDraw.Draw(self.whole)
        self.device.display (self.whole)
        


    def get_height (self):
        return self.height

    def get_width(self):
        return self.height


    def addimage(self , x,y,w,h,image_path):
        im1 = Image.open(image_path)
        im1 = im1.resize((w,h))
        self.whole.paste (im1, (x, y))
        self.device.display (self.whole)


    def clear(self):
        self.whole = Image.new(self.device.mode,  self.device.size, BACKGROUND_COLOR)
        self.draw = ImageDraw.Draw(self.whole)
        self.device.display (self.whole)

    def drawtext (self , x, y, text , fill="white"):
        self.draw.text((x, y), text, fill=fill, font=self.font)
        self.device.display (self.whole)

    def drawcentertext (self , x, y, text , fill="white"):
        wtext,htext = self.draw.textsize (text, font=self.font)
        self.draw.text((x - (wtext/2), y - (htext/2)), text, fill=fill, font=self.font)
        self.device.display (self.whole)


