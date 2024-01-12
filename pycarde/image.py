from PIL import Image

def pal16to24(pal16):
    pal = []
    for i in range(0,len(pal16),2):
        v = pal16[i]|(pal16[i+1]<<8)
        pal.append((v&0x1F)<<3)
        pal.append((v&0x3E0)>>2)
        pal.append((v&0x7C00)>>7)
    return bytes(pal)

def pal24to16(pal24):
    pal = []
    for i in range(0,len(pal24),3):
        v = (pal24[i]>>3)|((pal24[i+1]>>3)<<5)|((pal24[i+2]>>3)<<10)
        pal.append(v&0xFF)
        pal.append(v>>8)
    return bytes(pal)

def setsprite(sprite, xtile, ytile):
    dout = bytearray((xtile*ytile+1)*32)
    if sprite is not None:
        dout[:0x20] = pal24to16(list(sprite.palette.palette)[:0x30])
        n = 0
        for cy in range(ytile):
            for cx in range(xtile):
                for y in range(8):
                    for x in range(8):
                        c = sprite.getpixel((cx*8+x, cy*8+y))&0xF
                        if x&1:
                            dout[n+0x20] |= c<<4
                            n+=1
                        else:
                            dout[n+0x20] |= c
    return bytes(dout)

def getsprite(din, xtile, ytile):
    if len(din)==0:
        return None
    else:
        pal = pal16to24(din[:0x20])
        sprite = Image.new(mode="P", size=(xtile*8,ytile*8))
        n = 0
        for cy in range(ytile):
            for cx in range(xtile):
                for y in range(8):
                    for x in range(8):
                        c = din[n+0x20]
                        if x&1:
                            c >>= 4
                            n+=1
                        else:
                            c &= 0xF
                        sprite.putpixel((cx*8+x, cy*8+y), c)
        sprite.putpalette(pal)
        return sprite
