#!/usr/bin/env python3

import argparse
import os.path
import array
import numpy as np

from struct import *
from PIL import Image, ImageOps

class DATFileExtractor:
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
        img = ImageOps.flip(img)
        # img = ImageOps.mirror(img)
        img.save(outputFile, transparency=0)
        
        return outputFile

    def extract(self):
        print(f"Preparing to extract `{self.filename}`")

        with open(self.filename, mode='rb') as f:
            checksum = f.read(4)

            content = f.read()

        print("--")
        print(f"Total size (bytes):\t{len(content)}")

        if os.path.exists("output/sprites"):
            print("Deleting previous output")
            for root, dirs, files in os.walk("output/sprites"):
                for file in files:
                    if file.endswith(".png"):
                        print(f"\t\tdeleting `{root}/{file}`")
                        os.remove(os.path.join(root, file))
        else:
            os.makedirs("output/sprites")

        if os.path.exists("output/shadows"):
            print("Deleting previous output")
            for root, dirs, files in os.walk("output/shadows"):
                for file in files:
                    if file.endswith(".png"):
                        print(f"\t\tdeleting `{root}/{file}`")
                        os.remove(os.path.join(root, file))
        else:
            os.makedirs("output/shadows")

        offset = 0
        paletteData = array.array('I')
        paletteData.frombytes(content[offset:1024])
        offset += 1024

        numSprites = unpack_from('I', content, offset)[0]
        offset += 4

        print(f"Num Sprites:\t{numSprites}")

        # Build lookup table
        lookupTable = []

        skippedCount = 0

        for id in range(numSprites):
            encodedCategoryType, dataOffset = unpack_from('II', content, offset)
            offset += 8

            decodedCategory = (encodedCategoryType & 0x7F8000) >> 15
            decodedInstance = (encodedCategoryType & 0x1FE0) >> 5

            outputSpriteFile = f"output/sprites/sprite_c{decodedCategory}_t{decodedInstance}_id{id}.png"

            print(f"\tExtracting sprite {id} to {outputSpriteFile}")

                
            d = dataOffset # skip the first field (repeat of encodedCategory). Remember we dont include the first 4 bytes in our content
            width, height, rleFlag = unpack_from('<3I', content, d)
            d += (8*3)

            print(f"\t\tWidth:\t{width}px\n\t\tHeight:\t{height}px")

            rleMask = 0b1111
            rleEncodingMode = rleFlag & rleMask

            rleMaskSecondary = 0b11110000
            rleModeSec = rleFlag & rleMaskSecondary

            print(f"\t\tRLE Encoding Mode:\t{rleEncodingMode}")

            bmpData = bytearray(0)

            if (rleEncodingMode != 0 or rleModeSec == 16):
                # only certain fields are set when using RLE
                rleWidth, rleHeight = unpack_from('<2H', content, d)
                d += 4

                # Compressed images are trimmed - we need to restore the padding
                widthPadded = rleWidth + (4 - rleWidth % 4) % 4

                # we can ignore the line lookup table
                # For RLE8, each entry is a ushort. For RLE4, each entry is a uint32
                lookupTableLength = height * 2 if (rleEncodingMode == 8 or rleEncodingMode == 0) else height * 4
                d += lookupTableLength

                # decompress the bitmap
                bmpData = bytearray((height * widthPadded))
                for h in range(height - 1, -1, -1):
                    idx = 0
                    while (idx < width):
                        # RLE - read padding byte
                        t = unpack_from('B', content, d)[0]
                        d += 1

                        for i in range(t):
                            x = h*widthPadded+idx+i
                            bmpData[x] = 0
                        idx += t

                        # RLE - expand color indexes
                        p = unpack_from('B', content, d)[0]
                        d += 1

                        for i in range(p):
                            bmpData[h*widthPadded+idx+i] = unpack_from('B', content, d+i)[0]
                        idx += p
                        d += p
            elif rleEncodingMode == 0 and rleModeSec == 32:
                # There is strange padding in this mode I have not figured out
                skippedCount += 1
                print(f"Failed to extract id {id}: Non-RLE image data not understood. Skipping...")
                continue
            elif rleEncodingMode == 0:
                # Uncompressed bitmaps are mostly easy
                widthPadded = width + (4 - width % 4) % 4
                bmpData = content[d:(d+(height*widthPadded))]

                print("\t\t\tNo compression detected. Extracting raw data...")
            else:
                print(f"!! Unrecognized RLE compression format {rleEncodingMode} detected. Expected 0, 4, or 8. Skipping {id}")
                continue

            # Construct the image format
            # bmpHeader = pack("=bbIII", 0x42, 0x4D, len(bmpData)+54+1024, 0, 54)
            # dibHeader = pack("=IiiHHIIiiII", 40, width, height, 1, 8, 0, 0, 0, 0, 256, 0) 
            self.write_bitmap(outputSpriteFile, widthPadded, height, bmpData, paletteData)

            # write the file
            # with open(outputSpriteFile, mode='wb') as out:
            #    out.write(bmpHeader)
            #    out.write(dibHeader)
            #    out.write(paletteData)
            #    out.write(bmpData)

        print(f"Export complete\n\t\tTotal:\t{numSprites}\n\t\tExtracted:\t{numSprites-skippedCount}\n\t\tSkipped:\t{skippedCount}")
        



print("DAT Army Men 1 Object Data Extractor")
print("Author:\tadelphospro")

parser = argparse.ArgumentParser(description='Army Men 1 DAT file extractor')
parser.add_argument('dat_file', metavar='DAT_FILE', type=str, help='the DAT file to process')

args = parser.parse_args()

extractor = DATFileExtractor(args.dat_file, args)
