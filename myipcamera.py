# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import random

import cv2
import numpy as np
import requests


class MyIpCamera:
    """Access to camera on network devices"""

    login = None
    password = None
    url = ""

    def __init__(self, login, password, url):
        """ create object with login credentials"""
        self.login = login
        self.password = password
        self.url = url

    def capture_photo(self, name=None):
        """Capture phot from camera connected on network"""

        try:
            request = requests.get(self.url, auth=(self.login, self.password), timeout=10)
            img = cv2.imdecode(np.array(bytearray(request.content), dtype=np.uint8), -1)

            if name is None:
                name = "/tmp/image" + str(int(random.random() * 1000)) + ".png"

            print("name" + name)
            cv2.imwrite(name, img)
        except: 
            return None
        return name
