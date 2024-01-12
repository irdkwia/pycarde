from pycarde.macro import *

# Get the NES ROM file from a card set
# Cards must be in scan order
getnesapp(
    ["/path/to/cards/card00.raw",
     "/path/to/cards/card01.raw",
     "/path/to/cards/card02.raw",
     "/path/to/cards/card03.raw",
     "/path/to/cards/card04.raw",
     "/path/to/cards/card05.raw",
     "/path/to/cards/card06.raw",
     ],
    "EXTRACTED.nes", # ROM output path
    ines=False, # Delete this if you want the ROM in the iNES format
    transform=rawtobin, # Delete this if you have them in the BIN format instead of RAW
)
