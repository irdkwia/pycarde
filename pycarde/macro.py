import os

from zipfile import ZipFile
from pycarde.serializer import *
from pycarde.constants import *
from pycarde.image import *
from pycarde.util import *
from pycarde.card import *
from pycarde.raw import *
from pycarde.save import *
from pycarde.compression.vpk import decompressVpk, compressVpk

DMCA = b'\x00\x00DMCA NINTENDO E-READER'

def createnesapp(src, dst, region, appname, transform=lambda x: x, save=False):
    with open(src, 'rb') as file:
        data = bytearray(file.read())
    if data[:3]==b'NES':
        data = data[0x10:]

    nmi = int.from_bytes(data[0x3FFA:0x3FFC], 'little')
    for i in reversed(range(0x18)):
        for j in range(8):
            c = nmi & 1
            nmi >>= 1
            if c:
                nmi ^= 0x8646
        nmi ^= DMCA[i]<<8
    data[0x3FFA:0x3FFC] = nmi.to_bytes(2, 'little')
    data = compressVpk(data)
    card = RawAppCard(region, LONG_CODE)
    card._appname = appname
    card.nes = True
    card.save = save
    card.data = len(data).to_bytes(2, 'little')+data
    for i, e in enumerate(Card.makecards([card], extend=True)):
        with open(os.path.join(dst, "card%02d.bin"%(i+1)), 'wb') as file:
            file.write(transform(e))

def getnesapp(src, dst, transform=lambda x: x, ines=True):
    cards = []
    for e in src:
        with open(e, 'rb') as file:
            cards.append(transform(file.read()))
    cards = Card.parsecards(cards)
    data = Card.mergecardsdata(cards)[0].data[2:]
    data = bytearray(decompressVpk(data))
    nmi = int.from_bytes(data[0x3FFA:0x3FFC], 'little')
    for i in range(0x18):
        nmi ^= DMCA[i]<<8
        for j in range(8):
            nmi <<= 1
            if nmi & 0x10000:
                nmi ^= 0x10C8D
    data[0x3FFA:0x3FFC] = nmi.to_bytes(2, 'little')
    if ines:
        data = b'NES\x1A\x01\x01'+bytes(10)+data
    with open(dst, 'wb') as file:
        file.write(data)


def createappvpkfromdata(src, dst, lenhead=True, gba=False):
    with open(dst, 'wb') as outfile:
        with open(src, 'rb') as infile:
            c = compressVpk(infile.read())
            if gba:
                c = bytes(4)+c
            if lenhead:
                c = len(c).to_bytes(2, 'little')+c
            outfile.write(c)

def getdatafromappvpk(src, dst, lenhead=True):
    with open(dst, 'wb') as outfile:
        with open(src, 'rb') as infile:
            d = infile.read()
            if lenhead:
                d = d[2:]
            if d[:4]==b'\x00\x00\x00\x00':
                d = d[4:]
            outfile.write(decompressVpk(d))

def getcardsinfo(clist, transform=lambda x: x, merge=False):
    srclist = []
    for t in clist:
        with open(t[0], 'rb') as file:
            srclist.append(transform(file.read()))
    dstlist = Card.parsecards(srclist)
    if merge:
        dstlist = Card.mergecardsdata(dstlist)
    
    for i, t in enumerate(clist):
        if t[1].endswith(".zip"):
            file = ZipFile(t[1], 'w')
        else:
            file = Directory(t[1], 'w')
        with file as zf:
            CardSerializer.serialize(dstlist[i], zf)

def createcardsinfo(clist, transform=lambda x: x):
    srclist = []
    for t in clist:
        if t[0].endswith(".zip"):
            file = ZipFile(t[0])
        else:
            file = Directory(t[0])
        with file as zf:
            srclist.append(CardSerializer.deserialize(zf))
    dstlist = Card.makecards(srclist)
    
    for i, t in enumerate(clist):
        with open(t[1], 'wb') as file:
            file.write(transform(dstlist[i]))

def createcardssave(clist, sav, base=None):
    srclist = []
    for t in clist:
        if t.endswith(".zip"):
            file = ZipFile(t)
        else:
            file = Directory(t)
        with file as zf:
            srclist.append(CardSerializer.deserialize(zf))
    if base:
        with open(base, 'rb') as file:
            basesave = file.read()
    else:
        basesave = BASESAVE_US
    with open(sav, 'wb') as file:
        file.write(createsaveforcardlist(srclist, basesave))

def createcardssaveraw(clist, sav, base=None, transform=lambda x: x):
    srclist = []
    for t in clist:
        with open(t, 'rb') as file:
            srclist.append(transform(file.read()))
    dstlist = Card.parsecards(srclist)
    
    if base:
        with open(base, 'rb') as file:
            basesave = file.read()
    else:
        basesave = BASESAVE_US
    
    with open(sav, 'wb') as file:
        file.write(createsaveforcardlist(dstlist, basesave))
