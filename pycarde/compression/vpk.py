from pycarde.compression.util import *
COMMAND_OUTPUT_ONE = 0
COMMAND_OUTPUT_MULTI = 1
MAX_MOVE = 16
MAX_SIZE = 16
def decompressVpk(data):
    buffer = BitBuffer(data)
    if buffer.read(32)!=0x76706b30:
        raise Exception("Not a valid vpk0!")
    size = buffer.read(32)
    method = buffer.read(8)
    movetree = readhuffman(buffer)
    sizetree = readhuffman(buffer)
    dc = []
    while len(dc)<size:
        a = buffer.read(1)
        if a:
            mvalue = searchtree(buffer, movetree)
            mvalue = buffer.read(mvalue)
            if method:
                if mvalue<3:
                    msecond = searchtree(buffer, movetree)
                    msecond = buffer.read(msecond)
                    mvalue = mvalue-1+((msecond-2)<<2)
                else:
                    mvalue = (mvalue-2)<<2
            svalue = searchtree(buffer, sizetree)
            svalue = buffer.read(svalue)
            for i in range(svalue):
                dc.append(dc[-mvalue])
                if len(dc)>=size:
                    break
        else:
            dc.append(buffer.read(8))
    return bytes(dc[:size])
        
def compressVpk(data):
    stat = [[] for x in range(256)]
    for i, b in enumerate(reversed(data)):
        stat[b].append(len(data)-1-i)
    clist = []
    i = 0
    while i<len(data):
        pmax = 0
        psmax = 0
        cmax = 0
        csmax = 0
        smax = 0
        amax = 0
        for ahead in range(2):
            if i+ahead<len(data):
                for j in stat[data[i+ahead]]:
                    if j>=i+ahead:
                        continue
                    if i+ahead-j>=(1<<MAX_MOVE):
                        continue
                    n = 1
                    while n<(1<<MAX_SIZE)-1 and i+ahead+n<len(data) and data[i+ahead+n]==data[j+n]:
                        n += 1
                    s = (n-ahead)*8-8
                    if s>smax:
                        l = 0
                        while (1<<l)<=i+ahead-j:
                            l += 1
                        q = l
                        s -= q
                        if s>smax:
                            l = 0
                            while (1<<l)<=n:
                                l += 1
                            p = l
                            pmax = i+ahead-j
                            psmax = q
                            cmax = n
                            csmax = p
                            smax = s
                            amax = ahead
                    j += 1
        if smax>0:
            for _ in range(amax):
                clist.append((COMMAND_OUTPUT_ONE, data[i]))
                i += 1
            clist.append((COMMAND_OUTPUT_MULTI, pmax, psmax, cmax, csmax))
            i += cmax
        else:
            clist.append((COMMAND_OUTPUT_ONE, data[i]))
            i += 1
    freqmove = [0 for i in range(MAX_MOVE+1)]
    mfmove = 0
    freqsize = [0 for i in range(MAX_SIZE+1)]
    mfsize = 0
    osmove = [i for i in range(MAX_MOVE+1)]
    ossize = [i for i in range(MAX_SIZE+1)]
    for c in clist:
        if c[0]==COMMAND_OUTPUT_MULTI:
            freqmove[c[2]] += 1
            mfmove = max(mfmove, c[2])
            freqsize[c[4]] += 1
            mfsize = max(mfsize, c[4])
    for i in range(mfmove):
        if (freqmove[i+1]<<1) >= freqmove[i] or (freqmove[i]<100 and i>=mfmove-3) or freqmove[i]<25:
            freqmove[i+1] += freqmove[i]
            for j in range(len(osmove)):
                if osmove[j]==i:
                    osmove[j] = i+1
            freqmove[i] = 0
    freqmove = [[f, c] for c, f in enumerate(freqmove) if f>0]
    movetree = buildhuffman(freqmove)
    pmove = dict()
    genpathlist(movetree, pmove)
    for i in range(mfsize):
        if (freqsize[i+1]<<1) >= freqsize[i] or (freqsize[i]<100 and i>=mfsize-3) or freqsize[i]<25:
            freqsize[i+1] += freqsize[i]
            for j in range(len(ossize)):
                if ossize[j]==i:
                    ossize[j] = i+1
            freqsize[i] = 0
    freqsize = [[f, c] for c, f in enumerate(freqsize) if f>0]
    sizetree = buildhuffman(freqsize)
    psize = dict()
    genpathlist(sizetree, psize)
    dc = BitBuffer()
    dc.write(32, 0x76706b30)
    dc.write(32, len(data))
    dc.write(8, 0)
    writehuffman(dc, movetree)
    writehuffman(dc, sizetree)
    for c in clist:
        if c[0]==COMMAND_OUTPUT_MULTI:
            dc.write(1, 1)
            for a in pmove[osmove[c[2]]]:
                dc.write(1, a)
            dc.write(osmove[c[2]], c[1])
            for a in psize[ossize[c[4]]]:
                dc.write(1, a)
            dc.write(ossize[c[4]], c[3])
        else:
            dc.write(1, 0)
            dc.write(8, c[1])
    return dc.getdata()
    
