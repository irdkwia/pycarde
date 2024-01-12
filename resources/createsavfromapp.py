from pycarde.macro import *

# Create e-Reader save file from raw dotcode files
createcardssaveraw(
    [
    "helloworld/card01.raw",
    "helloworld/card02.raw",
    ],
    "save_raw.sav",
    #base="/path/to/base/save", # Uncomment this if you want to use an existing save as a base
    transform=rawtobin, # Delete this if you use BIN files instead of RAW
)

# Create e-Reader save file from raw dotcode files
createcardssave(
    [
    "apptemplate/card01",
    "apptemplate/card02",
    ],
    "save_info.sav",
    #base="/path/to/base/save", # Uncomment this if you want to use an existing save as a base
)
