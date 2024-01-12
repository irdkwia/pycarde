import os
from pycarde.constants import *
from pycarde.compression.util import *

with open(os.path.join(os.path.dirname(__file__), "data", "textbuffer_us.dat"), 'rb') as file:
    BUFFER_US = file.read()

with open(os.path.join(os.path.dirname(__file__), "data", "textbuffer_jp.dat"), 'rb') as file:
    BUFFER_JP = file.read()

HTREE_US = [[32, [[110, [104, [[127, [[33, [[120, 85], [37, [[14, 13], 55]]]], 71]], [[[65, 49], [67, [[31, 54], [20, [[5, 113], 78]]]]], 44]]]], [[100, 117], 116]]], [[[97, [[107, [119, [[[72, 122], [[[58, 30], [[16, [[26, 15], 81]], [57, 41]]], [75, 22]]], 118]]], 114]], [[[[[39, [[77, [[106, 29], 53]], 73]], [69, [[[51, 28], 82], [[76, [[56, [64, [0, [256, 59]]]], 79]], 70]]]], 1], 115], [105, [102, 2]]]], [[111, 101], [[[[80, [40, [84, 83]]], 109], [103, 108]], [[[[[[50, 87], 48], 98], 46], 99], [121, [[[[[[45, [38, 23]], 89], [52, [[9, 6], [86, 74]]]], 66], [10, 68]], 112]]]]]]]
HTREE_JP = [[[131, [[2, [[224, [67, [96, [221, 7]]]], 65]], [[147, [[71, [76, 190]], [206, 111]]], [[[[135, [176, [[178, 89], [218, 33]]]], 187], [[[35, 182], [8, [159, [[[18, 4], 121], 37]]]], 108]], 91]]]], [[[[197, [164, 234]], [[80, [104, [[235, 184], [[116, 113], 157]]]], 142]], 129], [[[[[[[78, [29, 45]], [70, 20]], 141], 169], [[[[[192, [244, [16, 93]]], 39], [[123, 31], 83]], 175], [[[125, 106], [227, [115, [[122, [[[242, 6], 165], [19, [[11, 3], 26]]]], 9]]]], 95]]], [[117, [[243, [[134, [14, [161, 119]]], [186, 30]]], 85]], [[74, 87], 232]]], [[[205, [[[[214, 152], 73], 146], [[191, [28, 252]], [128, [251, 217]]]]], [[[81, [34, [211, [[219, 167], 64]]]], [136, [69, [[[100, 236], 22], [[17, 49], [[163, 154], 23]]]]]], 145]], [[103, [149, [98, [15, 102]]]], [181, 220]]]]]], [130, [[[[204, [198, [[[226, [[44, [[41, 32], 90]], [21, [216, 210]]]], 88], 194]]], [[[166, [150, [133, 68]]], 170], [196, 200]]], [[[143, [[212, [84, [188, 112]]], [[203, 223], [75, [25, 126]]]]], [233, 118]], [[[[179, [[[215, [245, [246, 12]]], 222], 168]], [199, [86, 202]]], [[94, 79], 241]], [[[82, 230], 173], 66]]]], [[[[[[[[174, 132], [[156, [239, [247, 250]]], 172]], 229], 124], 240], [[231, 177], [151, [[248, 120], [[[180, 207], [[158, 228], 213]], 92]]]]], [[[193, 171], 183], [[[148, 10], 138], [[[[[114, 209], 110], [[[72, [[[36, [[153, [256, 107]], 97]], 195], 13]], 208], 24]], 105], 140]]]], [[[201, [[47, 237], 189]], [162, [[160, 185], [46, [[99, [5, [27, [0, 38]]]], [109, [[225, [238, [155, 43]]], 101]]]]]]], [[[139, 137], [144, [40, 77]]], 1]]]]]]

PLIST_US = dict()
PLIST_JP = dict()

genpathlist(HTREE_US, PLIST_US)
genpathlist(HTREE_JP, PLIST_JP)

def reverse(x, n):
    y = 0
    for i in range(n):
        if x&(1<<i):
            y |= 1<<(n-1-i)
    return y
REVERSE8 = [reverse(i, 8) for i in range(256)]
def decompressLZ19(data):
    dc = bytearray(0)
    off = 0
    while off<len(data):
        ctrl = data[off]
        off += 1
        if ctrl&0xFC==0xFC:
            break
        elif ctrl&0xE0==0xE0:
            size = ((ctrl&0x3)<<8)+data[off]+1
            cmd = (ctrl >> 2)&0x7
            off += 1
        else:
            size = (ctrl&0x1F)+1
            cmd = ctrl >> 5
        if cmd==0x0:
            dc += data[off:off+size]
            off += size
        elif cmd==0x1:
            dc += bytes([data[off]]*size)
            off += 1
        elif cmd==0x2:
            dc += bytes([data[off],data[off+1]]*size)
            off += 2
        elif cmd==0x3:
            dc += bytes([(data[off]+i)&0xFF for i in range(size)])
            off += 1
        elif cmd==0x4:
            adx = (data[off]<<8) + data[off+1]
            dc += dc[adx:adx+size]
            off += 2
        elif cmd==0x5:
            adx = (data[off]<<8) + data[off+1]
            dc += bytes([REVERSE8[x] for x in dc[adx:adx+size]])
            off += 2
        elif cmd==0x6:
            adx = (data[off]<<8) + data[off+1]
            dc += bytes(reversed(dc[adx+1-size:adx+1]))
            off += 2
        else:
            import binascii
            print(binascii.hexlify(dc))
            raise Exception("Unkown command at 0x%X /0x%X/: %02X"%(off,len(dc),ctrl))
    return bytes(dc)

def compressLZ19(data):
    cp = []
    def emptytmp(tmp):
        while len(tmp)>0:
            x = tmp[:1024]
            tmp = tmp[1024:]
            n = len(x)-1
            if n>=32:
                cp.append(0xE0|(n>>8))
                cp.append(n&0xFF)
            else:
                cp.append(n)
            cp.extend(x)
    tmp = []
    i = 0
    while i<len(data):
        j = 0
        pmax = 0
        cmax = 0
        cmdmax = 0
        smax = 0
        n = 1
        while n<1024 and i+n<len(data) and data[i+n]==data[i]:
            n += 1
        s = n-2
        if s>smax:
            cmax = n
            cmdmax = 0x1
            smax = s
        n = 2
        while n<2048 and i+n+1<len(data) and data[i+n]==data[i] and data[i+n+1]==data[i+1]:
            n += 2
        s = n-3
        if s>smax:
            cmax = n
            cmdmax = 0x2
            smax = s
        n = 1
        while n<1024 and i+n<len(data) and data[i+n]==(data[i]+n)&0xFF:
            n += 1
        s = n-2
        if s>smax:
            cmax = n
            cmdmax = 0x3
            smax = s
        while j<i:
            n = 0
            while n<1024 and j+n<i and i+n<len(data) and data[i+n]==data[j+n]:
                n += 1
            if n>0:
                s = n-3
                if s>smax:
                    pmax = j
                    cmax = n
                    cmdmax = 0x4
                    smax = s
            n = 0
            while n<1024 and j+n<i and i+n<len(data) and data[i+n]==REVERSE8[data[j+n]]:
                n += 1
            if n>0:
                s = n-3
                if s>smax:
                    pmax = j
                    cmax = n
                    cmdmax = 0x5
                    smax = s
            n = 0
            while n<1024 and j+n<i and i+n<len(data) and data[i+n]==data[i-j-1-n]:
                n += 1
            if n>0:
                s = n-3
                if s>smax:
                    pmax = i-j-1
                    cmax = n
                    cmdmax = 0x6
                    smax = s
            j += 1
        if smax>0:
            emptytmp(tmp)
            tmp = []
            cmax -= 1
            if cmdmax==2:
                cmax -= 1
                cmax >>=1
            if cmax>=32:
                cp.append(0xE0|(cmdmax<<2)|(cmax>>8))
                cp.append(cmax&0xFF)
            else:
                cp.append((cmdmax<<5)|cmax)
            if cmdmax==2:
                cmax <<=1
            if cmdmax in [0x1, 0x3]:
                cp.append(data[i])
            elif cmdmax==0x2:
                cp.append(data[i])
                cp.append(data[i+1])
            elif cmdmax in [0x4, 0x5, 0x6]:
                cp.append(pmax>>8)
                cp.append(pmax&0xFF)
            else:
                raise Exception("WTF")
            i += cmax + 1
            if cmdmax==2:
                i += 1
        else:
            tmp.append(data[i])
            i += 1
    emptytmp(tmp)
    cp.append(0xFF)
    return bytes(cp)

def decompressBufferedHuffman(data, htree, buffer):
    data = BitBuffer(data)
    dc = []
    maxlen = data.read(16)
    while len(dc)<maxlen:
        a = data.read(1)
        if a:
            cmdn = data.read(12)
            cmds = data.read(4)
            #print("POS",len(dc),hex(cmdn),cmds+1)
            for i in range((cmds+1)):
                if cmdn+i<len(buffer):
                    dc.append(buffer[cmdn+i])
                else:
                    dc.append(0)
        else:
            cmdn = searchtree(data, htree)
            if cmdn==0x100:
                cmdn = data.read(8)
                dc.append(cmdn)
            else:
                dc.append(cmdn)
            if cmdn&0x80:
                cmdn = searchtree(data, htree)
                if cmdn==0x100:
                    cmdn = data.read(8)
                    dc.append(cmdn)
                else:
                    dc.append(cmdn)
    return bytes(dc)

def compressBufferedHuffman(data, plist, buffer):
    cp = BitBuffer()
    cp.write(16, len(data))
    b = -1
    i = 0
    while i<len(data):
        j = 0
        jmax = 0
        cmax = 0
        smax = 0
        while j<len(buffer):
            n = 0
            while n<16 and i+n<len(data) and j+n<len(buffer) and data[i+n]==buffer[j+n]:
                n += 1
            if n>0:
                s = 0
                for c in buffer[j:j+n]:
                    if c in plist:
                        s += len(plist[c])+1
                    else:
                        s += len(plist[0x100])+1+8-(c>>7)
                if s>smax:
                    jmax = j
                    cmax = n
                    smax = s
            j += 1
        if smax<=17:
            cp.write(1, 0)
            forcesgc = 2
            while forcesgc:
                if forcesgc==1:
                    forcesgc = 0
                if data[i] in plist:
                    for a in plist[data[i]]:
                        cp.write(1, a)
                else:
                    for a in plist[0x100]:
                        cp.write(1, a)
                    cp.write(8, data[i])
                if i+1<len(data) and data[i]&0x80 and forcesgc:
                    forcesgc = 1
                else:
                    forcesgc = 0
                i += 1
        else:
            cp.write(1, 1)
            cp.write(12, jmax)
            cp.write(4, cmax-1)
            i += cmax
    return cp.getdata()

def decompressBufferedHuffmanRegion(data, region):
    if region==REGION_US:
        return decompressBufferedHuffman(data, HTREE_US, BUFFER_US)
    else:
        return decompressBufferedHuffman(data, HTREE_JP, BUFFER_JP)

def compressBufferedHuffmanRegion(data, region):
    if region==REGION_US:
        return compressBufferedHuffman(data, PLIST_US, BUFFER_US)
    else:
        return compressBufferedHuffman(data, PLIST_JP, BUFFER_JP)
    
