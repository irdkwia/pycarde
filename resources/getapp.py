from pycarde.macro import *

# Cards in the list must be related to the same multi dotcode set (as described when you scan them with the e-reader)
# and listed in the same order as in the dotcode set (from top to bottom order in the e-reader scan screen)
getcardsinfo([
    ("helloworld/card01.raw", "helloworld/card01"),
    ("helloworld/card02.raw", "helloworld/card02"),
    # You can put more raw files if you need to
    ],
                # Delete next line if you want to create bin card files
                transform=rawtobin,
                # Delete next line if you don't want to merge card data into the first one (useful to get a single app data out of a multi dotcode set)
                merge=True,
                )


# decompress app data (when merge=True)
getdatafromappvpk("helloworld/card01/data.dat", "helloworld/card01/clear.bin")
