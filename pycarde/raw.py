from pycarde.image import *
from pycarde.constants import *

def rawtoimg(raw):
    pass

def bintoraw(data):
    temp = bytearray(len(data)*4//3)
    interleave = len(temp)//0x40
    for i in range(0, len(data), 0x30):
        cdata = bytearray(0x10)+bytes(reversed(data[i:i+0x30]))
        for j in reversed(range(0x10, 0x40)):
            z = ALPHATO.index(cdata[j] ^ cdata[0xF])
            for k in reversed(range(0x10)):
                if k==0:
                    x = 0
                else:
                    x = cdata[k-1]
                if z!=0xFF:
                    y = GG[k]
                    if y!=0xFF:
                        y += z
                        if y>=0xFF:
                            y -= 0xFF
                        x ^= ALPHATO[y]
                cdata[k] = x
        for j in range(0x10):
            cdata[j] ^= 0xFF
        for j, b in enumerate(reversed(cdata)):
            temp[(j*interleave)+(i//0x30)] = b
    j = 0xB38 if len(temp)==0xB00 else 0x724
    k = 0xB60 if len(temp)==0xB00 else 0x750
    raw = bytearray(k)

    i = 0
    while i<j:
        for e in range(2):
            code = ((i//0x68*2)+e)%0x18
            raw[i+e] = LONGHEADER[code] if len(temp)==0xB00 else SHORTHEADER[code]
        i += 0x68
    idc = 0
    i = 2
    while i<j:
        if (i%0x68)==0:
            i+=2
        raw[i] = temp[idc]
        idc += 1
        i += 1
    for i in range(j, k):
        raw[i] = i&0xFF
    return raw

## TODO: does not correct errors!!!
def rawtobin(raw):
    temp = bytearray(0xB00 if len(raw)==0xB60 else 0x700)
    j = 0xB38 if len(temp)==0xB00 else 0x724
    idc = 0
    i = 2
    while i<j:
        if (i%0x68)==0:
            i+=2
        temp[idc] = raw[i]
        idc += 1
        i += 1
    data = bytearray(HEAD_LEN+(LONG_CODE if len(temp)==0xB00 else SHORT_CODE))
    
    interleave = len(temp)//0x40
    for i in range(0, len(data), 0x30):
        for j in range(0x30):
            data[i+j] = temp[(j*interleave)+(i//0x30)]
    return data
