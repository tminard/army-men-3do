#!/usr/bin/env python3

import argparse
import os.path
import array

from struct import *

class AXSFileExtractor:
    def __init__(self, filename, args):
        self.filename = filename
        self.args = args
        self.prepare()

    def prepare(self):
        if os.path.isfile(self.filename):
            self.extract()
        else:
            print(f"File `{self.filename}` not found!")

    def extract(self):
        print(f"Preparing to extract `{self.filename}`")

        with open(self.filename, mode='rb') as f:
            content = f.read()

        print("--")
        print(f"Total size (bytes):\t{len(content)}")

        if os.path.exists("output/sprites"):
            print("Deleting previous output")
            for root, dirs, files in os.walk("output/sprites"):
                for file in files:
                    if file.endswith(".bmp"):
                        print(f"\t\tdeleting `{root}/{file}`")
                        os.remove(os.path.join(root, file))
        else:
            os.makedirs("output/sprites")

        if os.path.exists("output/shadows"):
            print("Deleting previous output")
            for root, dirs, files in os.walk("output/shadows"):
                for file in files:
                    if file.endswith(".bmp"):
                        print(f"\t\tdeleting `{root}/{file}`")
                        os.remove(os.path.join(root, file))
        else:
            os.makedirs("output/shadows")

        offset = 0
        paletteData = array.array('I')
        paletteData.frombytes(content[offset:1024])
        offset += 1024


        # Build lookup table
        lookupTable = []

        numSprites = 241
        d = offset


        for id in range(numSprites):
            outputSpriteFile = f"output/sprites/sprite_id{id}.bmp"

            print(f"\tExtracting sprite {id} to {outputSpriteFile}")
            d += (4*4) + (2*2) # skip the header information

            dataSize = unpack_from('<I', content, d)[0]
            d += 4

            d += 4*4 # skip unknown fields

            width, height = unpack_from('<HH', content, d)
            d += 4

            print(f"\t\tData Size:\t{dataSize}\n\t\tWidth:\t{width}px\n\t\tHeight:\t{height}px")

            bmpData = bytearray(0)

            # Compressed images are trimmed - we need to restore the padding
            widthPadded = width + (4 - width % 4) % 4

            # we can ignore the line lookup table
            lookupTableLength = height * 2
            d += lookupTableLength

            compressedDataSize = dataSize - 4 - (height * 2) # dataSize includes width, height, and lineOffsets table data. Exclude that
            compressedData = content[d:(d + compressedDataSize)]

            # decompress the bitmap
            bmpData = bytearray((height * widthPadded))

            bi = 0
            for h in range(height):
                idx = 0
                while (idx < width and bi < len(compressedData)):
                    # RLE - read padding byte
                    t = compressedData[bi]
                    bi += 1

                    for i in range(t):
                        x = h*widthPadded+idx+i
                        bmpData[x] = 0
                    idx += t

                    # RLE - expand color indexes
                    p = compressedData[bi]
                    bi += 1

                    for i in range(p):
                        bmpData[h*widthPadded+idx+i] = compressedData[bi+i]
                    idx += p
                    bi += p

            # Construct the image format
            bmpHeader = pack("=bbIII", 0x42, 0x4D, len(bmpData)+54+1024, 0, 54)
            dibHeader = pack("=IiiHHIIiiII", 40, width, height, 1, 8, 0, 0, 0, 0, 256, 0) 

            # write the file
            with open(outputSpriteFile, mode='wb') as out:
                out.write(bmpHeader)
                out.write(dibHeader)
                out.write(paletteData)
                out.write(bmpData)

            d += compressedDataSize

            # skip the shadow data for now
            shadowDataSize = unpack_from('<I', content, d)[0]
            d += (shadowDataSize + 4)

        print(f"Export complete\n\t\tTotal:\t{numSprites}\n\t\tExtracted:\t{numSprites}")




print("AXS Army Men 1 AXS Animation Extractor")
print("Author:\tadelphospro")

parser = argparse.ArgumentParser(description='Army Men 1 AXS file extractor')
parser.add_argument('axs_file', metavar='AXS_FILE', type=str, help='the AXS file to process')

args = parser.parse_args()

extractor = AXSFileExtractor(args.axs_file, args)
