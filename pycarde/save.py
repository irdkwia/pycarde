import os
from pycarde.util import *
from pycarde.card import *

def gensource(factor):
    source = []
    for i in range(256):
        tmp = i
        for j in range(8):
            if tmp&1:
                tmp >>= 1
                tmp ^= factor
            else:
                tmp >>= 1
        source.append(tmp)
    return source

with open(os.path.join(os.path.dirname(__file__), "data", "save.dat"), 'rb') as file:
    SAVEHEAD = file.read()

BASESAVE_US = bytearray([0xFF]*0x20000)
BASESAVE_US[0xD000:0xD050] = SAVEHEAD
BASESAVE_US[0xD050:0xE000] = bytes(0xFB0)
BASESAVE_US[0xD052] = 1
BASESAVE_US[0xE000:0xF000] = BASESAVE_US[0xD000:0xE000]

SAVESUM_SOURCE_US = gensource(0xEDB88320)
INITSUM_US = 0xAA478422

def checksum(buffer, source, finalsum):
    for c in buffer:
        tmp = finalsum>>8
        c = (finalsum^c)&0xFF
        finalsum = source[c]^tmp
    return finalsum

def createsaveforapp(data, region, appname, base=BASESAVE_US, flags=0):
    savedata = bytearray(base)
    fulldata = bytearray()
    fulldata += padding(convertstringlocale(appname, region, MODE_LONG), 0x1F)+bytes(1)
    fulldata += bytes(4)
    fulldata += flags.to_bytes(4, 'little')+len(data).to_bytes(4, 'little')
    fulldata += bytes(4)+data
    savedata[0x10000:0x10004] = checksum(fulldata, SAVESUM_SOURCE_US, INITSUM_US).to_bytes(4, 'little')
    savedata[0x10004:0x10004+len(fulldata)] = fulldata
    return savedata

def createsaveforcardlist(clist, base=BASESAVE_US):
    clist = Card.mergecardsdata(clist)
    return createsaveforapp(clist[0].data, clist[0].region, clist[0].appname, base, (clist[0].save<<2)|(clist[0].nes<<3))
    
