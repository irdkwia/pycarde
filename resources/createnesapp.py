from pycarde.macro import *

# Create a NES app from a NES ROM file
createnesapp(
    "MYROM.nes", # The NES ROM Image
    "MYROM", # Folder 
    REGION_US, # e-Reader Region
    "My NES ROM", # App Name
    save=True, # Delete this if you don't want this app to be saved on the e-Reader
    transform=bintoraw, # Delete this if you want them in the BIN format instead of RAW
)
