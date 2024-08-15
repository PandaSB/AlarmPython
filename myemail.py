# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

import datetime
import smtplib

# from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MyEmail:
    """Access to smtp email"""

    email = None
    password = None
    port = None
    server = None

    def __init__(self, email, password, server, port):
        print("Config Email : " + email + "/" + password + "@" + server + ":" + port)
        self.email = email
        self.password = password
        self.port = port
        self.server = server

    def sendmail(self, receiver, subject, body, photo=None, photo2=None):
        """Send sms"""
        print(photo)
        print(photo2)

        now = datetime.datetime.now()
        timedate = now.strftime("%d/%m/%Y %H:%M:%S")
        body += "\r\n" + timedate + "\r\n"

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.email
        msg["To"] = ", ".join(receiver)

        html = "<p>" + body + "</p><br>"
        if photo is not None:
            img = open(photo, "rb").read()
            msgImg = MIMEImage(img, "png")
            msgImg.add_header("Content-ID", "<image1>")
            msgImg.add_header("Content-Disposition", "inline", filename=photo)
            html.join('<p><img src="cid:image1"></p>')

        if photo2 is not None:
            img2 = open(photo2, "rb").read()
            msgImg2 = MIMEImage(img2, "png")
            msgImg2.add_header("Content-ID", "<image2>")
            msgImg2.add_header("Content-Disposition", "inline", filename=photo2)
            html.join('<p><img src="cid:image2"></p>')

        msgHtml = MIMEText(html, "html")
        msg.attach(msgHtml)
        if photo is not None:
            msg.attach(msgImg)
        if photo2 is not None:
            msg.attach(msgImg2)

        server = smtplib.SMTP_SSL(self.server, self.port)
        server.login(self.email, self.password)
        server.sendmail(self.email, receiver, msg.as_string())
        server.quit()
