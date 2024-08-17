# SPDX-FileCopyrightText: 2024 BARTHELEMY Stephane  stephane@sbarthelemy.com
# SPDX-License-Identifier: ISC

class MyUtils:
    """Utilitaires"""
    def get_cputemperature():
        """Return CPU temperature"""
        thermal_zone = 'thermal_zone0'  # Replace with the appropriate thermal zone
        file_path = f'/sys/class/thermal/{thermal_zone}/temp'
        with open(file_path, 'r') as file:
            temperature = int(file.read()) / 1000
        return temperature
