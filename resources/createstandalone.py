from pycarde.macro import *

# Create a standalone card

# In this example, this card contains info
# that will be displayed on the e-reader Pokémon Viewer

# Create BIN Files
createcardsinfo([
    ("hamtaro", "hamtaro.bin"),
    ])

# Create RAW Files
createcardsinfo([
    ("hamtaro", "hamtaro.raw"),
    ],
                transform=bintoraw)
