# AXS Extractor

See the local .bt file for specs.

The AXS AM1 file contains a header block of animation tracks, followed by a color palette and sprite compressed image data. Each sprite has an image, followed by an optional shadow.

This script will extract the sprite image portion.

Currently, to work you must manually remove the header block of the .AXS file:

- Open the final in a hex editor
- search for "AXS" sequence
- delete everything from the start of the file until the beginning of the palette data

See one of the included partial.axs files for an example. Eventually I will automate this or decode the header block (I am close, but there are a few unsolved portions)

$	./extractor.py Walk.part.axs

Output will be in `output/sprites`
