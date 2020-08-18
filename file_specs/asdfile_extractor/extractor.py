#!/usr/bin/env python3

import argparse
import numpy as np

class ASDFileExtractor:
    def __init__(self, filename, args):
        self.filename = filename
        self.args = args
        self.prepare()
    
    def prepare(self):
        print(f"Preparing to extract `{self.filename}`")


print("ASD Army Men 1 Audio Data Extractor")
print("adelphospro@gmail.com")

parser = argparse.ArgumentParser(description='Army Men 1 ASD file extractor')
parser.add_argument('asd_file', metavar='ASD_FILE', type=str, help='the ASD file to process')

args = parser.parse_args()

extractor = ASDFileExtractor(args.asd_file, args)
