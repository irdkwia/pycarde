from pycarde.macro import *

# Create compressed data
createappvpkfromdata(
    "apptemplate/card01/clear.bin",
    "apptemplate/card01/data.dat",
    #gba=True, # Uncomment this if you want to set your app to GBA mode instead of Z80
    )

# Create BIN Files
createcardsinfo([
    ("apptemplate/card01", "apptemplate/card01.bin"),
    ("apptemplate/card02", "apptemplate/card02.bin"),
    ])

# Create RAW Files
createcardsinfo([
    ("apptemplate/card01", "apptemplate/card01.raw"),
    ("apptemplate/card02", "apptemplate/card02.raw"),
    ],
                transform=bintoraw)
