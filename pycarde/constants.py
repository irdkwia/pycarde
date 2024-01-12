# User constants

## Region Modes
REGION_JO = 0
REGION_US = 1
REGION_JP = 2

## Pokemon Card Types
PKTY_GRASS = 0
PKTY_FIRE = 1
PKTY_WATER = 2
PKTY_LIGHTNING = 3
PKTY_PSYCHIC = 4
PKTY_FIGHTING = 5
PKTY_DARKNESS = 6
PKTY_METAL = 7
PKTY_COLORLESS = 8

## Pokemon Card Data App
PKAPP_NONE = 0
PKAPP_MINIGAME = 1
PKAPP_CARTOON = 2
PKAPP_ABILITY = 3
PKAPP_BRICKBREAKER = 4
PKAPP_PLATFORMER = 5
PKAPP_MUSICBOX = 6

## Pokemon Card Evolution Types
EVOTY_NONE = 0
EVOTY_PRE = 1
EVOTY_1EVO = 2
EVOTY_PRE_1EVO = 3
EVOTY_2EVO = 4
EVOTY_3EVO = 5
EVOTY_4EVO = 6
EVOTY_5EVO = 7
EVOTY_PRE_2EVO = 8
EVOTY_PRE_3EVO = 9
EVOTY_PRE_4EVO = 10
EVOTY_PRE_5EVO = 11
EVOTY_2UNK = 12

## Dotcode Type
### Note: Decimal value is shown in comments for JSON readability purposes
LONG_CODE = 0x810 #2064
SHORT_CODE = 0x510 #1296

## File Type (used for JSON info files)
FTYPE_IMAGE = 0
FTYPE_DATA = 1

# Internal constants

HEAD_LEN = 0x30

APPTYPE_PKMN = 0x0
APPTYPE_S_PKMN = 0x1
APPTYPE_PKMNMINIGAME = 0x2
APPTYPE_S_PKMNMINIGAME = 0x3
APPTYPE_PKMNCARTOON = 0x4
APPTYPE_S_PKMNCARTOON = 0x5
APPTYPE_PKMNABILITY = 0x6
APPTYPE_S_PKMNABILITY = 0x7
APPTYPE_PKMNBB = 0x8
APPTYPE_S_PKMNBB = 0x9
APPTYPE_PKMNPF = 0xA
APPTYPE_S_PKMNPF = 0xB
APPTYPE_PKMNMB = 0xC
APPTYPE_S_PKMNMB = 0xD
APPTYPE_STANDALONE = 0xE
APPTYPE_LINKDATA = 0xF

SIDE_DATA = 1
SIDE_APP = 2

MODE_LONG = 0
MODE_SHORT = 1

NBEVOS = [0, 1, 1, 2, 2, 3, 4, 5, 3, 4, 5, 6, 2]

TABLE_LID = [chr(c) for c in range(ord("A"), ord("Z")+1)]+["-", "_", "%", ".", "#"]
TABLE_MID = ["%02d"%i for i in range(1,100)]+["A%d"%i for i in range(10)]+["B%d"%i for i in range(10)]+["C%d"%i for i in range(9)]
TABLE_RID = "abcdefg#"

H = [0x0D, 0x0C, 0x10, 0x11, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D]

POLY = 0x78

mask = 1
ALPHATO = [0 for x in range(256)]
for i in range(255):
    ALPHATO[i] = mask
    mask<<=1
    if mask >= 256:
        mask ^= POLY ^ 0x1FF

GG = [0 for x in range(0x10)]
GG[0] = ALPHATO[POLY]
for i in range(1, 0x10):
    GG[i] = 1
    for j in reversed(range(i+1)):
        if j==0:
            y = 0
        else:
            y = GG[j-1]
        x = GG[j]
        if x!=0:
            x = ALPHATO.index(x)+POLY+i
            if x>=0xFF:
                x -= 0xFF
            y ^= ALPHATO[x]
        GG[j]=y

GG = [ALPHATO.index(x) for x in GG]

DCHEAD = [
	0xCC, 0xCC, 0x01, 0xCC, #HEADSIZE
	0x00, 0x01, 0xCC, 0xCC,
	0x00, 0x00, 0x10, 0x12,

	0x00, 0x00,

	0x01, 0x00, # TODO

	0x00, 0x00,

	0x10, 0x47, 0xEF,

              0x19, 0x00, 0x00,
        0x00, 0x08, 0x4E, 0x49,
        0x4E, 0x54, 0x45, 0x4E,
        0x44, 0x4F, 0x00, 0x22,
	0x00, 0x09,

                    0x00, 0x00,
	0x00, 0x00, 0x00, 0x00,
	0x00, 0x00,
                    0x00,
                          0x57
]

SHORTHEADER = [
	0x00, 0x02, 0x00, 0x01, 0x40, 0x10, 0x00, 0x1C,
	0x10, 0x6F, 0x40, 0xDA, 0x39, 0x25, 0x8E, 0xE0,
	0x7B, 0xB5, 0x98, 0xB6, 0x5B, 0xCF, 0x7F, 0x72
]
LONGHEADER = [
	0x00, 0x03, 0x00, 0x19, 0x40, 0x10, 0x00, 0x2C,
	0x0E, 0x88, 0xED, 0x82, 0x50, 0x67, 0xFB, 0xD1,
	0x43, 0xEE, 0x03, 0xC6, 0xC6, 0x2B, 0x2C, 0x93
]
