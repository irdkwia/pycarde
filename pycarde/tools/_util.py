"""
SRC = "e-Reader (USA).gba"
ADDR = 0x85EB930
"""
SRC = "Card e-Reader+ (J).gba"
ADDR = 0x84DBC64

with open(SRC, 'rb') as file:
    data = file.read()


def treeget(data, addr):
    addr -= 0x08000000
    c = int.from_bytes(data[addr:addr+4], 'little')
    if c==0xFFFFFFFF:
        return [treeget(data, int.from_bytes(data[addr+4:addr+8], 'little')), treeget(data, int.from_bytes(data[addr+8:addr+12], 'little'))]
    else:
        if c==0 or c>=0x100:
            print(hex(addr))
        return c

htree = treeget(data, ADDR)

print(htree)
