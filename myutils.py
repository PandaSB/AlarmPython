# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC
import shlex
from subprocess import STDOUT, CalledProcessError, check_output
import socket

class MyUtils:
    """Utilitaires"""
    def get_cputemperature():
        """Return CPU temperature"""
        thermal_zone = 'thermal_zone0'  # Replace with the appropriate thermal zone
        file_path = f'/sys/class/thermal/{thermal_zone}/temp'
        try:
            with open(file_path, 'r') as file:
                temperature = int(file.read()) / 1000
            return temperature
        except:
            return 0

    def get_serialnumber():
        serialnumber = "None"
        try:
            with open ('/proc/cpuinfo') as file:
                for line in file:
                    data = line.split()
                    if len(data) == 3:
                        if data[0].lower() == "serial":
                            serialnumber = data[2]
                file.close()
        except:
            serialnumber = "Error"
        return serialnumber

    def system_call(command):
        """Call a system command"""
        command = shlex.split(command)
        try:
            output = check_output(command, stderr=STDOUT).decode()
            success = True
        except CalledProcessError as e:
            output = e.output.decode()
            success = False
        return output, success

    def  isReachable(hostname, port = 80, timeout=2):
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((hostname, int(port)))
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            return True
        except:
            if s:
                s.close()
            return False
