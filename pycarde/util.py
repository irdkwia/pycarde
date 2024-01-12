import os
from pycarde.constants import *

BUFFER_SHORT = []

with open(os.path.join(os.path.dirname(__file__), "data", "short_jp.dat"), 'rb') as file:
    for _ in range(0x100):
        BUFFER_SHORT.append(file.read(2))
        if BUFFER_SHORT[-1][0]<0x80:
            BUFFER_SHORT[-1] = BUFFER_SHORT[-1][:1]

def convertstringlocale(string, region, mode):
    if isinstance(string, bytes) or isinstance(string, bytearray):
        return string
    if region==REGION_US:
        return string.encode("cp1252")
    else:
        string = string.encode("shift-jis")
        if mode==MODE_SHORT:
            ns = bytearray()
            i = 0
            while i<len(string):
                if string[i]<0x80:
                    ns += bytes([BUFFER_SHORT.index(string[i:i+1])])
                    i += 1
                else:
                    ns += bytes([BUFFER_SHORT.index(string[i:i+2])])
                    i += 2
            string = bytes(ns)
        return string

def convertbyteslocale(string, region, mode):
    try:
        if region==REGION_US:
            return string.decode("cp1252")
        else:
            if mode==MODE_SHORT:
                string = b''.join([BUFFER_SHORT[b] for b in string])
            string = string.decode("shift-jis")
            return string
    except UnicodeDecodeError:
        return string

def padding(data, value):
    if len(data)>value:
        data = data[:value]
    else:
        data += bytes(value-len(data))
    return data

def trimpadding(data):
    return data.split(b'\x00')[0]
