
"""
Author : Anonymous
Date : 15/01/2021
"""

import time

def generateFile(name):
    currTime = time.strftime("%Y%m%d_%H%M%S")
    filename = name + "\\" + currTime 
    # print(filename)
    return filename