from pycarde.macro import *

# This will create zip files containing info extracted from raw card data
# If destination does not end with ".zip", this will create folders instead
# This example is similar to get app cards, but applies to standalone
# cards instead (standalone cards are basically all cards that are not
# apps and contain all needed data on a single dotcode; this includes
# raw data cards [like SMA4 power ups], Pokémon Viewer cards and
# construction blocks for platformer, brick breaker and music box)
createcardsinfo([
    ("/path/to/standalone.raw", "standalone.zip"),
    ],
                # Delete next line if you want to create bin card files
                transform=rawtobin,
                )
