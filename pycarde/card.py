from copy import deepcopy

from pycarde.constants import *
from pycarde.image import *
from pycarde.util import *
from pycarde.compression.pkviewer import decompressLZ19, compressLZ19, decompressBufferedHuffmanRegion, compressBufferedHuffmanRegion

def infercard(cdata):
    apptype = cdata[0x0C]>>4
    if apptype in [APPTYPE_STANDALONE, APPTYPE_LINKDATA]:
        return RawAppCard
    else:
        if cdata[0x03]==SIDE_APP:
            if apptype in [APPTYPE_PKMNBB, APPTYPE_S_PKMNBB, APPTYPE_PKMNPF, APPTYPE_S_PKMNPF, APPTYPE_PKMNMB, APPTYPE_S_PKMNMB]:
                return PkConstructCard
            elif apptype in [APPTYPE_PKMNABILITY, APPTYPE_S_PKMNABILITY]:
                return PkAbilityCard
            else:
                return PkSTAppCard
        else:
            if cdata[0x26]&1:
                return STViewCard
            else:
                return PkViewCard

class Card:
    @staticmethod
    def mergecardsdata(cards):
        if len(cards)==0:
            return cards
        gdata = bytearray(0)
        for c in cards:
            cdata = c.propdata
            if cdata is not None:
                gdata += cdata
        cards[0].propdata = gdata
        for c in cards[1:]:
            c.propdata = None
        return cards
        
    @staticmethod
    def parsecards(chunks):
        cards = []
        consecutivelen = 0
        for cdata in chunks:
            region = cdata[0x0D]&0xF
            codelen = int.from_bytes(cdata[0x06:0x08], 'big')
            cards.append(infercard(cdata)(region, codelen))
            cf = bytearray(12)
            for i, p in enumerate(H):
                cf[i] = cdata[p]
            cards[-1].propcustomflags = cf
            apptype = cdata[0x0C]>>4
            cards[-1].propapptype = apptype
            if cdata[0x03]==SIDE_APP and apptype not in [APPTYPE_PKMNABILITY, APPTYPE_S_PKMNABILITY]:
                if apptype in [APPTYPE_PKMNBB, APPTYPE_S_PKMNBB, APPTYPE_PKMNPF, APPTYPE_S_PKMNPF, APPTYPE_PKMNMB, APPTYPE_S_PKMNMB]:
                    applen = ((int.from_bytes(cf[4:],'little')>>9)&0xFFFF)+0x1A0
                    scdata = cdata[0x30:0x30+applen]
                else:
                    cardno = (cdata[0x26]>>1)&0xF
                    nbcards = ((cdata[0x27]&1)<<3)|(cdata[0x26]>>5)
                    applen = (cdata[0x28]<<7)|(cdata[0x27]>>1)
                    cards[-1].propappname = cdata[0x30:0x30+cards[-1].appnamelen()]
                    if cdata[0x2A]&0x2:
                        cards[-1].propname = None
                        scdata = cdata[0x30+cards[-1].appnamelen():]
                    else:
                        cards[-1].propname = cdata[0x30+cards[-1].appnamelen()+(cards[-1].namelen())*(cardno-1):0x30+cards[-1].appnamelen()+(cards[-1].namelen())*cardno]
                        scdata = cdata[0x30+cards[-1].appnamelen()+(cards[-1].namelen())*nbcards:]
                    if consecutivelen>=applen:
                        scdata = scdata = b''
                    elif consecutivelen+len(scdata)>applen:
                        scdata = scdata[:applen-consecutivelen]
            else:
                scdata = cdata[0x30:]
            cards[-1].propdata = scdata
            consecutivelen += len(scdata)
        return cards
        
    @staticmethod
    def makecards(cards, extend=False):
        if len(cards)==0:
            return []
        if len(set([c.propapptype for c in cards]))>1:
            raise Exception("All cards should have the same app type!")
        if len(set([c.region for c in cards]))>1:
            raise Exception("All cards should have the same region!")
        if len(set([c.propappname for c in cards]))>1:
            raise Exception("All cards should have the same app name!")
        fixeddata = bytearray()
        if cards[0].propappname:
            fixeddata += cards[0].propappname
            fixeddata += bytes(1)
            noneapp = cards[0].propname is None
            for c in cards:
                if (c.propname is None) is not noneapp:
                    raise Exception("Either all cards should have a title or not have one")
                if c.propname is not None:
                    fixeddata += c.propname
                    fixeddata += bytes(1)
        chunks = []
        cdats = [c.propdata for c in cards]
        dtlen = sum([len(c) if c is not None else 0 for c in cdats])
        n = 0
        while n<len(cards):
            c = cards[n]
            cdata = bytearray(DCHEAD)+fixeddata
            remaining = c.codelen-len(fixeddata)
            extending = extend and n+1==len(cards) and len(cdats[n])>remaining
            if n+1<len(cards) and cdats[n+1] is None or extending:
                if extending:
                    cards.append(deepcopy(c))
                    cards[-1].propdata = None
                    cdats.append(None)
                cdats[n+1] = cdats[n][remaining:]
                cdats[n] = cdats[n][:remaining]
            if len(cdats[n])>remaining:
                raise Exception("Card data is too long!")
            cdata += padding(cdats[n], remaining)
            cdata[0x00:0x02] = len(DCHEAD).to_bytes(2, 'big')
            cdata[0x03] = c.propside
            cdata[0x06:0x08] = c.codelen.to_bytes(2, 'big')
            cdata[0x0C] = c.propapptype<<4
            cdata[0x0D] = c.region
            cdata[0x10] = 0
            cdata[0x11] = 0
            cdata[0x26] = 0
            cdata[0x27] = 0
            cdata[0x28] = 0
            cdata[0x29] = 0
            cdata[0x2A] = 0
            cdata[0x2B] = 0
            cdata[0x2C] = 0
            cdata[0x2D] = 0
            if c.propappname:
                cdata[0x27] |= (dtlen&0x7F)<<1
                cdata[0x28] |= dtlen>>7
                if noneapp:
                    cdata[0x2A] |= 2
            for i, f in enumerate(c.propcustomflags):
                cdata[H[i]] |= f
            chunks.append(cdata)
            n += 1
        n = 0
        while n<len(cards):
            c = cards[n]
            cdata = chunks[n]
            if c.propside==SIDE_APP and c.propapptype not in [APPTYPE_PKMNBB, APPTYPE_S_PKMNBB, APPTYPE_PKMNPF, APPTYPE_S_PKMNPF, APPTYPE_PKMNMB, APPTYPE_S_PKMNMB]:
                cdata[0x26] |= ((len(cards)<<5)|((n+1)<<1))&0xFF
                cdata[0x27] |= len(cards)>>3
            chk = 0
            for i in [0x0C,0x0D,0x10,0x11,0x26,0x27,0x28,0x29,0x2A,0x2B,0x2C,0x2D]:
                chk ^= cdata[i]
            cdata[0x2E] = chk

            cdata[0x12] = 0x10
            cdata[0x02] = 1

            chk = 0
            for i, b in enumerate(cdata[0x30:]):
                if i&1:
                    chk += b
                else:
                    chk += (b << 8)
            chk &= 0xFFFF
            chk ^= 0xFFFF
            cdata[0x13:0x15] = chk.to_bytes(2, 'big')

            chk = 0
            for b in cdata[:0x2F]:
                chk += b

            chk &= 0xFF

            xor = 0
            for i, b in enumerate(cdata[0x30:]):
                xor ^= b
                if not (i+1)%0x30:
                    chk += xor
                    xor = 0
            chk &= 0xFF
            chk ^= 0xFF
            cdata[0x2F] = chk
            n += 1
        return chunks

    def __init__(self, region, codelen):
        self.region = region
        self.codelen = codelen
    
    def appnamelen(self):
        return 0
    
    def namelen(self):
        return 0
    
    def getside(self):
        raise Exception("Not implemented!")

    propside = property(getside)
    
    def getapptype(self):
        raise Exception("Not implemented!")
    
    def setapptype(self, value):
        raise Exception("Not implemented!")

    propapptype = property(getapptype, setapptype)
    
    def getappname(self):
        raise Exception("Not implemented!")
    
    def setappname(self, value):
        raise Exception("Not implemented!")
    
    propappname = property(getappname, setappname)
    
    def getdata(self):
        raise Exception("Not implemented!")
    
    def setdata(self, value):
        raise Exception("Not implemented!")
    
    propdata = property(getdata, setdata)
    
    def getname(self):
        raise Exception("Not implemented!")
    
    def setname(self, value):
        raise Exception("Not implemented!")
    
    propname = property(getname, setname)
    
    def getcustomflags(self):
        raise Exception("Not implemented!")
    
    def setcustomflags(self, value):
        raise Exception("Not implemented!")
    
    propcustomflags = property(getcustomflags, setcustomflags)
    

class PkCard(Card):
    def __init__(self, region, codelen):
        super().__init__(region, codelen)
        self.pkapp = PKAPP_NONE
        self.special = False
        self.cname = None
        self.cid = None
        self.hp = 0

    def transcoid(self):
        return TABLE_LID.index(self.cid[0]), TABLE_MID.index(self.cid[2:4]), TABLE_RID.index(self.cid[5])
    
    def gethead(self):
        if self.cid:
            pklid, pkmid, pkrid = self.transcoid()
            return ((pklid<<10)|(pkmid<<3)|pkrid).to_bytes(2, 'big')
        return bytes(2)
    
    def sethead(self, value):
        value = int.from_bytes(value, 'big')
        if value:
            pkrid = value&0x7
            pkmid = (value>>3)&0x7F
            pklid = (value>>10)&0x1F
            self.cid = TABLE_LID[pklid]+"-"+TABLE_MID[pkmid]+"-"+TABLE_RID[pkrid]
        else:
            self.cid = None
    
    def getapptype(self):
        return (self.pkapp<<1)|int(self.special)
    
    def setapptype(self, value):
        self.special = bool(value&1)
        self.pkapp = value>>1

    propapptype = property(getapptype, setapptype)


class RawCard(Card):
    def __init__(self, region, codelen):
        super().__init__(region, codelen)
        self.data = None
        self.appname = ""
        self.save = False
        self.support = False
        self.unk1 = False
        self.nes = False
    
    def getside(self):
        return SIDE_APP

    propside = property(getside)
    
    def getappname(self):
        if self.appname=="":
            return self.appname
        else:
            return padding(convertstringlocale(self.appname, self.region, MODE_LONG if self.appnamelen()==0x21 else MODE_SHORT), self.appnamelen()-1)
    
    def setappname(self, value):
        self.appname = convertbyteslocale(trimpadding(value), self.region, MODE_LONG if self.appnamelen()==0x21 else MODE_SHORT)
    
    propappname = property(getappname, setappname)
    
    def getdata(self):
        return self.data
    
    def setdata(self, value):
        self.data = value
    
    propdata = property(getdata, setdata)

    def getcustomflags(self):
        head = bytearray(2)+self.gethead()+bytes(8)
        head[0x4] = int(self.support)
        head[0x7] = self.unk1<<1
        head[0x8] = int(self.save)|(self.nes<<2)
        return head
    
    def setcustomflags(self, value):
        self.support = bool(value[0x4]&1)
        self.unk1 = bool(value[0x7]&2)
        self.nes = bool(value[0x8]&4)
        self.save = bool(value[0x8]&1)
        self.sethead(value[2:4])
    
    propcustomflags = property(getcustomflags, setcustomflags)


class PkSTAppCard(PkCard, RawCard):
    def appnamelen(self):
        return 0x11
    
    def namelen(self):
        return 0x15
    
    def getname(self):
        if self.name:
            if self.cid:
                av = (int.from_bytes(self.gethead(), 'big')<<4)|((self.hp//10)&0xF)
            else:
                av = 0x80000
            return av.to_bytes(3,'little')+padding(convertstringlocale(self.name, self.region, MODE_SHORT), self.namelen()-4)
        else:
            return None
    
    def setname(self, value):
        if value:
            c = int.from_bytes(value[:3], 'little')
            if c&0x80000:
                self.cid = None
                self.hp = 0
            else:
                self.sethead((c>>4).to_bytes(2, 'big'))
                self.hp = (c&0xF)*10
            self.name = convertbyteslocale(trimpadding(value[3:]), self.region, MODE_SHORT)
        else:
            self.cid = None
            self.hp = 0
            self.name = ""
    
    propname = property(getname, setname)


class STViewCard(PkCard):
    def __init__(self, region, codelen):
        super().__init__(region, codelen)
        self.title = None
        self.cdesc = ""
    
    def getside(self):
        return SIDE_DATA

    propside = property(getside)
    
    def getappname(self):
        return b""
    
    def setappname(self, value):
        raise Exception("Not implemented!")
    
    propappname = property(getappname, setappname)
    
    def getdata(self):
        buffer = bytearray(padding(convertstringlocale(self.cname, self.region, MODE_SHORT), 0x18)+bytes(1))
        d = list(self.title.getdata())
        buffer += bytes([((d[j]&3)<<4)|((d[j+1]&3)<<6)|(d[j+2]&3)|((d[j+3]&3)<<2) for j in range(0, len(d), 4)])
        return bytes(buffer+compressBufferedHuffmanRegion(convertstringlocale(self.cdesc, self.region, MODE_LONG)+bytes(1), self.region))
    
    def setdata(self, value):
        self.cname = convertbyteslocale(trimpadding(value[0x00:0x19]), self.region, MODE_SHORT)
        self.title = Image.frombytes(mode="P", size=(192,12), data=bytes(sum([[(c>>4)&0x3,c>>6,c&0x3,(c>>2)&0x3] for c in value[0x19:0x259]],[])))
        self.title.putpalette(bytes([0,0,0,64,64,64,128,128,128,255,255,255]))
        self.cdesc = convertbyteslocale(decompressBufferedHuffmanRegion(value[0x259:], self.region)[:-1], self.region, MODE_LONG)
    
    propdata = property(getdata, setdata)

    def getcustomflags(self):
        head = bytearray(8)
        head[0] = 1
        return bytearray(2)+self.gethead()+head
    
    def setcustomflags(self, value):
        self.sethead(value[2:4])
    
    propcustomflags = property(getcustomflags, setcustomflags)


class PkViewCard(PkCard):
    def __init__(self, region, codelen):
        super().__init__(region, codelen)
        self.cat = ""
        self.pdesc = ""
        self.pname = ""
        self.ctype = PKTY_COLORLESS
        self.cdesc = ""
        self.dex = 0
        self.height = ""
        self.weight = ""
        self.sprite = None
        self.evotype = EVOTY_NONE
        self.evos = []
    
    def getside(self):
        return SIDE_DATA

    propside = property(getside)
    
    def getheight(self):
        return self.height
    
    def setheight(self, value):
        if len(value)<5:
            value = "?"*(5-len(value)) + value
        else:
            value = value[len(value)-5:]
        self.height = value
        
    propheight = property(getheight, setheight)
    
    def getweight(self):
        return self.weight
    
    def setweight(self, value):
        if len(value)<5:
            value = ("?"*(5-len(value))) + value
        else:
            value = value[len(value)-5:]
        self.weight = value
        
    propweight = property(getweight, setweight)
    
    def getappname(self):
        return b""
    
    def setappname(self, value):
        raise Exception("Not implemented!")
    
    propappname = property(getappname, setappname)
    
    def getdata(self):
        buffer = bytearray(1)
        buffer[0]  = (ord(self.propweight[0])-ord("0"))&0xF
        buffer[0] |= ((ord(self.propweight[1])-ord("0"))&0xF)<<4
        buffer += padding(convertstringlocale(self.cname, self.region, MODE_SHORT), 0xB)+bytes(1)
        buffer += padding(convertstringlocale(self.cat, self.region, MODE_SHORT), 0xB)+bytes(1)
        buffer += padding(convertstringlocale(self.pname, self.region, MODE_SHORT), 0x11)+bytes(1)
        buffer += padding(convertstringlocale(self.pdesc, self.region, MODE_SHORT), 0x6E)+bytes(1)
        dout = compressLZ19(setsprite(self.sprite, 5, 5))
        if len(dout)>=0x1C2:
            raise Exception("Compressed length is too high.")
        buffer += padding(dout, 0x1C2)

        if NBEVOS[self.evotype]!=len(self.evos):
            raise Exception("Number of evos not matching evolution type!")
        if NBEVOS[self.evotype]:
            evodata = bytearray(0x1F)
            evodata[0] = self.evotype
            np = 0
            for i, e in enumerate(self.evos):
                pal = pal24to16(list(e[1].palette.palette)[0x3:0xC])
                merge = None
                for j in range(1, np*6+1, 6):
                    if evodata[j:j+6]==pal:
                        merge = (j-1)//6
                        break
                if merge is None:
                    evodata += bytes([np])
                    evodata[np*6+1:np*6+7] = pal
                    if np>6:
                        raise Exception("Too much palettes for evolutions!")
                    np += 1
                else:
                    evodata += bytes([merge])
                evodata += padding(convertstringlocale(e[0], self.region, MODE_SHORT), 0xB)+bytes(1)
                d = list(e[1].getdata())
                evodata += bytes([((d[j]&3)<<4)|((d[j+1]&3)<<6)|(d[j+2]&3)|((d[j+3]&3)<<2) for j in range(0, len(d), 4)])
            buffer += evodata
        else:
            buffer += bytes(1)
        
        return bytes(buffer+compressBufferedHuffmanRegion(convertstringlocale(self.cdesc, self.region, MODE_LONG)+bytes(1), self.region))
    
    def setdata(self, value):
        self.propweight = chr((value[0]>>4)+ord("0"))+chr((value[0]&0xF)+ord("0"))+self.propweight[2:]
        self.cname = convertbyteslocale(trimpadding(value[0x01:0x0D]), self.region, MODE_SHORT)
        self.pname = convertbyteslocale(trimpadding(value[0x19:0x2B]), self.region, MODE_SHORT)
        self.cat = convertbyteslocale(trimpadding(value[0x0D:0x19]), self.region, MODE_SHORT)
        self.pdesc = convertbyteslocale(trimpadding(value[0x2B:0x9A]), self.region, MODE_SHORT)
        dout = decompressLZ19(value[0x9A:0x25C])
        self.sprite = getsprite(dout, 5, 5)

        self.evotype = value[0x25C]
        self.evos = []
        fieldstart = 0x27B
        for i in range(NBEVOS[self.evotype]):
            pal = bytes(3)+pal16to24(value[0x25D+value[fieldstart]*6:0x25D+value[fieldstart]*6+6])
            im = Image.frombytes(mode="P", size=(16,16), data=bytes(sum([[(c>>4)&0x3,c>>6,c&0x3,(c>>2)&0x3] for c in value[fieldstart+0xD:fieldstart+0x4D]],[])))
            im.putpalette(pal)
            n = convertbyteslocale(trimpadding(value[fieldstart+0x1:fieldstart+0xD]), self.region, MODE_SHORT)
            self.evos.append((n, im))
            fieldstart += 0x4D
        if fieldstart==0x27B:
            fieldstart = 0x25D
        self.cdesc = convertbyteslocale(decompressBufferedHuffmanRegion(value[fieldstart:], self.region)[:-1], self.region, MODE_LONG)
    
    propdata = property(getdata, setdata)

    def getcustomflags(self):
        head = bytearray(8)
        head[0:4] = (((self.hp//10)<<9)|(self.ctype<<13)|(self.dex<<17)).to_bytes(4, 'little')
        head[4]  = (ord(self.propheight[4])-ord("0"))&0xF
        head[4] |= ((ord(self.propheight[3])-ord("0"))&0xF)<<4
        head[5]  = (ord(self.propheight[2])-ord("0"))&0xF
        head[5] |= ((ord(self.propheight[1])-ord("0"))&0xF)<<4
        head[6]  = (ord(self.propheight[0])-ord("0"))&0xF
        head[6] |= ((ord(self.propweight[4])-ord("0"))&0xF)<<4
        head[7]  = (ord(self.propweight[3])-ord("0"))&0xF
        head[7] |= ((ord(self.propweight[2])-ord("0"))&0xF)<<4
        return bytearray(2)+self.gethead()+head
    
    def setcustomflags(self, value):
        self.sethead(value[2:4])
        head = int.from_bytes(value[4:8], 'little')
        self.hp = ((head>>9)&0xF)*10
        self.ctype = (head>>13)&0xF
        self.dex = head>>17
        self.propheight = chr((value[10]&0xF)+ord("0"))+chr((value[9]>>4)+ord("0"))+chr((value[9]&0xF)+ord("0"))+chr((value[8]>>4)+ord("0"))+chr((value[8]&0xF)+ord("0"))
        self.propweight = self.propweight[:2]+chr((value[11]>>4)+ord("0"))+chr((value[11]&0xF)+ord("0"))+chr((value[10]>>4)+ord("0"))
    
    propcustomflags = property(getcustomflags, setcustomflags)


class PkAbilityCard(PkCard):
    def __init__(self, region, codelen):
        super().__init__(region, codelen)
        self.support = False
        self.abilityflags = [0 for _ in range(9)]
        self.cdesc = ""
        self.sprite = None
        self.fieldspecs = None
    
    def getside(self):
        return SIDE_APP

    propside = property(getside)
    
    def getappname(self):
        return b""
    
    def setappname(self, value):
        raise Exception("Not implemented!")
    
    propappname = property(getappname, setappname)
    
    def getdata(self):
        buffer = bytearray(self.abilityflags)
        buffer += padding(convertstringlocale(self.cdesc, self.region, MODE_SHORT), 0xD0)+bytes(1)
        buffer += setsprite(self.sprite, 26, 2)
        buffer += self.fieldspecs
        return compressLZ19(buffer)
    
    def setdata(self, value):
        buffer = decompressLZ19(value)
        self.abilityflags = list(buffer[:0x9])
        self.cdesc = convertbyteslocale(trimpadding(buffer[0x9:0xDA]), self.region, MODE_SHORT)
        self.sprite = getsprite(buffer[0xDA:0x77A], 26, 2)
        self.fieldspecs = buffer[0x77A:]
    
    propdata = property(getdata, setdata)

    def getcustomflags(self):
        return bytearray(2)+self.gethead()+bytes([int(self.support)])+bytes(7)
    
    def setcustomflags(self, value):
        self.support = bool(value[0x4]&1)
        self.sethead(value[2:4])
    
    propcustomflags = property(getcustomflags, setcustomflags)


class PkConstructCard(PkCard):
    def __init__(self, region, codelen):
        super().__init__(region, codelen)
        self.support = False
        self.layout = None
        self.data = None
        self.blocktype = 0
        self.unkid = 0
    
    def getside(self):
        return SIDE_APP

    propside = property(getside)
    
    def getappname(self):
        return b""
    
    def setappname(self, value):
        raise Exception("Not implemented!")
    
    propappname = property(getappname, setappname)
    
    def getdata(self):
        return setsprite(self.layout, 4, 3)+self.data
    
    def setdata(self, value):
        self.layout = getsprite(value[:0x1A0], 4, 3)
        self.data = value[0x1A0:]
    
    propdata = property(getdata, setdata)

    def getcustomflags(self):
        c = bytearray(((self.unkid<<25)+(len(self.data)<<9)).to_bytes(8, 'little'))
        c[0] = int(self.support|((self.blocktype&0x7F)<<1))
        c[1] |= self.blocktype>>7
        return bytearray(2)+self.gethead()+c
    
    def setcustomflags(self, value):
        self.sethead(value[2:4])
        self.support = bool(value[4]&1)
        self.blocktype = ((value[4]>>1))|((value[5]&1)<<7)
        self.unkid = int.from_bytes(value[4:],'little')>>25
    
    propcustomflags = property(getcustomflags, setcustomflags)


class RawAppCard(RawCard):
    def __init__(self, region, codelen):
        super().__init__(region, codelen)
        self.name = None
        self.link = False
    
    def appnamelen(self):
        return 0x21
    
    def namelen(self):
        return 0x21
    
    def gethead(self):
        return bytes(2)
    
    def sethead(self, value):
        pass
    
    def getapptype(self):
        return 0xE|int(self.link)
    
    def setapptype(self, value):
        self.link = bool(value&1)

    propapptype = property(getapptype, setapptype)

    def getname(self):
        if self.name:
            return padding(convertstringlocale(self.name, self.region, MODE_LONG), self.namelen()-1)
        else:
            return None
    
    def setname(self, value):
        if value:
            self.name = convertbyteslocale(trimpadding(value), self.region, MODE_LONG)
        else:
            self.name = None
    
    propname = property(getname, setname)
