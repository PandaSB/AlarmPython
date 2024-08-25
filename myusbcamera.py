# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

# sudo apt-get install python3-opencv

import random

import cv2
import numpy as np


class MyUsbCamera:
    """access to camera liked  on "/dev/video*" device"""

    width = 640
    height = 480
    fps = 30

    camera_id = "/dev/video0"
    video_capture = None

    def __init__(self, camera_port):
        """Init video camera for V4l2 device"""
        self.camera_id = camera_port
        self.video_capture = cv2.VideoCapture(self.camera_id, cv2.CAP_V4L2)

        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.video_capture.set(cv2.CAP_PROP_FPS, self.fps)

    def capture_photo(self, name=None):
        """Function capture video from /dev/video* device"""
        frame = np.zeros((self.height, self.width, 3), np.uint8)
        if self.video_capture.isOpened():
            ret_val, frame = self.video_capture.read()
        if name is None:
            name = "/tmp/image" + str(int(random.random() * 1000)) + ".png"
        print("name" + name)
        cv2.imwrite(name, frame)
        return name
