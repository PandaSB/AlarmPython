# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

from threading import Thread
from http.server import HTTPServer


class MyWebServer:
    """Create a webserver"""
    hostName = "localhost"
    serverPort = 8080
    webServer = None

    def server_pulling(self):
        """Start pulling of webserver"""
        self.webServer.serve_forever()
                
    def __init__(self, hostName , serverPort, serverClass) -> None:
        """Init http server """
        self.webServer = HTTPServer((hostName, int(serverPort)), serverClass)
        print("Server started http://%s:%s" % (hostName, serverPort))

        try:
            thread = Thread(target=self.server_pulling)
            thread.start()
            
        except KeyboardInterrupt:
            pass