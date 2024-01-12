from pycarde.macro import *

# Create an app card completely from scratch

# Get the app bin file
with open("apptemplate/card01/clear.bin", 'rb') as infile:
    cdata = compressVpk(infile.read())

# Create a card object
c = RawAppCard(REGION_US, LONG_CODE)
# Add length before the compressed app data
c.data = len(cdata).to_bytes(2, 'little')+cdata
c.appname = "My App"
c.save = True # Delete this if you don't want to save it on e-reader

# extend=True will create as many additional cards as necessary
# to store the whole app data (copying the settings from
# the previous card, which means our defined card here)
lchunks = Card.makecards([c], extend=True)


for i, b in enumerate(lchunks):
    with open("apptemplate/card%02d.bin"%(i+1), 'wb') as file:
        # file.write(bintoraw(b)) # to write raw files instead
        file.write(b) # to write bin files
