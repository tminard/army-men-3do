#!/usr/bin/env python3

import argparse
import os.path
import array
import numpy as np

from struct import *
from PIL import Image, ImageOps

class AMMFileExtractor:
    def __init__(self, filename, args):
        self.filename = filename
        self.args = args
        self.prepare()

    def prepare(self):
        if os.path.isfile(self.filename):
            self.extract()
        else:
            print(f"File `{self.filename}` not found!")

    # Extract data as 8-byte grayscale bitmaps for easier use in other engines
    def write_bitmap(self, outputFile, width, height, bmpData):
        img = Image.new('L', (width, height))
        img.putdata(bmpData)

        img.save(outputFile)
        
        return outputFile


    def extract(self):
        print(f"Preparing to extract `{self.filename}`")

        with open(self.filename, mode='rb') as f:
            content = f.read()

        print("--")
        print(f"Total size (bytes):\t{len(content)}")

        if os.path.exists("output"):
            print("Deleting previous output")
            for root, dirs, files in os.walk("output"):
                for file in files:
                    if file.endswith(".bmp"):
                        print(f"\t\tdeleting `{root}/{file}`")
                        os.remove(os.path.join(root, file))
        else:
            os.makedirs("output")


        offset = 0

        # AMM files are pretty easy. After the initial header, each section is followed by a size indicator, then data in a custom format
        # Most of it is sized to the map size of 256*256.


        d = offset

        while d < len(content):
            outputSpriteFile = f"output/sprites/sprite_id{numSpritesExtracted}.png"
            outputShadowFile = f"output/sprites/sprite_id{numSpritesExtracted}_shadow.bmp"

            print(f"\tExtracting sprite {numSpritesExtracted + 1} to {outputSpriteFile}")
            d += (4*4) + (2*2) # skip the header information

            dataSize = unpack_from('<I', content, d)[0]
            d += 4

            d += 4*4 # skip unknown fields

            width, height = unpack_from('<HH', content, d)
            d += 4

            print(f"\t\tData Size:\t{dataSize}\n\t\tWidth:\t{width}px\n\t\tHeight:\t{height}px")

            # we can ignore the line lookup table
            lookupTableLength = height * 2
            d += lookupTableLength

            compressedDataSize = dataSize - 4 - (height * 2) # dataSize includes width, height, and lineOffsets table data. Exclude that
            compressedData = content[d:(d + compressedDataSize)]

            # decompress the bitmap
            bmpData = self.decompress_image(width, height, compressedData)
            self.write_bitmap(outputSpriteFile, width, height, bmpData, paletteData)


            d += compressedDataSize

            # skip the shadow data for now
            shadowDataSize = unpack_from('<I', content, d)[0]
            d += 4

            d += shadowDataSize

            numSpritesExtracted += 1

        print(f"Export complete\n\t\tTotal:\t{numSpritesExtracted}")




print("AMM Army Men 1 AMM Data Extractor")
print("Author:\tadelphospro")

parser = argparse.ArgumentParser(description='Army Men 1 AMM file extractor')
parser.add_argument('amm_file', metavar='AMM_FILE', type=str, help='the AMM file to process')

args = parser.parse_args()

extractor = AMMFileExtractor(args.amm_file, args)
