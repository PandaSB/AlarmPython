#SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
#SPDX-License-Identifier: ISC

import smtplib
import ssl
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication


class myemail:
        email = ''
        password = ''
        port = ''
        server = ''

        def __init__ (self , email, password , server, port):
            print ("Config Email : " + email + '/' + password + '@' + server + ':' + port )
            self.email = email
            self.password = password
            self.port = port
            self.server = server


        def sendmail (self, receiver, subject, body, photo = None, photo2 = None):

            print ( photo)
            print ( photo2)

            now = datetime.datetime.now()
            timedate = now.strftime("%d/%m/%Y %H:%M:%S")
            body += '\r\n' + timedate + '\r\n'

            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.email
            msg['To'] = ', '.join(receiver)


            html = '<p>' + body + '</p><br>'
            print ("html init : " + html)
            if not (photo is None):
                img = open(photo, 'rb').read()
                msgImg = MIMEImage(img, 'png')
                msgImg.add_header('Content-ID', '<image1>')
                msgImg.add_header('Content-Disposition', 'inline', filename=photo)
                html.join ('<p><img src="cid:image1"></p>')
                print ("html photo : " + html)
                

            if not (photo2 is None):
                img2 = open(photo2, 'rb').read()
                msgImg2 = MIMEImage(img2, 'png')
                msgImg2.add_header('Content-ID', '<image2>')
                msgImg2.add_header('Content-Disposition', 'inline', filename=photo2)
                html.join ('<p><img src="cid:image2"></p>')
                print ("html photo2 : " + html)


            print ("html end  : " + html)

            msgHtml = MIMEText(html, 'html')

            msg.attach(msgHtml)
            if not (photo is None): msg.attach(msgImg)
            if not (photo2 is None): msg.attach(msgImg2)



            
            context=ssl.create_default_context()
            server=smtplib.SMTP_SSL(self.server ,self.port) 
            server.login(self.email,self.password)
            server.sendmail(self.email,receiver,msg.as_string()) 
            server.quit()


                
