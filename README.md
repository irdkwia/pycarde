# pycarde
A Python package for Nintendo e-Reader cards.

## How to install

You need python3 installed: https://www.python.org/

To install a package, run in your command line:
`pip install pycarde`

NOTE: command may vary according to your environment
in case this doesn't work, refer to the official
manuals to run `pip` on your system.

## How to use

### Simple

Pycarde provides some simple samples for the most common use cases at https://github.com/irdkwia/pycarde/blob/main/resources

A list of available constants is defined at https://github.com/irdkwia/pycarde/blob/main/pycarde/constants.py
(note: numerical values must be used in JSON card info files)

### Advanced

Pycarde can also be used to manipulate e-card info as a list of Card objects
containing cards in the same set.
This package provides class types for several card formats detailed [here](#e-reader-card-types)

You can import the `Card` class (`from pycarde.card import Card`), which provides
useful functions to transform your cards: 
- `binaries = Card.makecards(cards, extend=True)`
returns a list of cards in BIN format as bytes objects from a list of Card objects. `extend` specifies if the card list should be extended in case the data need more cards to be fully stored. NOTE: If a card contains too much data, remaining data is inserted at a the beginning of the next one.
- `cards = Card.parsecards(binaries)`
returns a list of card objects from bytes objects representing cards in BIN format.
- `cards = Card.mergecardsdata(cards)`
returns the list of cards will all data merged on the first one, which is useful
for multi dotcode apps.

**IMPORTANT**: These functions modify your original card objects and lists!

If you need to work with RAW cards instead, you can import transform functions:
`from pycarde.raw import rawtobin, bintoraw`

These functions convert a card represented as a bytes object between RAW and BIN format.

Note: to convert all cards in a list, you can use list comprehensions such as `binaries = [bintoraw(b) for b in binaries]` and `binaries = [rawtobin(b) for b in binaries]`.

## e-Reader Card Types

This will list card types as defined in `pycarde.card`.
Constants are defined in [constants.py](https://github.com/irdkwia/pycarde/blob/main/pycarde/constants.py).
Images are all palette indexed, with the first color being transparent.

**IMPORTANT**: Development version! Card properties may change on subsequent releases!

All cards have the following properties: 
- `region`: targeted region (constants)
- `codelen`: dotcode length (constants)

### General Cards

#### RawAppCard - General Purpose Application Cards

A general purpose data cards, a.k.a. all cards that are not TCG cards.

Properties:
- `data`: Data contained in the card
- `appname`: Name of the app for this card set.
- `save`: `True` if the e-reader should prompt to save the app on the e-reader flash, `False` if it can't be saved.
- `support`: Not relevant.
- `unk1`: Not relevant.
- `nes`: `True` if the app is a NES ROM.
- `name`: Name of the current card in the list of cards to be scanned to run its app.
- `link`: `True` if the card contains data that needs to be linked to another app (link cable), `False` if it's a standalone app.

### TCG Cards

All TCG Cards have these shared fields:
- `pkapp`: Type of linked app (constants).
- `special`: If the card has its special flag set (unknown purpose).
- `cname`: Card name.
- `cid`: The TCG card id in "A-99-#" format.
- `hp`: HP of the TCG card.

#### STViewCard - TCG Trainer Supporter Viewer Cards

Dotcodes that contain info for Supporter/Trainer cards.

- `title`: A 192x12 4-colors indexed image representing the card title.
- `cdesc`: Card description.

#### PkViewCard - TCG Pokémon Viewer Cards

Dotcodes that contain info for Pokémon cards.

- `cat`: Pokémon category
- `pdest`: Pokémon description
- `pname`: Pokémon name
- `ctype`: Pokémon card type (constants)
- `cdesc`: Card description.
- `dex`: Pokémon dex #
- `height`: Height of the Pokémon
- `weight`: Weight of the Pokémon
- `sprite`: A 40x40 16-colors indexed image representing the Pokémon.
- `evotype`: Type of evolution (constants), defining the # of evolutions and pre evo.
- `evos`: A list of tuples describing evolutions. The number of entries depend on
the `evotype`, pre evo is first when defined. Each tuple contain the evolution name
and a 4x4 4-colors indexed image representing the evo.


#### PkSTAppCard - TCG Linked Application Cards

Application dotcodes for TCG cards (minigames and cartoons).

Properties:
- `data`: Data contained in the card
- `appname`: Name of the app for this card set.
- `save`: `True` if the e-reader should prompt to save the app on the e-reader flash, `False` if it can't be saved.
- `support`: `True` if the TCG Linked card is a Supporter/Trainer Card.
- `unk1`: Not relevant.
- `nes`: `True` if the app is a NES ROM.

#### PkAbilityCard - TCG Secret Ability Cards

Dotcodes that contain info on a secret ability of the scanned Pokémon card.

**IMPORTANT** Only provides partial support! (This means you should still be able
to modify anything, but unknown fields are reprensented as binary data.)

Properties:
- `support`: `True` if the TCG Linked card is a Supporter/Trainer Card.
- `abilityflags`: A list of 9 integers [0-256[ of unknown data.
- `cdesc`: Card description.
- `sprite`: A 208x16 16-colors indexed image representing the ability title.
- `fieldspecs`: Unknown data that should contain instructions ability usage on TCG battle (the animation that plays when you view it in the e-reader).

#### PkConstructCard - TCG Linked Construction Blocks

Dotcodes that contain info for a Construction Block.

**IMPORTANT** Only provides partial support! (This means you should still be able
to modify anything, but unknown fields are reprensented as binary data.)

Properties:
- `support`: `True` if the TCG Linked card is a Supporter/Trainer Card.
- `layout`: A 32x24 16-colors indexed image representing the Construction Block layout in the e-reader Construction menu.
- `layout`: Construction Block binary data.
- `blocktype`: Block type.
- `unkid`: Unknown ID represented as a numerical value, could also be a set of flags.

## Documentation/Special Thanks

- caitsith2's ereader research and tools - https://caitsith2.com/ereader/index.htm
- gbatek's ereader doc - https://problemkaputt.de/gbatek.htm#gbacartereader
