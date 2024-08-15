#SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
#SPDX-License-Identifier: ISC

import cv2
import requests
import numpy as np
import random


class myipcamera:
    login = ""
    password = ""
    url = ""
    def __init__ (self ,login , password , url  ):
        self.login = login
        self.password = password
        self.url = url

    def capture_photo(self,name = None):

        request = requests.get(self.url, auth=(self.login, self.password)) 
        img = cv2.imdecode(np.array(bytearray(request.content), dtype=np.uint8), -1)

        if name is None:
            name ='/tmp/image'+str (int (random.random()*1000)) + '.png'
        
        print ('name' + name )
        cv2.imwrite(name , img)
        return name