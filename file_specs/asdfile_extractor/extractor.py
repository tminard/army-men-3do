#!/usr/bin/env python3

import argparse
import os.path

from struct import *

class ASDFileExtractor:
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
            magicId = f.read(4)

            if magicId != bytearray(b'\x56\x30\x2E\x30'):
                print(f"`{self.filename}` does not appear to be a valid Army Men 1 ASD file. Aborting.")
                return

            content = f.read()

            print("--")
            print(f"Total size (bytes):\t{len(content)}")

            if os.path.exists("output"):
                print("Deleting previous output")
                for root, dirs, files in os.walk("output"):
                    for file in files:
                        if file.endswith(".wav"):
                            print(f"\t\tdeleting `{file}`")
                            os.remove(os.path.join(root, file))
            else:
                os.makedirs("output")


            numAudioClips = unpack_from('i', content, 0)[0]
            print(f"Num Clips:\t{numAudioClips}")

            offset = 2060
            for id in range(numAudioClips):
                outputFile = f"output/audio_{id}.wav"
                print(f"\tExtracting clip {id} to {outputFile}")

                imgHeader = unpack_from('4siHHiiHH', content, offset)
                imgData = unpack_from('4si', content, offset+24)
                dataSize = imgData[1]

                offsetEnd = offset + 24+8+dataSize

                # write the file
                rawImageContent = content[offset:offsetEnd]
                riffHeader = pack("4si4s", bytearray("RIFF", "utf-8"), len(rawImageContent)+4, bytearray("WAVE", "utf-8"))
                with open(outputFile, mode='wb') as out:
                    out.write(riffHeader)
                    out.write(rawImageContent)

                offset = offsetEnd 

        



print("ASD Army Men 1 Audio Data Extractor")
print("Author:\tadelphospro")

parser = argparse.ArgumentParser(description='Army Men 1 ASD file extractor')
parser.add_argument('asd_file', metavar='ASD_FILE', type=str, help='the ASD file to process')

args = parser.parse_args()

extractor = ASDFileExtractor(args.asd_file, args)
