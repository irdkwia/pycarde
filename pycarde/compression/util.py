SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

class BitBuffer:
    def __init__(self, data=bytes(1)):
        self.data = bytearray(data)
        self.byte = 0
        self.bit = 7

    def tell(self):
        return (self.byte<<3)|(7-self.bit)
        
    def seek(self, off, seektype=SEEK_CUR):
        if seektype==SEEK_SET:
            self.byte = 0
            self.bit = 7
        elif seektype==SEEK_END:
            self.byte = len(self.data)
            self.bit = 7

        self.byte += off >> 3
        if off<0:
            off = -((-off)&0x7)
            while off<0:
                off += 1
                self.bit += 1
                if self.bit==8:
                    self.bit = 0
                    self.byte -= 1
        else:
            off &= 0x7
            while off>0:
                off -= 1
                self.bit -= 1
                if self.bit==-1:
                    self.bit = 7
                    self.byte += 1
        
    def read(self, bits):
        n = 0
        for _ in range(bits):
            n <<= 1
            n |= (self.data[self.byte]>>self.bit)&1
            self.bit -= 1
            if self.bit==-1:
                self.bit = 7
                self.byte += 1
        return n
    
    def write(self, bits, value):
        if value>=(1<<bits):
            print("Warning!",value,"does not fit",bits,"bits data!")
        for i in reversed(range(bits)):
            self.data[self.byte] &= ~(1<<self.bit)
            self.data[self.byte] |= (((value>>i)&1)<<self.bit)
            self.bit -= 1
            if self.bit==-1:
                self.bit = 7
                self.byte += 1
                if self.byte==len(self.data):
                    self.data += bytes(1)
    
    def getdata(self):
        return bytes(self.data)

def genpathlist(htree, plist, p=[]):
    if not isinstance(htree, list):
        plist[htree] = p
    else:
        if len(htree)==0:
            return
        genpathlist(htree[0], plist, p+[0])
        genpathlist(htree[1], plist, p+[1])

def searchtree(buffer, htree):
    if isinstance(htree, list):
        a = buffer.read(1)
        return searchtree(buffer, htree[a])
    else:
        return htree
    
def buildhuffman(freqlist):
    if len(freqlist)==0:
        return []
    while len(freqlist)>1:
        freqlist.sort(key=lambda i:i[0])
        x = freqlist[0]
        y = freqlist[1]
        del freqlist[0]
        del freqlist[0]
        freqlist.append((x[0]+y[0], [x[1], y[1]]))
    return freqlist[0][1]
    
def readhuffman(buffer):
    htree = []
    while True:
        a = buffer.read(1)
        if a:
            if len(htree)>=2:
                htree[-2] = [htree[-2], htree[-1]]
                del htree[-1]
            else:
                if len(htree)==0:
                    return None
                else:
                    return htree[0]
        else:
            htree.append(buffer.read(8))

def writehuffman(buffer, htree, end=True):
    if isinstance(htree, list):
        if len(htree)==0:
            buffer.write(1, 1)
        else:
            writehuffman(buffer, htree[0], False)
            writehuffman(buffer, htree[1], False)
            buffer.write(1, 1)
    else:
        buffer.write(1, 0)
        buffer.write(8, htree)
    if end:
        buffer.write(1, 1)
