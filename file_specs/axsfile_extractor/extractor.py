#!/usr/bin/env python3

import argparse
import os.path
import array
import numpy as np

from struct import *
from PIL import Image, ImageOps

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

    def write_bitmap(self, outputFile, width, height, bmpData, paletteData):
        pal = array.array('B')
        for c in paletteData:
            b, g, r, _ = unpack('<BBBB', c.to_bytes(4, byteorder='little', signed=False))
            pal.fromlist([r, g, b])
        
        img = Image.new('P', (width, height))
        img.putpalette(pal)
        img.putdata(bmpData)

         # img = img.convert('RGB')
        # img = ImageOps.flip(img)
        # img = ImageOps.mirror(img)
        img.save(outputFile, transparency=0)
        
        return outputFile

    def build_image(self, outputFile, width, height, bmpData, paletteData):

        pal = array.array('B')
        for c in paletteData:
            b, g, r, _ = unpack('<BBBB', c.to_bytes(4, byteorder='little', signed=False))
            pal.fromlist([r, g, b])
        
        img = Image.new('P', (width, height))
        img.putpalette(pal)
        img.putdata(bmpData)

        img = ImageOps.flip(img)
        
        return img

    def decompress_image(self, width, height, compressedData):
        bmpData = bytearray(height * width)
        bi = 0

        for h in range(height):
            idx = 0
            while (idx < width and bi < len(compressedData)):
                # RLE - read padding byte
                t = compressedData[bi]
                bi += 1

                for i in range(t):
                    x = h*width+idx+i
                    bmpData[x] = 0
                idx += t

                # RLE - expand color indexes
                p = compressedData[bi]
                bi += 1

                for i in range(p):
                    bmpData[h*width+idx+i] = compressedData[bi+i]
                idx += p
                bi += p
        
        return bmpData


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

        numSpritesExtracted = 0
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




print("AXS Army Men 1 AXS Animation Extractor")
print("Author:\tadelphospro")

parser = argparse.ArgumentParser(description='Army Men 1 AXS file extractor')
parser.add_argument('axs_file', metavar='AXS_FILE', type=str, help='the AXS file to process')

args = parser.parse_args()

extractor = AXSFileExtractor(args.axs_file, args)
